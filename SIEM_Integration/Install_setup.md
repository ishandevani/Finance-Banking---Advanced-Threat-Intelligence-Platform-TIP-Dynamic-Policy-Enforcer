# ELK Stack Installation & Setup

## Overview

This project explains how to install and configure:

* Elasticsearch
* Logstash
* Kibana (ELK Stack)

on Ubuntu 22.04 / 24.04.

---

# Architecture

```text
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

```bash
sudo apt update && sudo apt upgrade -y
```

---

# Step 2: Install Required Packages

```bash
sudo apt install apt-transport-https wget curl gnupg -y
```

---

# Step 3: Import Elastic GPG Key

```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | \
sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
```

---

# Step 4: Add Elastic Repository

```bash
echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | \
sudo tee /etc/apt/sources.list.d/elastic-8.x.list
```

---

# Step 5: Update Packages

```bash
sudo apt update
```

---

# Step 6: Install Elasticsearch

```bash
sudo apt install elasticsearch -y
```

---

# Step 7: Configure Elasticsearch

Edit configuration:

```bash
sudo nano /etc/elasticsearch/elasticsearch.yml
```

Add:

```yaml
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
```

---

# Step 8: Start Elasticsearch

```bash
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
```

Check status:

```bash
sudo systemctl status elasticsearch
```

---

# Step 9: Verify Elasticsearch

```bash
curl localhost:9200
```

---

# Step 10: Install Kibana

```bash
sudo apt install kibana -y
```

---

# Step 11: Configure Kibana

Edit configuration:

```bash
sudo nano /etc/kibana/kibana.yml
```

Add:

```yaml
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
```

---

# Step 12: Start Kibana

```bash
sudo systemctl enable kibana
sudo systemctl start kibana
```

Check status:

```bash
sudo systemctl status kibana
```

---

# Step 13: Access Kibana

Open browser:

```text
http://YOUR-IP:5601
```

Example:

```text
http://192.168.1.10:5601
```

---

# Step 14: Install Logstash

```bash
sudo apt install logstash -y
```

---

# Step 15: Verify Logstash

```bash
/usr/share/logstash/bin/logstash --version
```

---

# Step 16: Start Logstash

```bash
sudo systemctl enable logstash
sudo systemctl start logstash
```

Check status:

```bash
sudo systemctl status logstash
```

---

# Useful Commands

## Restart Services

```bash
sudo systemctl restart elasticsearch
sudo systemctl restart kibana
sudo systemctl restart logstash
```

---

## Check Service Status

```bash
sudo systemctl status elasticsearch
sudo systemctl status kibana
sudo systemctl status logstash
```

---

## View Elasticsearch Indices

```bash
curl localhost:9200/_cat/indices?v
```

---

# Kibana Dashboard

Below is the successfully configured ELK Stack dashboard screenshot.

![ELK.png](/screenshots/ELK.png)

---

# Conclusion

This setup creates a complete ELK Stack environment for log monitoring, analytics, and visualization using Elasticsearch, Logstash, and Kibana.
