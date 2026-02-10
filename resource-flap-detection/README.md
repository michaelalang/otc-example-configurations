# Resource flapping detection

**NOTE** this scenario is perfectly 10000% unsupported by Red Hat !!!!

the use-case show-cases how we could detect resource flapping like when two CI/CD engines race on one Custom Resource (CR).
The deployment will require to have **no** `openshift-logging` being present/setup. As mentioned this is an explicit decision as we don't want ClusterLogForwarder (CLF) and OpenTelemetryCollector (OTC) race for the logs.

Included in this deployment
* `openshift-logging` namespace creation
* a serviceAccount that will receive privileges you don't want to run in production
* a Security Context Constraint (SCC) that grants access to your Cluster gems (the logs of everything)
* ClusterRole and RoleBinding towards the SCC 
* the OpenTelemetryCollector (OTC)

The goal is to read the audit logs from the kube-apiserver and openshift-apiserver report the resource and user associated to the token of the API request in metrics. Those metrics can than be used to graph and understand flapping of resources.

# Requirements

* Cluster Administrative rights

## deployment process

Since we need the permissions in place before the OpenTelemetryCollector should start and we are not using a wave based CI/CD system we first create those resources

```
oc create -k resource-flap-detection
```

Second we are going to deploy the OpenTelemetryCollector
**NOTE** ensure to point the `prometheusremotewriter` exporter to a valid Prometheus instance accepting remote writes on `/api/v1/otlp`.

```
oc create -f resource-flap-detection/otc.yml
```

# clean up

```
oc delete -f resource-flap-detection/otc.yml
oc delete -k resource-flap-detection
```
