# OpenTelemetry Collector Target Allocator 

The OpenTelemetry Target Allocator (TA) is a separate component that manages the discovery and distribution of Prometheus scrape targets to a pool of OpenTelemetry Collectors.

# deployment

deploy the basic setup

```
oc create -k troubleshooting/targetallocator
```

## verification and first thing to recognize

verifying that the targetAllocator provides the targets we configured 

```
oc -n otctargetallocator exec -ti otcta-collector-0 -c debug -- curl otcta-targetallocator/scrape_configs
```

Expected output

```
{"otc0":{"enable_compression":true,"enable_http2":true,"fallback_scrape_protocol":"PrometheusText1.0.0","follow_redirects":true,"honor_timestamps":true,"job_name":"otc0","metric_relabel_configs":[{"action":"keep","regex":"up|TargetAllocator","replacement":"$1","separator":";","source_labels":["__name__"]}],"metrics_path":"/metrics","scheme":"http","scrape_interval":"10s","scrape_protocols":["OpenMetricsText1.0.0","OpenMetricsText0.0.1","PrometheusText1.0.0","PrometheusText0.0.4"],"scrape_timeout":"10s","static_configs":[{"targets":["127.0.0.1:9090"]}],"track_timestamps_staleness":false},"otc1":{"enable_compression":true,"enable_http2":true,"fallback_scrape_protocol":"PrometheusText1.0.0","follow_redirects":true,"honor_timestamps":true,"job_name":"otc1","metric_relabel_configs":[{"action":"keep","regex":"up|TargetAllocator","replacement":"$1","separator":";","source_labels":["__name__"]}],"metrics_path":"/metrics","scheme":"http","scrape_interval":"10s","scrape_protocols":["OpenMetricsText1.0.0","OpenMetricsText0.0.1","PrometheusText1.0.0","PrometheusText0.0.4"],"scrape_timeout":"10s","static_configs":[{"targets":["127.0.0.1:9091"]}],"track_timestamps_staleness":false},"otc2":{"enable_compression":true,"enable_http2":true,"fallback_scrape_protocol":"PrometheusText1.0.0","follow_redirects":true,"honor_timestamps":true,"job_name":"otc2","metric_relabel_configs":[{"action":"keep","regex":"up|TargetAllocator","replacement":"$1","separator":";","source_labels":["__name__"]}],"metrics_path":"/metrics","scheme":"http","scrape_interval":"10s","scrape_protocols":["OpenMetricsText1.0.0","OpenMetricsText0.0.1","PrometheusText1.0.0","PrometheusText0.0.4"],"scrape_timeout":"10s","static_configs":[{"targets":["127.0.0.1:9092"]}],"track_timestamps_staleness":false}}
```

verifying the opentelemetry collector prometheus receiver 

```
oc -n otctargetallocator exec -ti otcta-collector-0 -c debug -- curl localhost:8889/metrics -w '%{http_code}\n'
```

Expected output

```
200
```

This is not quite what we are looking for as there's not a singl scrape target or scrape result metric expose.
Reason for that is visible in the targetAllocator pod

```
oc -n otctargetallocator logs deploy/otcta-targetallocator -c ta-container | tail -1
```

Expected output

```
{"level":"error","ts":"2026-02-15T13:18:27Z","msg":"Unhandled Error","logger":"UnhandledError","error":"k8s.io/client-go@v0.32.3/tools/cache/reflector.go:251: Failed to watch *v1.Pod: failed to list *v1.Pod: pods is forbidden: User \"system:serviceaccount:otctargetallocator:default\" cannot list resource \"pods\" in API group \"\" in the namespace \"otctargetallocator\"","stacktrace":"k8s.io/client-go/tools/cache.DefaultWatchErrorHandler\n\tk8s.io/client-go@v0.32.3/tools/cache/reflector.go:166\nk8s.io/client-go/tools/cache.(*Reflector).Run.func1\n\tk8s.io/client-go@v0.32.3/tools/cache/reflector.go:316\nk8s.io/apimachinery/pkg/util/wait.BackoffUntil.func1\n\tk8s.io/apimachinery@v0.32.3/pkg/util/wait/backoff.go:226\nk8s.io/apimachinery/pkg/util/wait.BackoffUntil\n\tk8s.io/apimachinery@v0.32.3/pkg/util/wait/backoff.go:227\nk8s.io/client-go/tools/cache.(*Reflector).Run\n\tk8s.io/client-go@v0.32.3/tools/cache/reflector.go:314\nk8s.io/client-go/tools/cache.(*controller).Run.(*Group).StartWithChannel.func2\n\tk8s.io/apimachinery@v0.32.3/pkg/util/wait/wait.go:55\nk8s.io/apimachinery/pkg/util/wait.(*Group).Start.func1\n\tk8s.io/apimachinery@v0.32.3/pkg/util/wait/wait.go:72"}
```

So it's mandatory to understand that the targetAllocator Pod requires permissions to discover and accept collector Pods.
Add the missing permissions by executing

```
oc -n otctargetallocator apply -f troubleshooting/targetallocator/rbac.yml
```

To speed things up restart both pods 

```
oc -n otctargetallocator rollout restart deploy/otcta-targetallocator 
sleep 3
oc -n otctargetallocator rollout restart statefulset/otcta-collector
```

**NOTE** without the targetallocator being up and ready the collector will not update it's list of targets in the very exact moment that is the reason for the staged rollout.


verifying the opentelemetry collector prometheus receiver not has targets listed and the metrics being scraped

```
oc -n otctargetallocator exec -ti otcta-collector-0 -c debug -- curl localhost:8889/metrics | grep -E '(target_info|TargetAllocator_total)'
```

