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

## Database

- MongoDB setup and configuration
- `mongo_to_es.py` — pipes threat data from MongoDB into Elasticsearch for a searchable, visual threat landscape via Kibana

### Risk Score Design (Planning)

This week we defined how risk score will be calculated.

Risk score is on a scale of 1–10 based on three factors:

| Factor | Logic | Max Points |
|---|---|---|
| Source count | How many feeds reported this IP | 3 |
| Threat type | Ransomware=4, Botnet/Malware=3, Phishing=2, Scanner=1 | 4 |
| Recency | Last seen ≤7 days=3, ≤30 days=2, older=1 | 3 |

Risk score implementation will be done in Week 3 inside the enforcement daemon.

## Week 3: Dynamic Policy Enforcement Engine

we developed the Dynamic Security Policy Enforcer module. A Python script was created to assign risk scores to collected threat indicators based on their source and severity. The system continuously monitors high-risk indicators stored in the MongoDB database and automatically blocks malicious IP addresses using Linux iptables firewall rules. This automation helps proactively protect organizational systems by dynamically updating security policies and preventing connections from malicious infrastructure in real time.

we created policy_enforcer.py script for Dynamic Policy Enforcement in Enforcer folder.

 ## Threat Intelligence Enrichment

The `virustotal_enrich.py` script in the `processing/` folder automates the enrichment of threat intelligence data using the VirusTotal API.

### Key Features
* **Automated Lookups:** Queries VirusTotal API for threat feed IPs and domains.
* **Context Enrichment:** Extracts malicious scores, reputation, ASN, and country data.
* **Batch Processing:** Handles large datasets efficiently in batches.
* **Fault Tolerance:** Automatically saves progress to prevent data loss during interruptions.
* **Structured Output:** Generates a fully enriched, production-ready JSON threat feed.

This script uses the VirusTotal API to enrich threat intelligence indicators collected from sources such as AlienVault OTX. It converts basic IOC data containing only source, IP/domain, and timestamp into an enriched threat intelligence format by adding malicious score, suspicious score, country, ASN, reputation, calculated risk score, and severity level.

Example Transformation:

Input:
```json
{
    "source": "AlienVault OTX",
    "ip": "209.99.185.223",
    "added_at": "2026-05-13T02:38:48.420283"
}
```
Output:
```json
{
    "source": "AlienVault OTX",
    "ip": "209.99.185.223",
    "added_at": "2026-05-13T02:38:48.420283",
    "malicious_score": 9,
    "suspicious_score": 2,
    "country": "CH",
    "asn": 402253,
    "reputation": 0,
    "risk_score": 6,
    "severity": "high"
}
```
The script processes indicators in batches, automatically tracks progress, handles API errors, and generates an enriched JSON threat intelligence feed suitable for SIEM integration and threat analysis.

## Week 4: Alerting, Testing, and Final Reporting

During Week 4, the project focused on validation, visualization, and incident response management. A rollback mechanism was implemented to allow SOC analysts to reverse automated firewall rules in case of false-positive detections. The system updates MongoDB records and removes the corresponding UFW firewall rule when an IP is unblocked.

Key activities completed:

* Implemented `rollback.py` for automated firewall rule reversal.
* Added MongoDB status tracking for blocked and unblocked IPs.
* Tested Dynamic Security Policy Enforcer and rollback workflows.
* Verified automated IP blocking and unblocking functionality.
* Enhanced Kibana dashboards to visualize threat intelligence and blocked indicators.
* Documented testing procedures, project architecture, and deployment steps.
* Finalized GitHub repository structure and project documentation.

### Outcome

The Threat Intelligence Platform now supports the complete threat lifecycle:

```text
Threat Detection
        ↓
Risk Scoring
        ↓
Automatic IP Blocking
        ↓
SOC Analyst Review
        ↓
Rollback (False Positive Handling)
        ↓
Dashboard Visualization & Reporting
```

This completes the implementation of an automated Threat Intelligence Platform with dynamic security policy enforcement and incident response capabilities.
