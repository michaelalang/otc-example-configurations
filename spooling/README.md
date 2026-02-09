# OpenTelemetry Spooling for outages

the show-cases provides spooling capabilities in case of an outage of an exporter.
**NOTE** the deployment uses only an `emptyDir` which is not suite able for production.

If you are looking for more production grade storage evaluate:

* volumeClaimTemplates
* volumes
    * persistentVolumeClaim
    * csi
    * and a ton of others (`oc explain opentelemetrycollector.spec.volumes`)

# Requirements

* ghcr.io access as the telemetrygen image is retrieved from there.

## deployment process

The deployment injects:

* two OTC deployment listening on otlp/grpc protocol port 4317
* manual inject telemetrygen 

```
oc create -k spooling
```

once both OTC deployment are ready patch the otcexternal collector to zero replicas 

```
oc -n otcspooling patch opentelemetrycollector otcexternal --type merge -p '{"spec": {"replicas": 0}}'
```

then simulate signal receiving on the spooling instance 

```
oc -n otcspooling create -f spooling/telemetrygen.yml
```

the otc-spooler-collector will show errors because of the exporter not being available

```
oc -n otcspooling logs deploy/otc-spooler-collector -f
```

Example connection issue log

```
2026-01-26T19:17:03.835Z	warn	grpc@v1.76.0/clientconn.go:1407	[core] [Channel #1 SubChannel #2] grpc: addrConn.createTransport failed to connect to {Addr: "otcexternal-collector.otcspooling.svc:4317", ServerName: "otcexternal-collector.otcspooling.svc:4317", }. Err: connection error: desc = "transport: Error while dialing: dial tcp 172.31.75.55:4317: connect: connection refused"	{"resource": {"service.instance.id": "8ef01097-38b6-4d91-a878-52207c60176f", "service.name": "otelcol", "service.version": "0.140.1"}, "grpc_log": true}
```

bring back the otcexternal collector again

```
oc -n otcspooling patch opentelemetrycollector otcexternal --type merge -p '{"spec": {"replicas": 1}}'
```

watch and wait the otcexternal-collector deployment for the signals to appear

```
oc -n otcspooling logs deploy/otcexternal-collector -f
```

# clean up

```
oc delete -f spooling/telemetrygen.yml
oc delete -k spooling
```