Expected output
```
# HELP TargetAllocator_total a sample counter metric
# TYPE TargetAllocator_total counter
TargetAllocator_total{instance="127.0.0.1:9090",job="otc0",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.1:9091",job="otc1",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.1:9092",job="otc2",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
# HELP target_info Target metadata
# TYPE target_info gauge
target_info{instance="127.0.0.1:9090",job="otc0",server_port="9090",url_scheme="http"} 1
target_info{instance="127.0.0.1:9091",job="otc1",server_port="9091",url_scheme="http"} 1
target_info{instance="127.0.0.1:9092",job="otc2",server_port="9092",url_scheme="http"} 1
```

## collector assignments by the targetAllocator

Unfortunately by the minute of writing, the targetAllocator CR lacks the possibility to add which collectors are excepted for being used in the distribution. That might lead to situations where a collector will not receive any assignement like

Execute following commands

```
oc -n otctargetallocator apply -f troubleshooting/targetallocator/targetallocator2.yml
oc -n otctargetallocator rollout restart statefulset/otcta-collector
```

now we might have no scrape targets assigned to the collector. If you see 

```
oc -n otctargetallocator exec -ti otcta-collector-0 -c debug -- curl localhost:8889/metrics -w '%{http_code}\n'
```
Expected output
```
200
```

again, even though both targetAllocators are up and ready, the targetAllocator assigned the slots to itself and the other targetAllocator.
You can check with executing

```
oc -n otctargetallocator port-forward service/otcta-targetallocator 8080:80 & 
```

and hit your local browser to http://localhost:8080

```#table format of the targetAllocator collector section


Collector	Job Count	Target Count
otcta-collector-0	0	0
otcta-targetallocator-fc7b8bf8-sqzmp	1	1
otcta2-targetallocator-fcbc4b858-2hd82	2	2
```

To fix this, for now we need to set the targetAllocator unmanaged and manually add the classification of which collectors are allowed to join.

```
oc -n otctargetallocator extract cm/otcta-targetallocator --to=- | yq -ry '.collector_selector={"matchLabels":{"app.kubernetes.io/instance":"otctargetallocator.otcta","app.kubernetes.io/managed-by":"opentelemetry-operator","app.kubernetes.io/component":"opentelemetry-collector"}}' > tacm.yml
```

The command above creates a copy with the collector_selector labels required to match only our OpenTelemetryCollector.
Next we set the targetAllocator `unmanaged` by executing following command

```
oc -n otctargetallocator patch targetallocator otcta --type=merge -p '{"spec":{"managementState":"unmanaged"}}'
```

Than we replace the configMap that has the current targetAllocator configuration with the new one we just created

```
oc -n otctargetallocator create cm otcta-targetallocator --from-file=targetallocator.yaml=tacm.yml \
 --dry-run=client -o yaml | \
oc -n otctargetallocator apply -f-
oc -n otctargetallocator rollout restart deploy/otcta-targetallocator
```

Since we are `unmanaged` we also need to take about the lifecycle of the pod including the configuration reload.

A final restart of the OTC should reveal all all targets from the first targetAlloator.

```
oc -n otctargetallocator rollout restart statefulset/otcta-collector
oc -n otctargetallocator exec -ti otcta-collector-0 -c debug -- curl localhost:8889/metrics | grep -E '(target_info|TargetAllocator_total)'
```

Expected output similar to 
```
# HELP TargetAllocator_total a sample counter metric
# TYPE TargetAllocator_total counter
TargetAllocator_total{instance="127.0.0.1:9090",job="otc0",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.1:9091",job="otc1",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.1:9092",job="otc2",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.2:9090",job="otc3",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.2:9091",job="otc4",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
# HELP target_info Target metadata
# TYPE target_info gauge
target_info{instance="127.0.0.1:9090",job="otc0",server_port="9090",url_scheme="http"} 1
target_info{instance="127.0.0.1:9091",job="otc1",server_port="9091",url_scheme="http"} 1
target_info{instance="127.0.0.1:9092",job="otc2",server_port="9092",url_scheme="http"} 1
target_info{instance="127.0.0.2:9090",job="otc3",server_port="9090",url_scheme="http"} 1
target_info{instance="127.0.0.2:9091",job="otc4",server_port="9091",url_scheme="http"} 1
```

Since the second targetAllocator does not have the selector workaround the resulting list will not be all targets. You know how to fix that already.

The final target list shall look like following after repeating the steps of setting otcta2 unmanaged and applying the selector labels

```
# HELP TargetAllocator_total a sample counter metric
# TYPE TargetAllocator_total counter
TargetAllocator_total{instance="127.0.0.1:9090",job="otc0",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.1:9091",job="otc1",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.1:9092",job="otc2",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.2:9090",job="otc3",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.2:9091",job="otc4",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
TargetAllocator_total{instance="127.0.0.2:9092",job="otc5",otel_scope_name="github.com/open-telemetry/opentelemetry-collector-contrib/receiver/prometheusreceiver",otel_scope_schema_url="",otel_scope_version="0.140.1"} 1
# HELP target_info Target metadata
# TYPE target_info gauge
target_info{instance="127.0.0.1:9090",job="otc0",server_port="9090",url_scheme="http"} 1
target_info{instance="127.0.0.1:9091",job="otc1",server_port="9091",url_scheme="http"} 1
target_info{instance="127.0.0.1:9092",job="otc2",server_port="9092",url_scheme="http"} 1
target_info{instance="127.0.0.2:9090",job="otc3",server_port="9090",url_scheme="http"} 1
target_info{instance="127.0.0.2:9091",job="otc4",server_port="9091",url_scheme="http"} 1
target_info{instance="127.0.0.2:9092",job="otc5",server_port="9092",url_scheme="http"} 1
```

# clean up

```
oc delete -k troubleshooting/targetallocator
```
