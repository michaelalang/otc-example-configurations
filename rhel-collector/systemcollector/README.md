# OpenTelemetry on Red Hat Enterprise Systems (RHEL)

the show-cases provides legacy system logs,metrics,traces collection capability 

# Requirements

* Superuser privileges to install packages
* a valid RHEL subscription for pulling content from the yum repositories
* Any OTEL receiving endpoint as debug will create loops of loops for logs

**NOTE** for simplicity we are going through the steps manually. I recommend to use Ansible for automation instead.

## deployment process

Install the `opentelemetry-collector` package 

```
sudo dnf install -y opentelemetry-collector
```

next we create a spooling directory for the signals.
**NOTE** use a separate partition to avoid filling an existing one like root.

```
sudo mkdir /queue
sudo mkdir /queue/work /queue/compact
sudo chown observability:observability -R /queue
```

than we remove the default configuration that the RPM package ships.

```
sudo rm -f /etc/opentelemetry-collector/configs/00-default-receivers.yaml
```

and instead we deploy the repository specific one `otc.yml` 

```
sudo otc.yml /etc/opentelemetry-collector/configs/otc.yaml
```

**NOTE** ensure to adjust all exporter endpoints according to your infrastructure

start the opentelemetry collector 

```
sudo systemctl enable --now opentelemetry-collector
```

If you do not have any OTLP collector available for the signals, you can spin up a debug instance on your host by executing

```
opentelemetry-collector --config ./otc-debug.yml
```

ensure to adjust the exporter settings in the system Collector towards

```
  # for otlp/grpc endpoints
  endpoint: 'http://127.0.0.1:14317'
  tls:
    insecure: true
  # for otlphttp endpoints
  endpoint: 'http://127.0.0.1:14318'
  tls:
    insecure: true
```

# clean up

```
sudo systemctl stop opentelemetry-collector
sudo dnf -y remove opentelemetry-collector
sudo rm -fR /queue
```
