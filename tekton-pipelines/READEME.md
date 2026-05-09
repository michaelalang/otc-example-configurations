# Taming the Churn: Preserving OpenShift Pipelines Logs with OpenTelemetry

If your team has fully embraced CI/CD on OpenShift, you already know the power of Red Hat OpenShift Pipelines. Built on the open-source Tekton framework, it allows developers to create cloud-native, execution-ready pipelines that run in isolated, ephemeral containers.
But there’s a catch. When you scale up, you inevitably run into the reality of high churn build clusters.

In high churn environments, thousands of pods spin up, execute a task, and terminate within minutes. While this is great for resource efficiency, it is an absolute nightmare for observability and compliance. Ephemeral pods mean ephemeral logs. If a build fails—or worse, if an auditor asks for the pipeline results from six months ago—those logs and event traces are long gone. OpenShift Pipelines added Tekton Results to mitigate the situation within OpenShift Pipelines.

Here is how you can use the Red Hat Build of OpenTelemetry to capture, enhance, and route your pipeline logs for both local troubleshooting and long-term, compliance-grade remote storage keeping OpenShift Pipeline Results effective and powerful.


## The Solution: Red Hat Build of OpenTelemetry

The Red Hat Build of OpenTelemetry provides a vendor-neutral, standardized way to collect, process, and export telemetry data (metrics, traces, and logs). By deploying the OpenTelemetry (OTel) Collector in your OpenShift cluster, you can intercept pipeline telemetry before the pods disappear.

### Enhancing Logs with Pipeline Events
Simply capturing standard output (stdout) from a build pod isn't enough. To make logs useful for long-term auditing, they need context. The OTel Collector can be configured to enrich raw logs with specific OpenShift and Tekton events.
Here is how the enrichment process works in a pipeline context:

* Kubernetes Attributes Processor: The OTel Collector uses this processor to automatically append pod metadata (namespace, pod name, node name) to the log stream.
* Tekton Event Integration: By capturing Kubernetes events tied to PipelineRun and TaskRun state changes, you can weave lifecycle events (e.g., Started, Failed, Succeeded) directly into the log stream.
* Custom Annotations: Developers can add annotations to their Pipeline tasks. The OTel Collector can extract these annotations (like the application version, target environment, or security scan results) and attach them as key-value pairs to the exported log payload.

### Architecting the Storage Strategy: Local vs. Remote

One of the biggest strengths of the OpenTelemetry Collector is its ability to fork telemetry data to multiple backends simultaneously using Exporters. This allows you to satisfy both the engineering team's need for fast, local troubleshooting and the security team's need for long-term compliance.

1. Local Storage for Fast Troubleshooting
Developers need immediate access to pipeline results to fix broken builds.

* The Workflow: The OTel Collector exports the enriched logs to your local OpenShift Logging stack	.
* The Benefit: Developers can seamlessly query logs in the OpenShift Web Console. Because the logs are enriched with Tekton metadata, a developer can simply search for tekton_pipelinerun="release-build-123" to see all logs and events associated with that specific execution, regardless of how many pods were spun up and destroyed.
* Retention: Short-term (e.g., 7 to 14 days) to save on local expensive storage.

2. Remote Storage for Compliance and Auditing

To meet regulatory requirements, the exact same data stream must be preserved securely off-cluster.

* The Workflow: Concurrently, the OTel Collector forwards the enriched logs and pipeline results to a remote, enterprise-grade storage backend. This could be a SIEM (like Splunk or Elastic), or highly durable object storage (like AWS S3 or Azure Blob Storage).
* The Benefit: Logs are shipped to immutable, Write-Once-Read-Many (WORM) storage. Because the OTel Collector already enriched the data with OpenShift pipeline events, auditors can easily reconstruct the exact sequence of events that led to a specific software release.
* Retention: Long-term (e.g., 1 to 7+ years) dictated by your organizational compliance policies.

# Implementing the components to satisfy the requirements

**NOTE** Red Hat does not support the OpenTelemetryCollector contrib image which is community supported. 

* Ensure to adjust the paramters for
    * namespace: the POC focuses on the `openshift-logging` namespace 
    * serviceAccounts: the POC uses two accounts, one for the OTC one for Splunk.
    * LokiStack: LokiStack is assumed to serve OpenShift UI
    * Splunk-HEC: the POC uses a free-to-use but not production ready deployment.

* Execute following command to deploy the resources (POC Loki+Splunk-Hec)

```
oc create -k .
oc apply -f tekton-config.yml --server-side=true
```

* If you want to evaluate the OpenShift Pipeline Results with S3 Storage execute the following
**NOTE** the LOGGING_PLUGIN_CA_CERT and corresponding volumes are only for the plugins not the S3 integration. Use the cluster trust-bundle accordingly.

```
oc apply -f tekton-s3-secret.yml 
oc apply -f tekton-config-s3.yml --server-side=true
```

