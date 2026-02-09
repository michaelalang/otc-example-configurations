# Kafka broker and OTC forwarding

the use-case show-cases forwarding and consumption of Kafka messages

The `producer` sends a message to the Broker. OTC consumes that message from the topic and forwards it to various other Topics (otlp_logs2 and otlp_logs3).
The `consumer` listens for messages in the Broker on `otlp_logs2` by default. The scenario will as well switch to `otlp_logs3`.

# Requirements

* docker.io access as the Apache Kafka image is fetched from there.

## deployment process

The deployment injects:

* two configMaps with the code of the consumer and the producer
    * consumer listens for `otlp_logs2` by default
    * producer creates message(s) in `otlp_logs` 
* the OTC is injected as sidecar

```
oc create -k kafka
```

## initial topic creation

the default Broker setup does not create a topic which is why you will see following `info` log on the `otc-container`

```
2026-01-19T18:29:01.775Z info franz kzap@v1.1.2/kzap.go:114 metadata update triggered {"resource": {"service.instance.id": "74e62a7b-0a3c-430c-b272-35d159667715", "service.name": "otelcol", "service.version": "0.140.1"}, "otelcol.component.id": "kafka", "otelcol.component.kind": "receiver", "otelcol.signal": "logs", "why": "re-updating due to inner errors: UNKNOWN_TOPIC_OR_PARTITION{otlp_logs}"}
```

* execute following command to send one message to the Broker and create the Topic

```
oc -n otckafka exec -ti deploy/kafka -c producer -- python producer.py
```

* execute another producer message to receive the OTLP log debug output (initial message is lost as the Topic wasn't consumed by OTC as it was missing)

```
oc -n otckafka exec -ti deploy/kafka -c producer -- python producer.py
```

* expected output (or similar since the content is generated)

```
2026-01-19T18:31:03.288Z info ResourceLog #0
Resource SchemaURL:
ScopeLogs #0
ScopeLogs SchemaURL:
InstrumentationScope
LogRecord #0
ObservedTimestamp: 1970-01-01 00:00:00 +0000 UTC
Timestamp: 1970-01-01 00:00:00 +0000 UTC
SeverityText:
SeverityNumber: Unspecified(0)
Body: Str({"message": "Clear role say phone common political.", "host": "oteltest", "facility": "user", "hostname": "oteltest", "application": "__main__", "service_name": "otel", "service_namespace": "otel-test", "timestamp": 1768847463.183423, "level": "INFO", "pid": 59})
Trace ID:
Span ID:
Flags: 0
```

## Consume on various Topics

* execute following command to consume message from the Topic `otlp_logs2`

```
oc -n otckafka exec -ti deploy/kafka -c consumer -- python consumer.py
```

* in another terminal execute another producer message

```
oc -n otckafka exec -ti deploy/kafka -c producer -- python producer.py
```

* expected output in the consumer logs (or similar since the content is generated)

```
ConsumerRecord(topic='otlp_logs2', partition=0, leader_epoch=0, offset=1, timestamp=1768847656916, timestamp_type=0, key=None, value=b'{"application":"__main__","facility":"user","host":"oteltest","hostname":"oteltest","level":"INFO","message":"What account if talk. Friend structure store beyond mean.","pid":87,"service_name":"otel","service_namespace":"otel-test","timestamp":1768847656.8115013}', headers=[], checksum=None, serialized_key_size=-1, serialized_value_size=263, serialized_header_size=-1)
```

* stop the `oltp_logs2` consumer and consume messages from Topic `otlp_logs3`

```
# [CTRL+C] in consumer Terminal
oc -n otckafka exec -ti deploy/kafka -c consumer -- python consumer.py otlp_logs3
```

* in another terminal execute another producer message

```
oc -n otckafka exec -ti deploy/kafka -c producer -- python producer.py
```

* expected output in the consumer logs (or similar since the content is generated)

```
ConsumerRecord(topic='otlp_logs3', partition=0, leader_epoch=0, offset=2, timestamp=1768847778639, timestamp_type=0, key=None, value=b'{"application":"__main__","facility":"user","host":"oteltest","hostname":"oteltest","level":"INFO","message":"Politics course require reason institution. Same rule law help bar discuss. Certain may capital audience speech view begin wonder.","pid":106,"service_name":"otel","service_namespace":"otel-test","timestamp":1768847778.5352297}', headers=[], checksum=None, serialized_key_size=-1, serialized_value_size=337, serialized_header_size=-1)
```

* if you want to create more than one record execute following producer command

```
oc -n otckafka exec -ti deploy/kafka -c producer -- /bin/sh -c "COUNT=100 python producer.py"
```

# clean up

```
oc delete -k kafka
```
