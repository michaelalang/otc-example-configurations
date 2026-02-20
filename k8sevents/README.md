# Receiving and transforming Kubernetes Events to Logs

the use-case show-cases fetching OpenShift Kubernetes events and transforming them into logs


# Requirements

* Administrative privileges to deploy ClusterRole and ClusterRoleBinding

## deployment process

Injecting the ClusterRole and ClusterRoleBinding for the serviceAccount otlp which is used to run the OpenTelemetry Collector.

```
oc create -k k8sevents
```

## verification of events

The deployment only exports the emitted events as logs to the OTC container stdout.

```
oc -n otck8sevents logs -f deploy/k8sevents-collector
```

Example output

```
ScopeLogs #0
ScopeLogs SchemaURL:
InstrumentationScope github.com/open-telemetry/opentelemetry-collector-contrib/receiver/k8seventsreceiver 0.144.0
LogRecord #0
ObservedTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 2026-02-20 12:43:32 +0000 UTC
SeverityText: Normal
SeverityNumber: Info(9)
Body: Str(Updated open-cluster-management-agent-addon/managed-serviceaccount-addon-agent)
Attributes:
-> k8s.event.reason: Str(Deployment Updated)
-> k8s.event.action: Str()
-> k8s.event.start_time: Str(2026-02-16 13:18:50 +0000 UTC)
-> k8s.event.name: Str(klusterlet-hcp1-work-agent.1894bc9bd2420b0e)
-> k8s.event.uid: Str(b0946a53-daf7-401b-8eff-4b558a665091)
-> k8s.namespace.name: Str(klusterlet-hcp1)
-> k8s.event.count: Int(1148)
-> openshift_cluster_name: Str(example)
-> openshift_cluster_id: Str(3c122224-747c-4802-b42d-60ebbb405b6b)
-> openshift_log_type: Str(events)
-> log_type: Str(events)
Trace ID:
Span ID:
Flags: 0
{"resource": {"service.instance.id": "0beadc97-6f26-40a2-9211-5dc4a10db7ee", "service.name": "otelcol", "service.version": "0.144.0"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "logs"
```

# clean up

```
oc delete -k k8sevents
```
