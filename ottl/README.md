# OpenTelemetry Transformation Language (OTTL)

the show-cases for OTTL will give you some idea on how to enhance your signals with various business logic values.
For simplicity we are going to inject Node Name and Cluster Name going with the semantic convention names of:

* k8s.node.name
* k8s.cluster.name

Other very good use-cases are enforced tenancy which will be handled on a different example in this repo.

# Requirements

* ghcr.io access as the telemetrygen image is retrieved from there.

## deployment process

The deployment injects:

* an OTC deployment listening on otlp/grpc protocol port 4317
* manual inject the telemetrygen pod once the OTC pod is ready

```
oc create -k ottl
```

once the deployment is ready execute the telemetrygen pod

```
oc -n otcottl create -f ottl/telemetrygen.yml
```

The pod should show up as `completed` after a short moment as it starts three containers.
Each sending one signal (log, metric, trace) without specifying any node or cluster name.

Still the OTC debug exporter shall show them for each signal as we enforce the attribute to all signals.

## Log attributes transformed

```
2026-01-26T18:21:35.957Z	info	Logs	{"resource": {"service.instance.id": "1c48735d-5741-4dd8-ad27-1b0729327724", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "logs", "resource logs": 1, "log records": 1}
2026-01-26T18:21:35.957Z	info	ResourceLog #0
Resource SchemaURL: https://opentelemetry.io/schemas/1.38.0
Resource attributes:
     -> service.name: Str(telemetrygen)
ScopeLogs #0
ScopeLogs SchemaURL: 
InstrumentationScope  
LogRecord #0
ObservedTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 2026-01-26 18:21:35.946499266 +0000 UTC
SeverityText: Info
SeverityNumber: Info(9)
Body: Str(Hello World)
Attributes:
     -> app: Str(server)
     -> k8s.node.name: Str(server11)
     -> k8s.cluster.name: Str(testing)
Trace ID: 
Span ID: 
Flags: 0
	{"resource": {"service.instance.id": "1c48735d-5741-4dd8-ad27-1b0729327724", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "logs"}
``` 

## Metric attribute transformed

```
2026-01-26T18:21:36.081Z	info	Metrics	{"resource": {"service.instance.id": "1c48735d-5741-4dd8-ad27-1b0729327724", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "metrics", "resource metrics": 1, "metrics": 1, "data points": 1}
2026-01-26T18:21:36.081Z	info	ResourceMetrics #0
Resource SchemaURL: https://opentelemetry.io/schemas/1.38.0
Resource attributes:
     -> service.name: Str(telemetrygen)
ScopeMetrics #0
ScopeMetrics SchemaURL: 
InstrumentationScope  
Metric #0
Descriptor:
     -> Name: gen
     -> Description: 
     -> Unit: 
     -> DataType: Gauge
NumberDataPoints #0
Data point attributes:
     -> k8s.node.name: Str(server11)
     -> k8s.cluster.name: Str(testing)
StartTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 2026-01-26 18:21:36.076634094 +0000 UTC
Value: 0
	{"resource": {"service.instance.id": "1c48735d-5741-4dd8-ad27-1b0729327724", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "metrics"}
```

## trace attributes transformed 

```
2026-01-26T18:21:37.213Z	info	Traces	{"resource": {"service.instance.id": "1c48735d-5741-4dd8-ad27-1b0729327724", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "traces", "resource spans": 1, "spans": 2}
2026-01-26T18:21:37.213Z	info	ResourceSpans #0
Resource SchemaURL: https://opentelemetry.io/schemas/1.38.0
Resource attributes:
     -> service.name: Str(telemetrygen)
ScopeSpans #0
ScopeSpans SchemaURL: 
InstrumentationScope telemetrygen 
Span #0
    Trace ID       : 4bc0cdd4c851b42cd1b47c8d27bfcb7d
    Parent ID      : 6b19ceab21c835d7
    ID             : e2bcff0c0276feb4
    Name           : okey-dokey-0
    Kind           : Server
    Start time     : 2026-01-26 18:21:36.208399409 +0000 UTC
    End time       : 2026-01-26 18:21:36.208522409 +0000 UTC
    Status code    : Unset
    Status message : 
Attributes:
     -> network.peer.address: Str(1.2.3.4)
     -> peer.service: Str(telemetrygen-client)
     -> k8s.node.name: Str(server11)
     -> k8s.cluster.name: Str(testing)
Span #1
    Trace ID       : 4bc0cdd4c851b42cd1b47c8d27bfcb7d
    Parent ID      : 
    ID             : 6b19ceab21c835d7
    Name           : lets-go
    Kind           : Client
    Start time     : 2026-01-26 18:21:36.208399409 +0000 UTC
    End time       : 2026-01-26 18:21:36.208522409 +0000 UTC
    Status code    : Unset
    Status message : 
Attributes:
     -> network.peer.address: Str(1.2.3.4)
     -> peer.service: Str(telemetrygen-server)
     -> k8s.node.name: Str(server11)
     -> k8s.cluster.name: Str(testing)
	{"resource": {"service.instance.id": "1c48735d-5741-4dd8-ad27-1b0729327724", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "traces"}
```

# clean up

```
oc delete -f ottl/telemetrygen.yml
oc delete -k ottl
```
