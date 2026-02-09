# OpenTelemetry deltactocumulativeprocessor workaround

the Red Hat Build of OpenTelemetry image does not provide the `deltactocumulativeprocessor`. That means, creating metrics from logs does not work properly without a workaround when trying to use prometheusremotewrite exporter.

# Requirements

* ghcr.io access as the telemetrygen image is retrieved from there.

## deployment process

The deployment injects:

* one otc-collector which handles log to metric with the `count` connector
* one telemetrygen pod

```
oc create -k deltactocumulativeprocessor
```

create a log which shall be counted and used as metric in prometheusremotewrite

```
oc -n otcworkaround create deltactocumulativeprocessor/telemetrygen.yml
```

after some time the logs should be represented as metrics 

```
oc -n otcworkaround logs deploy/otc-collector | grep -B16 -A 11 AggregationTemporality
```

Example output
```
--
Resource SchemaURL: 
Resource attributes:
     -> service.name: Str(otel-self-scrape)
     -> service.instance.id: Str(127.0.0.1:8889)
     -> server.port: Str(8889)
     -> url.scheme: Str(http)
ScopeMetrics #0
ScopeMetrics SchemaURL: 
InstrumentationScope github.com/open-telemetry/opentelemetry-collector-contrib/connector/countconnector 
Metric #0
Descriptor:
     -> Name: log_record_count_total
     -> Description: The number of log records observed.
     -> Unit: 
     -> DataType: Sum
     -> IsMonotonic: true
     -> AggregationTemporality: Cumulative
NumberDataPoints #0
Data point attributes:
     -> exported_job: Str(telemetrygen)
     -> must_have_1: Str(1)
     -> must_have_2: Str(2)
     -> must_have_3: Str(3)
     -> must_have_4: Str(4)
     -> service_name: Str(telemetrygen)
StartTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 2026-02-02 14:18:18.101 +0000 UTC
ScopeMetrics #1
```

as you can see the `AggregationTemporality: Cumulative` means, it cannot be used for remote writing to a prometheus instance.

# Workaround to the problem

To mitigate that issue youo can switch to the `otlphttp` exporter and enable `otlp` on the Prometheus side 

Ensure two options are set on your Prometheus arguments list

```
--enable-feature=otlp-deltatocumulative
--web.enable-otlp-receiver
```

That gives the endpoint `/api/v1/otlp` access and a configuration of

```
      otlphttp/prometheusremotewrite:
        endpoint: 'https://prometheus.apps.example.com/api/v1/otlp'
        retry_on_failure:
          enabled: true
          initial_interval: 60s
          max_elapsed_time: 600s
          max_interval: 120s
        timeout: 120s
```

will accept deltacumulative values for your metrics.

# Alternative workaround if you cannot enable OTLP on prometheus

To workaround this issue until the `deltactocumulativeprocessor` is supported in the image we can send it to a local prometheus instance and use remotewrite from that instance instead.

The local Prometheus instance is already configured in the OTC you would need to setup an external Prometheus instance with remote write capability and extend the Pipeline as follows

```
        metrics/loopback:
          exporters:
          - prometheusremotewrite
          processors:
          - batch
          receivers:
          - prometheus/loopback
```

Without the external Prometheus instance we can still check that the metrics are populated to the prometheus instance in the OTC.

Port-forward the prometheus instance of the OTC

```
oc -n otcworkaround port-forward service/otc-collector 8889:8889 &
```

than execute a curl command against your local port `8889`

```
curl localhost:8889/metrics
```

Example output:

```
Handling connection for 8889
# HELP log_record_count_total The number of log records observed.
# TYPE log_record_count_total counter
log_record_count_total{job="telemetrygen",must_have_1="1",must_have_2="2",must_have_3="3",must_have_4="4",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/connector/countconnector",otel_scope_schema_url="",otel_scope_version="",service_name="telemetrygen"} 1
```

# clean up

```
oc -n otcworkaround delete -f deltactocumulativeprocessor/telemetrygen.yml
oc delete -k deltactocumulativeprocessor
```
