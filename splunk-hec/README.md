# Splunk-HEC OTLP configuration

the use-case show-cases a Splunk-HEC deployment with OTC:

# Requirements

## deployment process

The deployment injects:

* a Splunk-Hec server with an OTC sidecar to take 4317/grpc and 4318/http OTEL messages and inject them into Splunk.

```
oc create -k splunk-hec
```

Wait until the log of the Splunk-hec pod shows
```
Ansible playbook complete, will begin streaming splunkd_stderr.log
```

## verification using telmetrygen

```
oc -n otcsplunkhec create -f splunk-hec/telemetrygen.yml
```

## verification of the OTLP logs in Splunk

use port-forwarding to access the Splunk UI 

```
oc -n otcsplunkhec port-forward service/splunk-hec 8000:8000 &
```

access the UI and authenticate with the credentials from the environment (admin:changeme)

```
http://localhost:8000
```

Select `Search & Reporting` 

Enter following `New Search`

```
index=main sourcetype=otlp_clean
| spath path=resourceLogs{}.scopeLogs{}.logRecords{}.body.stringValue output=json_body
| spath input=json_body
| fields - json_body
```

# clean up

```
oc -n otcsplunkhec delete -f splunk-hec/telemetrygen.yml
oc delete -k splunk-hec
```
