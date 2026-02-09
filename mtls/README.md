# TLS and mTLS configuration for OTC

the use-case show-cases two deployments of OTC:

* otc-server
* otc-client

Where `otc-server` is configured to use mTLS for communication. 
`otc-client` sends data reading from `/tmp/debug` file. Alternative you can use the debug container on the `otc-client` to curl the `otc-server`.

# Requirements

* Cert-Manager 
* Reflector

## deployment process

The deployment injects:

* two certificates in namespace `cert-manager-operator` which create two secrets
    * otc-server-certificate
    * otc-client-certificate
* reflector copies them to the `otccerts` namespace through the secret annotation 
* the certifcates last for 60min but are renewed every 5 minutes (renewBefore 55m)

```
oc create -k mtls
```

## verification mTLS/Certificate rotation

### mTLS verification

using the curl in the `debug` container of `otc-client`.

* successful mTLS verification showing the certificate dates

```
oc -n otccerts exec -ti $(oc -n otccerts get pods -l app.kubernetes.io/instance=otccerts.otel-client -o name) -c debug -- curl https://otel-server-collector.otccerts.svc:4317/v1/logs -v -d '{}' -H 'Content-Type: application/json' --cacert /etc/certs/client/ca.crt --cert /etc/certs/client/tls.crt --key /etc/certs/client/tls.key | grep date:
```

* expected output
```
*  start date: Jan 19 13:45:39 2026 GMT
*  expire date: Jan 19 14:45:39 2026 GMT
```

* successful mTLS enforcement 

```
oc -n otccerts exec -ti $(oc -n otccerts get pods -l app.kubernetes.io/instance=otccerts.otel-client -o name) -c debug -- curl https://otel-server-collector.otccerts.svc:4317/v1/logs -k
```

* expected output

```
curl: (56) OpenSSL SSL_read: error:0A00045C:SSL routines::tlsv13 alert certificate required, errno 0
command terminated with exit code 56
```

# clean up

```
oc delete -k mtls
```
