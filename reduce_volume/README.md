# OpenTelemetry log reduction

the show-cases shows how to reduce the signals logs and traces to a percentage of the received volume
**NOTE** metric as signal isn't supported by the probabilistic_sampler processor

# Requirements

* ghcr.io access as the telemetrygen image is retrieved from there.

## deployment process

The deployment injects:

* one OTC deployment listening on otlp/grpc protocol port 4317
* manual inject telemetrygen 

```
oc create -k reduce_volume
```

simulate signal injection. The TelemetryGen pod injects 8 logs and 8 traces.

```
oc -n otcreducevolume create -f reduce_volume/telemetrygen.yml
```

Since the OTC is configured for 25% it will reduce all signals passing by 75%.
That means sending 8 logs and 8 traces, only 2 of each are expected to be printed to the OTC console log output.

```
oc -n otcreducevolume logs deploy/otc-collector | grep info | grep  '"otelcol.signal"' | wc -l
```

Expected output
```
4
```

# clean up

```
oc delete -f reduce_volume/telemetrygen.yml
oc delete -k reduce_volume
```
