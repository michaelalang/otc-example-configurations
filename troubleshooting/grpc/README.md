# OpenTelemetry debugging GRPC receiver/exporter

This repository helps to understand certain use-cases for troubleshooting and debugging.

In this scenario we deal with errors from GRPC side like

```
grpc: received message after decompression larger than max 4194304
```

# Requirements

* ghcr.io access as the telemetrygen image is retrieved from there.

## deployment process

The deployment injects:

* two OTC deployment listening on otlp/grpc protocol port 4317
* manual inject telemetrygen1 and telemetrygen2

```
oc create -k troubleshooting/grpc
```

once both OTC deployment are ready we inject the `telemetrygen1.yml` which creates logs/metrics/traces with a size of exceeding the default 4MB grpc limit

```
oc -n otcdebuggrpc create -f troubleshooting/grpc/telemetrygen1.yml
```

we should see errors on the sender collector similar to

```
oc -n otcdebuggrpc logs deploy/otc-sender-collector | tail -15
```

Expected output
```
2026-02-11T08:23:09.810Z	info	service@v0.140.0/service.go:247	Everything is ready. Begin running and processing data.	{"resource": {"service.instance.id": "7fb04e77-bbb2-4d0c-abae-b9c75d89ef35", "service.name": "otelcol", "service.version": "0.140.1"}}
2026-02-11T08:45:04.359Z	error	internal/queue_sender.go:49	Exporting failed. Dropping data.	{"resource": {"service.instance.id": "7fb04e77-bbb2-4d0c-abae-b9c75d89ef35", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "otlp", "otelcol.component.kind": "exporter", "otelcol.signal": "logs", "error": "not retryable error: Permanent error: rpc error: code = ResourceExhausted desc = grpc: received message after decompression larger than max 4194304", "dropped_items": 1}
go.opentelemetry.io/collector/exporter/exporterhelper/internal.NewQueueSender.func1
	go.opentelemetry.io/collector/exporter/exporterhelper@v0.140.0/internal/queue_sender.go:49
go.opentelemetry.io/collector/exporter/exporterhelper/internal/queuebatch.(*disabledBatcher[...]).Consume
	go.opentelemetry.io/collector/exporter/exporterhelper@v0.140.0/internal/queuebatch/disabled_batcher.go:23
go.opentelemetry.io/collector/exporter/exporterhelper/internal/queue.(*asyncQueue[...]).Start.func1
	go.opentelemetry.io/collector/exporter/exporterhelper@v0.140.0/internal/queue/async_queue.go:49
2026-02-11T08:45:05.718Z	error	internal/queue_sender.go:49	Exporting failed. Dropping data.	{"resource": {"service.instance.id": "7fb04e77-bbb2-4d0c-abae-b9c75d89ef35", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "otlp", "otelcol.component.kind": "exporter", "otelcol.signal": "traces", "error": "not retryable error: Permanent error: rpc error: code = ResourceExhausted desc = grpc: received message after decompression larger than max 4194304", "dropped_items": 2}
go.opentelemetry.io/collector/exporter/exporterhelper/internal.NewQueueSender.func1
	go.opentelemetry.io/collector/exporter/exporterhelper@v0.140.0/internal/queue_sender.go:49
go.opentelemetry.io/collector/exporter/exporterhelper/internal/queuebatch.(*disabledBatcher[...]).Consume
	go.opentelemetry.io/collector/exporter/exporterhelper@v0.140.0/internal/queuebatch/disabled_batcher.go:23
go.opentelemetry.io/collector/exporter/exporterhelper/internal/queue.(*asyncQueue[...]).Start.func1
	go.opentelemetry.io/collector/exporter/exporterhelper@v0.140.0/internal/queue/async_queue.go:49
```

since the `otc-reciever` is set to not accept messages larger than 4M the `otc-sender` reports the problem. **NOTE** dispatched error from the exporter not the receiver on the telemetrygen endpoint.

## mitigating `larger than max` error messages

As mentioned it's not the `otc-sender` which has the problem but the `otc-receiver` which get's the signals from the otc-sender.

### ensure your batch sizes aren't cumulated to a bigger size than the `max_recv_msg_size_mib` on the `otc-receiver` collector.

the `telemetrygen2.yml` switched the size/message and batching towards a working configuration.

first restart the `otc-sender` collector to have a clear output in the logs

```
oc -n otcdebuggrpc rollout restart deploy/otc-sender-collector
```

next delete the `telemetrygen1` pod 

```
oc -n otcdebuggrpc delete -f troubleshooting/grpc/telemetrygen1.yml
```

than re-create the same telemetrygen1 instance

```
oc -n otcdebuggrpc create -f troubleshooting/grpc/telemetrygen2.yml
```

we have now change the behavior and `queuing` on the Exporter chunks them to larger values as 4194304

Understanding the batch chunking might be difficult but since we know, we are sending 2 signals each 2MB and in total exceeding the 4MB default,
we can utilize the `batch` processor to limit dispatching to one chunk (works only if 1 signal isn't bigger than max_recv_msg_size_mib) 

```
oc -n otcdebuggrpc apply -f troubleshooting/grpc/otc-sender-batch-limited.yml
```

revalidate the stepbs by executing

```
oc -n otcdebuggrpc delete -f troubleshooting/grpc/telemetrygen2.yml
sleep 5
oc -n otcdebuggrpc create -f troubleshooting/grpc/telemetrygen2.yml
```

The logs and traces should now be visible in the `otc-receiver` collector

### ensure your `max_recv_msg_size_mib` value is streamlined between all collectors

```
oc -n otcdebuggrpc apply -f otc-receiver-grpc-sized.yml 
```

cleanup any telemetrygen pods from the previous exercises

```
oc -n otcdebuggrpc delete -f troubleshooting/grpc/telemetrygen1.yml
oc -n otcdebuggrpc delete -f troubleshooting/grpc/telemetrygen2.yml
```

recreate both telemetrygenerators as both shall now successfully be handled

```
oc -n otcdebuggrpc create -f troubleshooting/grpc/telemetrygen1.yml
oc -n otcdebuggrpc create -f troubleshooting/grpc/telemetrygen2.yml
```

verify that 4 logs and 4 traces have been dispatched to the `otc-reciever` collector

```
oc -n otcdebuggrpc logs deploy/otc-receiver-collector
```


# clean up

```
oc delete -f otcdebuggrpc delete -f troubleshooting/grpc/telemetrygen1.yml
oc delete -f otcdebuggrpc delete -f troubleshooting/grpc/telemetrygen2.yml
oc delete -k otcdebuggrpc
```
