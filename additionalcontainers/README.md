# OpenTelemetry additional containers

the show-cases shows how add containers for debugging purpose for example

## deployment process

The deployment injects:

* one OTC deployment listening on otlphttp protocol port 4318
* runs an additional container (OpenShift ImageStream cli)

```
oc create -k additionalcontainers
```

assume we want to debug connectivity towards any exporter 

```
oc -n otcaddcontainers exec -ti deploy/otc-collector -c debug -- curl -I https://www.google.com 
```

Expected output 
```
HTTP/2 200 
...
date: Mon, 09 Feb 2026 17:32:42 GMT
server: gws
x-xss-protection: 0
x-frame-options: SAMEORIGIN
expires: Mon, 09 Feb 2026 17:32:42 GMT
...
```

extending this for connectivity test on otlphttp **NOTE** you cannot use curl for grpc (protobuf)

```
oc -n otcaddcontainers exec -ti deploy/otc-collector -c debug \
-- curl http://127.0.0.1:4318/v1/logs -X POST -d '{}' -H 'Content-Type: application/json'
```

Expected output
``` 
{"partialSuccess":{}}
```

**NOTE** additionally you can change which Container is access by default when using the UI or cli with

```
spec:
  podAnnotations:
    kubectl.kubernetes.io/default-container: "otc-container" # or "debug"
```

in the OTC CR.

# clean up

```
oc delete -k additionalcontainers
```
