import time
import os
import sys
from ansible.plugins.callback import CallbackBase

# --- Configuration ---
BASE_URL = "https://user-collector.apps.chester.at:443"
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "ansible-playbook")


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "opentelemetry"

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.tracer = None
        self.meter = None
        self.playbook_span = None
        self.current_task_span = None
        self.playbook_context = None
        self.task_context = None
        self.playbook_name = "unknown_playbook"
        self.host_task_start = {}

        try:
            self._setup_opentelemetry()
        except Exception as e:
            sys.stderr.write(f"\n[OTEL FATAL ERROR] Failed to initialize: {e}\n")

    def _setup_opentelemetry(self):
        from opentelemetry import trace, metrics
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

        # enable these exporters if you need to go http
        # from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        # from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter,
        )

        resource = Resource.create({"service.name": SERVICE_NAME})

        # 1. Tracing
        tp = TracerProvider(resource=resource)
        tp.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{BASE_URL}/v1/traces"))
        )
        try:
            trace.set_tracer_provider(tp)
        except:
            pass
        self.tracer = trace.get_tracer(__name__)

        # 2. Metrics (5s interval)
        exporter = OTLPMetricExporter(endpoint=f"{BASE_URL}/v1/metrics")
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
        mp = MeterProvider(resource=resource, metric_readers=[reader])
        try:
            metrics.set_meter_provider(mp)
        except:
            pass
        self.meter = metrics.get_meter(__name__)

        self.metric_task_duration = self.meter.create_histogram(
            name="ansible.task.duration",
            description="Duration of a task per host",
            unit="s",
        )

    def v2_playbook_on_start(self, playbook):
        if not self.tracer:
            return
        from opentelemetry import trace

        self.playbook_name = os.path.basename(playbook._file_name)
        self.playbook_span = self.tracer.start_span(f"Playbook: {self.playbook_name}")
        self.playbook_span.set_attribute("job", self.playbook_name)
        self.playbook_span.set_attribute("ansible.playbook", self.playbook_name)

        # Capture context to link all children to this TraceID
        self.playbook_context = trace.set_span_in_context(self.playbook_span)

    def v2_playbook_on_task_start(self, task, is_conditional):
        if not self.tracer:
            return
        from opentelemetry import trace

        if self.current_task_span:
            self.current_task_span.end()

        self.current_task_span = self.tracer.start_span(
            f"Task: {task.get_name()}", context=self.playbook_context
        )
        loop_data = getattr(task, "loop", None)
        try:
            loop_data = list(map(str, loop_data))
        except Exception:
            loop_data = []
        when_data = getattr(task, "when", None)
        try:
            when_data = list(map(str, when_data))
        except Exception:
            when_data = []
        self.current_task_span.set_attribute("job", self.playbook_name)
        self.current_task_span.set_attribute("action", task.action)
        for k in task.args:
            self.current_task_span.set_attribute("task.args", str(task.args[k]))
        self.current_task_span.set_attribute("when", task.when)
        self.current_task_span.set_attribute("items", loop_data)
        self.task_context = trace.set_span_in_context(self.current_task_span)

    def v2_runner_on_start(self, host, task):
        # CRITICAL: We must record the start time to calculate duration
        self.host_task_start[f"{host.name}_{task._uuid}"] = time.time()

    def _record_result(self, result, status):
        if not self.tracer:
            return
        host_name = result._host.name
        task = result._task
        key = f"{host_name}_{task._uuid}"

        start_time = self.host_task_start.pop(key, None)
        if start_time:
            duration = time.time() - start_time

            # Record Metric
            self.metric_task_duration.record(
                duration,
                {
                    "job": SERVICE_NAME,
                    "playbook_name": self.playbook_name,
                    "host.name": host_name,
                    "task.name": task.get_name(),
                    "status": status,
                },
            )

            # Start Host Span (linked to task)
            from opentelemetry import trace

            # Use start_time from host start for accurate waterfall
            start_nano = int(start_time * 1e9)
            with self.tracer.start_as_current_span(
                f"Host: {host_name}", context=self.task_context, start_time=start_nano
            ) as s:
                s.set_attributes(
                    {
                        "job": SERVICE_NAME,
                        "playbook_name": self.playbook_name,
                        "host.name": host_name,
                        "ansible.status": status,
                    }
                )

    def v2_runner_on_ok(self, result):
        self._record_result(result, "ok")

    def v2_runner_on_failed(self, result, **kwargs):
        self._record_result(result, "failed")

    def v2_runner_on_skipped(self, result):
        self._record_result(result, "skipped")

    def v2_playbook_on_stats(self, stats):
        if self.current_task_span:
            self.current_task_span.end()
        if self.playbook_span:
            self.playbook_span.end()

        from opentelemetry import trace, metrics

        try:
            # Force export of remaining data before Ansible exits
            metrics.get_meter_provider().shutdown()
            trace.get_tracer_provider().shutdown()
        except Exception as e:
            sys.stderr.write(f"OTel shutdown error: {e}\n")
        sys.stderr.write(
            f"TraceID: {format(trace.get_current_span(self.playbook_context).get_span_context().trace_id, '032x')}\n"
        )
