# OpenTelemetry routing show-case

the show-cases provides routing capabilities. Based upon the opentelemetry attribute `tenant` we are going to address different exporters.

# Requirements

* ghcr.io access as the telemetrygen image is retrieved from there.

## deployment process

The deployment injects:

* one otc-collector which handles the routing
* three otc-collectors called dest1,dest2,dest3 simulating different export targets

```
oc create -k routing
```

## create signals for tenant `tenant1` 

create the telemetrygen instance for tenant1 by executing following command

```
oc -n otcrouting create routing/telemetrygen1.yml
```

check the dest1 pod logs for signals 

```
oc -n otcrouting logs deploy/dest1-collector 
```

You should see for each Signal (log,metric,trace) a debug output accordingly.
Check the other collectors to not show any signals.

```
oc -n otcrouting logs deploy/dest2-collector
oc -n otcrouting logs deploy/dest3-collector
```

If you want for easier comparison of signals, you can restart the dest1-collector now.

```
oc -n otcrouting rollout restart deploy/dest1-collector
```

## create signals for tenant `tenant2`

create the telemetrygen instance for tenant2 by executing following command

```
oc -n otcrouting create routing/telemetrygen2.yml
```

check the dest2 pod logs for signals

```
oc -n otcrouting logs deploy/dest2-collector
```

You should see for each Signal (log,metric,trace) a debug output accordingly.
Check the other collectors to not show any signals.

```
oc -n otcrouting logs deploy/dest1-collector
oc -n otcrouting logs deploy/dest3-collector
```

If you want for easier comparison of signals, you can restart the dest2-collector now.

```
oc -n otcrouting rollout restart deploy/dest2-collector
```


## create signals for tenant `tenant3`

create the telemetrygen instance for tenant3 by executing following command

```
oc -n otcrouting create routing/telemetrygen3.yml
```

check the dest1 pod logs for signals

```
oc -n otcrouting logs deploy/dest3-collector
```

You should see for each Signal (log,metric,trace) a debug output accordingly.
Check the other collectors to not show any signals.

```
oc -n otcrouting logs deploy/dest1-collector
oc -n otcrouting logs deploy/dest2-collector
```

If you want for easier comparison of signals, you can restart the dest3-collector now.

```
oc -n otcrouting rollout restart deploy/dest3-collector
```

# clean up

```
oc -n otcrouting delete -f routing/telemetrygen1.yml
oc -n otcrouting delete -f routing/telemetrygen2.yml
oc -n otcrouting delete -f routing/telemetrygen3.yml
oc delete -k routing
```
