import requests
import json
import os
from datetime import datetime

# ============================================
# API KEYS
# ============================================

OTX_API_KEY = "API Key"
VT_API_KEY = "API Key"
ABUSEIPDB_API_KEY = "API Key"

OUTPUT_FILE = "osint_threat_feed.json"

# ============================================
# LOAD EXISTING JSON
# ============================================

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r") as f:
        threat_data = json.load(f)
else:
    threat_data = {
        "generated_at": "",
        "ips": [],
        "domains": []
    }

# ============================================
# TRACK EXISTING VALUES
# ============================================

existing_ips = set(item["ip"] for item in threat_data["ips"])
existing_domains = set(item["domain"] for item in threat_data["domains"])

# ============================================
# ADD NEW DATA
# ============================================

def add_ip(source, ip):
    if ip not in existing_ips:
        threat_data["ips"].append({
            "source": source,
            "ip": ip,
            "added_at": datetime.utcnow().isoformat()
        })
        existing_ips.add(ip)

def add_domain(source, domain):
    if domain not in existing_domains:
        threat_data["domains"].append({
            "source": source,
            "domain": domain,
            "added_at": datetime.utcnow().isoformat()
        })
        existing_domains.add(domain)

# ============================================
# ALIENVAULT OTX
# ============================================

def fetch_otx():
    print("[+] Fetching OTX...")

    headers = {
        "X-OTX-API-KEY": OTX_API_KEY
    }

    page = 1

    while True:

        url = f"https://otx.alienvault.com/api/v1/pulses/subscribed?page={page}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("[-] OTX Error")
            break

        data = response.json()

        results = data.get("results", [])

        if not results:
            break

        for pulse in results:

            for indicator in pulse.get("indicators", []):

                indicator_type = indicator.get("type")
                indicator_value = indicator.get("indicator")

                if indicator_type in ["IPv4", "IPv6"]:
                    add_ip("AlienVault OTX", indicator_value)

                elif indicator_type == "domain":
                    add_domain("AlienVault OTX", indicator_value)

        print(f"[+] OTX Page {page} completed")

        page += 1

# ============================================
# ABUSEIPDB
# ============================================

def fetch_abuseipdb():
    print("[+] Fetching AbuseIPDB...")

    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    for page in range(1, 6):

        params = {
            "limit": 500,
            "page": page
        }

        url = "https://api.abuseipdb.com/api/v2/blacklist"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print("[-] AbuseIPDB Error")
            break

        data = response.json()

        for item in data.get("data", []):

            ip = item.get("ipAddress")

            if ip:
                add_ip("AbuseIPDB", ip)

        print(f"[+] AbuseIPDB Page {page} completed")

# ============================================
# VIRUSTOTAL
# ============================================

def fetch_virustotal():
    print("[+] Fetching VirusTotal...")

    headers = {
        "x-apikey": VT_API_KEY
    }

    cursor = None

    for _ in range(5):

        params = {
            "query": "type:domain OR type:ip",
            "limit": 200
        }

        if cursor:
            params["cursor"] = cursor

        url = "https://www.virustotal.com/api/v3/intelligence/search"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print("[-] VirusTotal Error")
            break

        data = response.json()

        for item in data.get("data", []):

            item_type = item.get("type")
            item_id = item.get("id")

            if item_type == "ip_address":
                add_ip("VirusTotal", item_id)

            elif item_type == "domain":
                add_domain("VirusTotal", item_id)

        cursor = data.get("meta", {}).get("cursor")

        print("[+] VirusTotal page completed")

        if not cursor:
            break

# ============================================
# SAVE FILE
# ============================================

def save_json():

    threat_data["generated_at"] = datetime.utcnow().isoformat()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(threat_data, f, indent=4)

    print(f"[+] Saved to {OUTPUT_FILE}")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":

    fetch_otx()
    fetch_abuseipdb()
    fetch_virustotal()

    save_json()

    print("\n========== SUMMARY ==========")
    print(f"IPs     : {len(threat_data['ips'])}")
    print(f"Domains : {len(threat_data['domains'])}")
