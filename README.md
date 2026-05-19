# Finance-Banking: Advanced-Threat-Intelligence-Platform-TIP-Dynamic-Policy-Enforcer

## Project Description

Advanced Threat Intelligence Platform (TIP) with Dynamic Policy Enforcement for the Finance & Banking sector, designed to detect, analyse, and respond to cyber threats in real time using automated security policies and threat intelligence integration.

Explain:
- OSINT threat collection
- MongoDB storage
- Elasticsearch integration
- Dynamic firewall blocking
- Kibana dashboards

## Technologis Used

- Python
- MongoDB
- Elasticsearch
- Kibana
- Logstash
- Linux iptables


## Week 1: OSINT Ingestion and Database Design

First, I created Linux Environment. We have created python file which was collect malicious Ips and Domain in the OSINT threat feeds (AlienVault OTX, VirusTotal, AbuseIPDB).   
When we use this python file it gives me Ips and Domain in Json format. EX:
```json
{
  "generated_at": "2026-05-08T05:25:45.374317",
  "ips": [
    {
      "source": "AlienVault OTX",
      "ip": "45.142.36.76",
      "added_at": "2026-05-08T05:10:59.330885"
    }
  ]
}
```

I install MongoDB server and MongoDB compass.
MongoDB Compass is GUI for MongoDB, designed to help users interact with databases visually without writing command-line queries.
We have collected all data from osint_threat.py (JSON format) and insert into MongoDB Database.

## week 2: Normalization and SIEM Integration

I have created a dedicated folder named SIEM Integration in this repository. This folder contains detailed step-by-step documentation for setting up and configuring the SIEM environment, including installation, integration, and usage instructions. The guide is designed to help users easily understand and deploy the complete SIEM setup for this project.

### Risk Score Design (Planning)

This week we defined how risk score will be calculated.

Risk score is on a scale of 1–10 based on three factors:

| Factor | Logic | Max Points |
|---|---|---|
| Source count | How many feeds reported this IP | 3 |
| Threat type | Ransomware=4, Botnet/Malware=3, Phishing=2, Scanner=1 | 4 |
| Recency | Last seen ≤7 days=3, ≤30 days=2, older=1 | 3 |

Risk score implementation will be done in Week 3 inside the enforcement daemon.