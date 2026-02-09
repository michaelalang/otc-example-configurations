# Log Deduplication pre-evaluation (opentelemetry-collector-contrib)

the use-case is evaluating deduplication which is currently only featured in opentelemetry-collector-contrib

# Requirements

* docker.io access as the deployment uses the upstream image opentelemetry-collector-contrib
* ghcr.io access to utilize the telemetrygen image

## deployment process

The deployment injects:

* a deployment
    * with an initContainer running the telemetryGen in an infinite loop
    * sleep pod to avoid the deployment getting reconciled
* the OTC is injected as sidecar

```
oc create -k logdedup
```

## Verify 

The telemetrygen injects logs until we stop the pod. Still the OTC will show only a deduped version of it.

```
2026-01-25T15:29:10.547Z info ResourceLog #0
Resource SchemaURL:
Resource attributes:
-> service.name: Str(telemetrygen)
ScopeLogs #0
ScopeLogs SchemaURL:
InstrumentationScope
LogRecord #0
ObservedTimestamp: 2026-01-25 15:29:10.489058313 +0000 UTC
Timestamp: 2026-01-25 15:29:10.54744723 +0000 UTC
SeverityText: ERROR
SeverityNumber: Error(17)
Body: Str(Connection refused: failed to connect to database at 10.0.0.5:5432)
Attributes:
-> app: Str(server)
-> log_count: Int(100) # << the logs batched within the configured timeframe (1s in our example) 
-> first_observed_timestamp: Str(2026-01-25T15:29:10Z)
-> last_observed_timestamp: Str(2026-01-25T15:29:10Z)
Trace ID:
Span ID:
Flags: 0
```

# clean up

```
oc delete -k logdedup
```
