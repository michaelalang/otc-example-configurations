# Receiving and transforming Kubernetes Objects to Logs

the use-case show-cases fetching OpenShift Kubernetes Objects and transforming them into logs or metrics


# Requirements

* Administrative privileges to deploy ClusterRole and ClusterRoleBinding

**NOTE** the ClusterRole and ClusterRoleBinding equal the k8sevents Role and Binding accordingly since they both can emit the same objects.

## deployment process

Injecting the ClusterRole and ClusterRoleBinding for the serviceAccount otlp which is used to run the OpenTelemetry Collector.

```
oc create -k k8objects
```

## verification of events

The deployment only exports the emitted objects as logs to the OTC container stdout.

```
oc -n otck8sobjects logs -f deploy/k8sobjects-collector
```

Example output (not the output is with flatten enabled)

```
LogRecord #5
ObservedTimestamp: 2026-02-20 13:15:43.678429561 +0000 UTC
Timestamp: 1970-01-01 00:00:00 +0000 UTC
SeverityText:
SeverityNumber: Unspecified(0)
Body: Map({"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{"k8s.ovn.org/pod-networks":"{\"default\":{\"ip_addresses\":[\"10.143.4.206/23\"],\"mac_address\":\"0a:58:0a:8f:04:ce\",\"gateway_ips\":[\"10.143.4.1\"],\"routes\":[{\"dest\":\"10.140.0.0/14\",\"nextHop\":\"10.143.4.1\"},{\"dest\":\"172.30.0.0/16\",\"nextHop\":\"10.143.4.1\"},{\"dest\":\"169.254.0.5/32\",\"nextHop\":\"10.143.4.1\"},{\"dest\":\"100.64.0.0/16\",\"nextHop\":\"10.143.4.1\"}],\"ip_address\":\"10.143.4.206/23\",\"gateway_ip\":\"10.143.4.1\",\"role\":\"primary\"}}","k8s.v1.cni.cncf.io/network-status":"[{\n \"name\": \"ovn-kubernetes\",\n \"interface\": \"eth0\",\n \"ips\": [\n \"10.143.4.206\"\n ],\n \"mac\": \"0a:58:0a:8f:04:ce\",\n \"default\": true,\n \"dns\": {}\n}]","openshift.io/scc":"restricted-v2","seccomp.security.alpha.kubernetes.io/pod":"runtime/default","security.openshift.io/validated-scc-subject-type":"user","tempo.grafana.com/cert-hash-tempo-tempo-observe-compactor-mtls":"2bf9576e0eb9e27...
Attributes:
-> k8s.resource.name: Str(pods)
-> status.podIP: Str(10.143.4.206)
-> status.containerStatuses: Slice([{"containerID":"cri-o://b981e795c45c541a7348a6ab3b2865af2b3dd49dd0c1078035bf5bc0e9c12157","image":"registry.redhat.io/rhosdt/tempo-jaeger-query-rhel8@sha256:5c756f9904c0a278ff71c54757f4c20b6dd42319b14ad165d51ed1b599e3e10e","imageID":"registry.redhat.io/rhosdt/tempo-jaeger-query-rhel8@sha256:5c756f9904c0a278ff71c54757f4c20b6dd42319b14ad165d51ed1b599e3e10e","lastState":{},"name":"jaeger-query","ready":true,"resources":{},"restartCount":2,"started":true,"state":{"running":{"startedAt":"2026-02-16T13:02:14Z"}},"user":{"linux":{"gid":0,"supplementalGroups":[0,1001120000],"uid":1001120000}},"volumeMounts":[{"mountPath":"/tmp","name":"tempo-tmp-storage-query"},{"mountPath":"/var/run/ca","name":"tempo-tempo-observe-ca-bundle"},{"mountPath":"/var/run/tls/server","name":"tempo-tempo-observe-query-frontend-mtls"},{"mountPath":"/var/run/secrets/kubernetes.io/serviceaccount","name":"kube-api-access-dnnwb","readOnly":true,"recursiveReadOnly":"Disabled"}]},{"containerID":"cri-o://...
-> status.qosClass: Str(BestEffort)
-> status.hostIP: Str(192.168.192.209)
-> status.podIPs: Slice([{"ip":"10.143.4.206"}])
-> status.startTime: Str(2026-02-12T16:41:12Z)
-> status.phase: Str(Running)
-> status.conditions: Slice([{"lastProbeTime":null,"lastTransitionTime":"2026-02-16T13:02:14Z","status":"True","type":"PodReadyToStartContainers"},{"lastProbeTime":null,"lastTransitionTime":"2026-02-12T16:41:12Z","status":"True","type":"Initialized"},{"lastProbeTime":null,"lastTransitionTime":"2026-02-16T13:02:36Z","status":"True","type":"Ready"},{"lastProbeTime":null,"lastTransitionTime":"2026-02-16T13:02:36Z","status":"True","type":"ContainersReady"},{"lastProbeTime":null,"lastTransitionTime":"2026-02-12T16:41:12Z","status":"True","type":"PodScheduled"}])
-> status.hostIPs: Slice([{"ip":"192.168.192.209"}])
-> kind: Str(Pod)
```

# clean up

```
oc delete -k k8sobjects
```
