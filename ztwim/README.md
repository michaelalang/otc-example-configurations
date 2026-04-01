# OpenTelemetry Collector using ZeroTrust Workload Identity Manager

## Requirementes

* access to Registry ghcr.io (telemetrygen)
* ZeroTrustWorkload Identity Manager setup and configured

## deploy the OpenTelemetryCollector

* the repository will deploy
    * opentelemetry client-collector
    * opentelemetry server-collector
    * ClusterSPIFFEID template for subjectAltName handling
    * Config Map with your `TRUST_DOMAIN` for attribute enhancement

* execute following command to deploy the resources 

```
oc create -k ztwim
```

## verification

* run the telemetrygen 

```
oc -n ztwim-otc create -f telemetrygen.yml
```

* check the `server` logs to see the trace including the `Spiffe` id 

```
oc -n ztwim-otc logs deploy/server-collector
```

* Example output

```
Resource SchemaURL: https://opentelemetry.io/schemas/1.38.0
Resource attributes:
     -> service.name: Str(telemetrygen)
ScopeLogs #0
ScopeLogs SchemaURL: 
InstrumentationScope  
LogRecord #0
ObservedTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 2026-04-01 07:44:49.1218137 +0000 UTC
SeverityText: Info
SeverityNumber: Info(9)
Body: Str(Hello World)
Attributes:
     -> app: Str(server)
     -> peer.spiffe_id: Str(spiffe://example.com/ns/ztwim-otc/sa/client-collector)
Trace ID: 
Span ID: 
Flags: 0
	{"resource": {"service.instance.id": "b6651655-57dd-45af-bdd6-98d03d51d600", "service.name": "otelcol", "service.version": "0.144.0"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "logs"}
```

```
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
     -> peer.spiffe_id: Str(spiffe://example.com/ns/ztwim-otc/sa/client-collector)
StartTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 2026-04-01 07:44:49.335197965 +0000 UTC
Value: 0
	{"resource": {"service.instance.id": "b6651655-57dd-45af-bdd6-98d03d51d600", "service.name": "otelcol", "service.version": "0.144.0"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "metrics"}
```

```
Resource SchemaURL: https://opentelemetry.io/schemas/1.38.0
Resource attributes:
     -> service.name: Str(telemetrygen)
     -> tenant: Str(tenantA)
ScopeSpans #0
ScopeSpans SchemaURL: 
InstrumentationScope telemetrygen 
Span #0
    Trace ID       : 9945c1a6f93ba53bc64e6486483a13a1
    Parent ID      : a8b14f38dbc1524f
    ID             : afcc005785b21beb
    Name           : okey-dokey-0
    Kind           : Server
    Start time     : 2026-04-01 07:34:53.38686022 +0000 UTC
    End time       : 2026-04-01 07:34:53.38698322 +0000 UTC
    Status code    : Unset
    Status message : 
    DroppedAttributesCount: 0
    DroppedEventsCount: 0
    DroppedLinksCount: 0
Attributes:
     -> network.peer.address: Str(1.2.3.4)
     -> peer.service: Str(telemetrygen-client)
     -> peer.spiffe_id: Str(spiffe://example.com/ns/ztwim-otc/sa/client-collector)
Span #1
    Trace ID       : 9945c1a6f93ba53bc64e6486483a13a1
    Parent ID      : 
    ID             : a8b14f38dbc1524f
    Name           : lets-go
    Kind           : Client
    Start time     : 2026-04-01 07:34:53.38686022 +0000 UTC
    End time       : 2026-04-01 07:34:53.38698322 +0000 UTC
    Status code    : Unset
    Status message : 
    DroppedAttributesCount: 0
    DroppedEventsCount: 0
    DroppedLinksCount: 0
Attributes:
     -> network.peer.address: Str(1.2.3.4)
     -> peer.service: Str(telemetrygen-server)
     -> peer.spiffe_id: Str(spiffe://example.com/ns/ztwim-otc/sa/client-collector)
	{"resource": {"service.instance.id": "0dcdf779-475b-424b-a21e-2660c7a72b4e", "service.name": "otelcol", "service.version": "0.144.0"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "traces"}
```

## the extra mile

using ZeroTrustIdentityManager to authenticate telemetryGen to OpenTelemetryCollector through bearer token 

* remote the telemetrygen instance by executing

```
oc -n ztwim-otc delete -f ztwim-otc/telemetrygen.yml
```

* rollout the client-collector by executing following command

```
oc -n ztwim-otc rollout restart deploy/client-collector
```

* create or re-create a secret called svid-token. This is mandatory as the telemetrygen cannot take env from reading a file.

```
oc -n ztwim-otc create secret generic svid-token \
  --from-literal=token="$(oc -n ztwim-otc exec -ti deploy/client-collector -- cat /opt/client-certs/svid_token)" 
```

* if you need to re-create when the token expires for example

```
oc -n ztwim-otc create secret generic svid-token \
  --from-literal=token="$(oc -n ztwim-otc exec -ti deploy/client-collector -- cat /opt/client-certs/svid_token)" \
  --dry-run=client -o yaml | oc -n ztwim-otc replace -f-
```

* inject the `telemetrygen-protected` pod which sends three signals (log,metric,trace) but only trace is configured to use a bearer authentication

```
oc -n ztwim-otc create -f ztwim-otc/telemetrygen-protected.yml
```

* check the `server-collector` logs to see the trace arriving

```
oc -n ztwim-otc logs deploy/server-collector
```

* Example output

```
Resource SchemaURL: https://opentelemetry.io/schemas/1.38.0
Resource attributes:
     -> service.name: Str(telemetrygen)
ScopeSpans #0
ScopeSpans SchemaURL: 
InstrumentationScope telemetrygen 
Span #0
    Trace ID       : 2b4256bd32dc5f3c7e7b9bf52446567d
    Parent ID      : 84ceffbb396e7fe9
    ID             : 1ae71df3dc82c66c
    Name           : okey-dokey-0
    Kind           : Server
    Start time     : 2026-04-01 11:58:56.22429783 +0000 UTC
    End time       : 2026-04-01 11:58:56.22442083 +0000 UTC
    Status code    : Unset
    Status message : 
    DroppedAttributesCount: 0
    DroppedEventsCount: 0
    DroppedLinksCount: 0
Attributes:
     -> network.peer.address: Str(1.2.3.4)
     -> peer.service: Str(telemetrygen-client)
     -> peer.spiffe_id: Str(spiffe://example.com/ns/ztwim-otc/sa/default,spiffe://example.com/ns/ztwim-otc/sa/client-collector)
Span #1
    Trace ID       : 2b4256bd32dc5f3c7e7b9bf52446567d
    Parent ID      : 
    ID             : 84ceffbb396e7fe9
    Name           : lets-go
    Kind           : Client
    Start time     : 2026-04-01 11:58:56.22429783 +0000 UTC
    End time       : 2026-04-01 11:58:56.22442083 +0000 UTC
    Status code    : Unset
    Status message : 
    DroppedAttributesCount: 0
    DroppedEventsCount: 0
    DroppedLinksCount: 0
Attributes:
     -> network.peer.address: Str(1.2.3.4)
     -> peer.service: Str(telemetrygen-server)
     -> peer.spiffe_id: Str(spiffe://example.com/ns/ztwim-otc/sa/default,spiffe://example.com/ns/ztwim-otc/sa/client-collector)
	{"resource": {"service.instance.id": "1d773198-907e-400e-881b-7bcbef3747bb", "service.name": "otelcol", "service.version": "0.144.0"}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "traces"}
```
