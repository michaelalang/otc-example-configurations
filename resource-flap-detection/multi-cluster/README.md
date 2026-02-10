# Multi-Cluster Resource flapping detection

**NOTE** this scenario is perfectly 10000% unsupported by Red Hat !!!!

The use-case show-cases how we could detect resource flapping like when two CI/CD engines race on one Custom Resource (CR).
Each of the cluster sends **direcetly** to the Prometheus endpoint. If desired, a centralized OTC can take the OTLP streams from all clusters and be used as the single point to forward to the prometheus stack.

The deployment will require to have **no** `openshift-logging` being present/setup. As mentioned this is an explicit decision as we don't want ClusterLogForwarder (CLF) and OpenTelemetryCollector (OTC) race for the logs.

Included in this deployment
* `openshift-logging` namespace creation
* a serviceAccount that will receive privileges you don't want to run in production
* a Security Context Constraint (SCC) that grants access to your Cluster gems (the logs of everything)
* ClusterRole and RoleBinding towards the SCC 
* the OpenTelemetryCollector (OTC)

The goal is to read the audit logs from the kube-apiserver and openshift-apiserver report the resource and user associated to the token of the API request in metrics. Those metrics can than be used to graph and understand flapping of resources.

**NOTE** since this is a multi-cluster scenario the following cluster structures are created

* acm == AdvancedCluster Management Cluster running Hosted Control Planes (separate configuration)
* central
* east

The Clusters hcp1 and hcp2 are collected and forwarded by the HCP hosting Cluster (so no hcp1 and hcp2 deployments)

# Requirements

* Cluster Administrative rights

**NOTE** since we will be using the Red Hat build of OpenTelemetry image, we need to utilize prometheus OTLP endpoint and need to set following parameters to your Prometheus instance

```
--enable-feature=otlp-deltatocumulative
--web.enable-otlp-receiver
```

## deployment process

Since we need the permissions in place before the OpenTelemetryCollector should start and we are not using a wave based CI/CD system we first create those resources

Cluster names are in the `otc.yml` under the `env` section if you want to adjust.

```
oc --context acm create -k resource-flap-detection/multi-cluster/acm
oc --context central create -k resource-flap-detection/multi-cluster/central
oc --context east create -k resource-flap-detection/multi-cluster/east
```

That will deploy a daemonset on the HCP Hosting Cluster (acm) as hosted control plane pods are on `any` node in the cluster and we need to pick them up.
The none HCP Cluster can run a daemonset only on the ControlPlane nodes where the audit logs will be found.

A Grafana Dashboard to visualize the logs-to-metrics is located in `resource-flap-detection/multi-cluster/multi-cluster-dashboard.json`.

![Visualizing multi-cluster flapping resources](resource-flap-detection/multi-cluster/multi-cluster-dashboard.png)

