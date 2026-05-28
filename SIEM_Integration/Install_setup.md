# ELK Stack Installation & Setup

## Overview

This project explains how to install and configure:

* Elasticsearch
* Logstash
* Kibana (ELK Stack)

with authentication enabled on Ubuntu 22.04 / 24.04.

---

# Architecture

```text id="8r8r5w"
Logstash
    ↓
Elasticsearch
    ↓
Kibana Dashboard
```

---

# System Requirements

| Component | Recommended          |
| --------- | -------------------- |
| RAM       | 4 GB Minimum         |
| CPU       | 2 Core               |
| OS        | Ubuntu 22.04 / 24.04 |

---

# Step 1: Update System

```bash id="s19clq"
sudo apt update && sudo apt upgrade -y
```

---

# Step 2: Install Required Packages

```bash id="vjlwmr"
sudo apt install apt-transport-https wget curl gnupg -y
```

---

# Step 3: Import Elastic GPG Key

```bash id="t97cws"
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | \
sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
```

---

# Step 4: Add Elastic Repository

```bash id="gwc6rx"
echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | \
sudo tee /etc/apt/sources.list.d/elastic-8.x.list
```

---

# Step 5: Update Packages

```bash id="xjlwm7"
sudo apt update
```

---

# Step 6: Install Elasticsearch

```bash id="pbjlwm"
sudo apt install elasticsearch -y
```

---

# Step 7: Configure Elasticsearch

Edit configuration:

```bash id="q1m2ce"
sudo nano /etc/elasticsearch/elasticsearch.yml
```

Add:

```yaml id="i2zw1w"
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node

xpack.security.enabled: true
xpack.security.enrollment.enabled: true
```

---

# Step 8: Start Elasticsearch

```bash id="i6g4xw"
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
```

Check status:

```bash id="llyf9e"
sudo systemctl status elasticsearch
```

---

# Step 9: Reset Elasticsearch Password

Generate password for elastic user:

```bash id="wsjlwm"
/usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

Example output:

```text id="rmjlwm"
New value: Abcd@1234
```

Save this password.

---

# Step 10: Verify Elasticsearch

```bash id="jlwm85"
curl -u elastic localhost:9200
```

Enter password when prompted.

---

# Step 11: Install Kibana

```bash id="jlwm56"
sudo apt install kibana -y
```

---

# Step 12: Configure Kibana

Edit configuration:

```bash id="jlwm11"
sudo nano /etc/kibana/kibana.yml
```

Add:

```yaml id="jlwm33"
server.port: 5601
server.host: "0.0.0.0"

elasticsearch.hosts: ["http://localhost:9200"]

elasticsearch.username: "kibana_system"
elasticsearch.password: "YOUR_PASSWORD"
```

---

# Step 13: Generate Kibana Enrollment Token

Run:

```bash id="jlwm66"
/usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

Copy generated token.

---

# Step 14: Start Kibana

```bash id="jlwm22"
sudo systemctl enable kibana
sudo systemctl start kibana
```

Check status:

```bash id="jlwm44"
sudo systemctl status kibana
```

---

# Step 15: Access Kibana

Open browser:

```text id="jlwm99"
http://YOUR-IP:5601
```

You will see the Kibana login page.

Login using:

| Username | Password                |
| -------- | ----------------------- |
| elastic  | Your generated password |

---

# Step 16: Install Logstash

```bash id="jlwm77"
sudo apt install logstash -y
```

---

# Step 17: Configure Logstash Authentication

Create configuration file:

```bash id="jlwm55"
sudo nano /etc/logstash/conf.d/elastic.conf
```

Add:

```ruby id="jlwm88"
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]

    user => "elastic"
    password => "YOUR_PASSWORD"

    index => "logs"
  }
}
```

---

# Step 18: Start Logstash

```bash id="jlwm12"
sudo systemctl enable logstash
sudo systemctl start logstash
```

Check status:

```bash id="jlwm14"
sudo systemctl status logstash
```

---

# Useful Commands

## Restart Services

```bash id="jlwm15"
sudo systemctl restart elasticsearch
sudo systemctl restart kibana
sudo systemctl restart logstash
```

---

## Check Service Status

```bash id="jlwm16"
sudo systemctl status elasticsearch
sudo systemctl status kibana
sudo systemctl status logstash
```

---

## View Elasticsearch Indices

```bash id="jlwm17"
curl -u elastic localhost:9200/_cat/indices?v
```

---

# Kibana Dashboard

Below is the successfully configured ELK Stack dashboard screenshot.

![ELK Dashboard](/screenshots/ELK.png)

---

# Conclusion

This setup creates a complete ELK Stack environment with authentication enabled for secure log monitoring, analytics, and visualization using Elasticsearch, Logstash, and Kibana.
