# Dynamic Security Policy Enforcer

## Overview

The Dynamic Security Policy Enforcer is a Python daemon that continuously monitors threat intelligence data stored in MongoDB. It automatically blocks high-risk IP addresses based on their assigned risk score.

This module transforms threat intelligence into automated security actions by enforcing firewall policies in real time.

---

## How It Works

1. Continuously monitors the MongoDB threat database.
2. Reads IP indicators and their associated risk scores.
3. Compares each risk score against a predefined threshold.
4. Automatically blocks IPs with a risk score greater than or equal to 8.
5. Stores blocked IPs in MongoDB to avoid duplicate rules.
6. Repeats the process every 60 seconds.

### Workflow

```text
Threat Intelligence Sources
            │
            ▼
        MongoDB
            │
            ▼
 Dynamic Security Policy Enforcer
            │
            ▼
      Risk Score Check
            │
      risk_score >= 8
            │
            ▼
      Block Malicious IP
            │
            ▼
          iptables
```

---

## Risk Score Policy

| Risk Score | Severity | Action   |
| ---------- | -------- | -------- |
| 0 - 2      | Low      | Monitor  |
| 3 - 5      | Medium   | Monitor  |
| 6 - 7      | High     | Alert    |
| 8 - 10     | Critical | Block IP |

---

## How IP Blocking Works

If an IP has a risk score greater than or equal to 8:

```python
if risk_score >= 8:
    block_ip(ip)
```

The daemon creates an iptables firewall rule:

```bash
iptables -A INPUT -s <IP_ADDRESS> -j DROP
```

Example:

```bash
iptables -A INPUT -s 209.99.185.223 -j DROP
```

This blocks all incoming traffic from the malicious IP.

---

# Installation

## Install Dependencies

```bash
pip install pymongo python-daemon
```

---

## Run the Daemon

```bash
sudo python3 policy_enforcer.py
```

The daemon will start monitoring MongoDB in the background.

---

# Verification Commands

## Check if Daemon is Running

```bash
ps aux | grep policy_enforcer
```

Example:

```text
root     15420  0.0  python3 policy_enforcer.py
```

---

## Check Daemon Process ID (PID)

```bash
pgrep -f policy_enforcer.py
```

Example:

```text
15420
```

---

## View Running Python Processes

```bash
ps -ef | grep python
```

---

# Firewall Verification

## Show All Firewall Rules

```bash
sudo iptables -L -n
```

---

## Show INPUT Rules

```bash
sudo iptables -L INPUT -n
```

---

## Show Line Numbers

```bash
sudo iptables -L INPUT --line-numbers -n
```

---

## Verify Specific IP is Blocked

```bash
sudo iptables -L INPUT -n | grep 209.99.185.223
```

Example Output:

```text
DROP    all    --    209.99.185.223    0.0.0.0/0
```

---

# MongoDB Verification

## Open Mongo Shell

```bash
mongosh
```

---

## Select Database

```javascript
use Threat
```

---

## View Blocked IPs

```javascript
db.blocked_ips.find().pretty()
```

---

## Count Blocked IPs

```javascript
db.blocked_ips.countDocuments()
```

---

# Stop the Daemon

## Find Process

```bash
pgrep -f policy_enforcer.py
```

---

## Kill Using PID

```bash
sudo kill <PID>
```

Example:

```bash
sudo kill 15420
```

---

## Force Kill

```bash
sudo kill -9 <PID>
```

Example:

```bash
sudo kill -9 15420
```

---

# Unblock IP Address

## Remove Specific Rule

```bash
sudo iptables -D INPUT -s 209.99.185.223 -j DROP
```

---

## Verify Removal

```bash
sudo iptables -L INPUT -n
```

---

# Monitoring Logs

## View Live Logs

```bash
tail -f policy_enforcer.log
```

---

# Features

* Continuous threat monitoring
* Automated security policy enforcement
* Risk-based blocking
* MongoDB integration
* Duplicate block prevention
* Real-time firewall updates
* Automated threat mitigation
* Linux daemon support

---

# Technologies Used

* Python
* MongoDB
* iptables
* Python Daemon
* Elasticsearch
* Kibana
* Threat Intelligence Platform (TIP)