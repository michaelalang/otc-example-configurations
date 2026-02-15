# Ansible callback plugin for traces and metrics

## deployment

* install python3-pip package to pull the script dependencies

```
sudo dnf install -y python3-pip
```

* install the required python packages for ansible and opentelemetry

```
pip install -r requirementes.txt
```

* verify there's no missing dependecy left

```
python opentelemetry.py ; echo $?
```

* create a directory if not existing in your Ansible home to take the callback script

```
mkdir callback_plugins
cp opentelemetry.py callback_plugins/opentelemetry.py
```

* adjust your `ansible.cfg` configuration with the new Plugin setting accordingly

```#vi ansible.cfg
callback_plugins = ./callback_plugins
callbacks_enabled = opentelemetry
```

* execute a simple play to verify the functionality of the callback plugin

```
cat <<'EOF' > test-play.yml
---
- name: OTEL Monitoring configuration play
  hosts: localhost
  become: false

  tasks:
    - name: hello
      ansible.builtin.command:
        cmd: "echo Hello"
EOF

ansible-playbook test-play.yml
```

* you should see an output similar to this one

```
PLAY [OTEL Monitoring configuration play] ********************************************************************************************************

TASK [Gathering Facts] ***************************************************************************************************************************
ok: [localhost]

TASK [hello] *************************************************************************************************************************************
changed: [localhost]

PLAY RECAP ***************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

TraceID: b9e72c955274dc66b073d361403eb843
```

Use the `TraceID` to get directly to your Traces for that playbook run in Tempo 
For metrics use the metric names:

* ansible_task_duration_seconds_bucket
* ansible_task_duration_seconds_count
* ansible_task_duration_seconds_sum

to visualize the playbook and task runs.

If there are errors/warnings shown in the beginning of the ansible command output like 

```
[WARNING]: Skipping callback plugin 'opentelemetry', unable to load
```
ensure to have a match between your configuration and the plugin directory (like opentelemetry.py named wrong)

