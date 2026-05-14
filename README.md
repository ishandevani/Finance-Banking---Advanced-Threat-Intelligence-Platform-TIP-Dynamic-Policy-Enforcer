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
'''json
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
'''