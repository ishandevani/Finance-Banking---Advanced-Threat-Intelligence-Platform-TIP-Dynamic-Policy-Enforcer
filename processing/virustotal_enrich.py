import requests
import json
import time
import os
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
API_KEY = "YOUR_VIRUSTOTAL_API_KEY"

INPUT_FILE = "final_cleaned_osint_threat_feed.json"
OUTPUT_FILE = "virustotal_enriched_feed.json"
PROGRESS_FILE = "progress.json"

HEADERS = {
    "x-apikey": API_KEY
}

BATCH_SIZE = 100
BREAK_TIME = 60  # 1 minute

# ==========================================
# LOAD INPUT JSON
# ==========================================
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

# ==========================================
# LOAD OLD OUTPUT IF EXISTS
# ==========================================
if os.path.exists(OUTPUT_FILE):

    with open(OUTPUT_FILE, "r") as f:
        enriched_data = json.load(f)

else:

    enriched_data = {
        "generated_at": str(datetime.now()),
        "ips": [],
        "domains": []
    }

# ==========================================
# LOAD PROGRESS
# ==========================================
if os.path.exists(PROGRESS_FILE):

    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)

else:

    progress = {
        "last_ip_index": 0,
        "last_domain_index": 0
    }

# ==========================================
# VIRUSTOTAL IP CHECK
# ==========================================
def enrich_ip(ip):

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"[ERROR IP] {ip}")
        return None

    result = response.json()

    attributes = result["data"]["attributes"]

    stats = attributes.get("last_analysis_stats", {})

    return {
        "malicious_score": stats.get("malicious", 0),
        "suspicious_score": stats.get("suspicious", 0),
        "country": attributes.get("country"),
        "asn": attributes.get("asn"),
        "reputation": attributes.get("reputation")
    }

# ==========================================
# VIRUSTOTAL DOMAIN CHECK
# ==========================================
def enrich_domain(domain):

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"[ERROR DOMAIN] {domain}")
        return None

    result = response.json()

    attributes = result["data"]["attributes"]

    stats = attributes.get("last_analysis_stats", {})

    return {
        "malicious_score": stats.get("malicious", 0),
        "suspicious_score": stats.get("suspicious", 0),
        "reputation": attributes.get("reputation")
    }

# ==========================================
# PROCESS IPs
# ==========================================
start_ip = progress["last_ip_index"]
end_ip = start_ip + BATCH_SIZE

print(f"\nProcessing IPs {start_ip} -> {end_ip}\n")

for index, item in enumerate(data["ips"][start_ip:end_ip], start=start_ip):

    ip = item["ip"]

    print(f"[CHECKING IP] {ip}")

    vt_data = enrich_ip(ip)

    if vt_data:

        item.update(vt_data)

    enriched_data["ips"].append(item)

    progress["last_ip_index"] = index + 1

    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=4)

    time.sleep(15)

# ==========================================
# PROCESS DOMAINS
# ==========================================
start_domain = progress["last_domain_index"]
end_domain = start_domain + BATCH_SIZE

print(f"\nProcessing Domains {start_domain} -> {end_domain}\n")

for index, item in enumerate(data["domains"][start_domain:end_domain], start=start_domain):

    domain = item["domain"]

    print(f"[CHECKING DOMAIN] {domain}")

    vt_data = enrich_domain(domain)

    if vt_data:

        item.update(vt_data)

    enriched_data["domains"].append(item)

    progress["last_domain_index"] = index + 1

    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=4)

    time.sleep(15)

# ==========================================
# SAVE OUTPUT
# ==========================================
enriched_data["updated_at"] = str(datetime.now())

with open(OUTPUT_FILE, "w") as f:
    json.dump(enriched_data, f, indent=4)

# ==========================================
# STATUS
# ==========================================
print("\nBatch Completed!")

print(f"Processed IPs: {progress['last_ip_index']}")
print(f"Processed Domains: {progress['last_domain_index']}")

print(f"\nSleeping for {BREAK_TIME} seconds...\n")

time.sleep(BREAK_TIME)

print("Ready for next run!")