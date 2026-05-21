from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient("mongodb://localhost:27017/")
db = client["OSINT_Treat"]
collection = db["osint_data"]

def calculate_risk_score(obj):
    score = 0

    # Source points
    source = obj.get("source", "").lower()
    if "alienvault" in source:
        score += 2
    else:
        score += 1

    # Recency points
    added_at = obj.get("added_at")
    if added_at:
        if isinstance(added_at, str):
            added_at = datetime.fromisoformat(added_at)
        if added_at.tzinfo is None:
            added_at = added_at.replace(tzinfo=timezone.utc)
        days_ago = (datetime.now(timezone.utc) - added_at).days
        if days_ago <= 7:
            score += 3
        elif days_ago <= 30:
            score += 2
        else:
            score += 1

    # Default type score
    score += 2

    return min(score, 10)


# Loop through all 3 documents
for doc in collection.find():
    doc_id = doc["_id"]

    # --- Process IPs ---
    ips_array = doc.get("ips", [])
    updated_ips = []
    for ip_obj in ips_array:
        ip_obj["risk_score"] = calculate_risk_score(ip_obj)
        ip_obj["blocked"]    = False
        ip_obj["type"]       = "malware"
        updated_ips.append(ip_obj)

    # --- Process Domains ---
    domains_array = doc.get("domains", [])
    updated_domains = []
    for domain_obj in domains_array:
        domain_obj["risk_score"] = calculate_risk_score(domain_obj)
        domain_obj["blocked"]    = False
        domain_obj["type"]       = "malware"
        updated_domains.append(domain_obj)

    # --- Save back to MongoDB ---
    collection.update_one(
        {"_id": doc_id},
        {"$set": {
            "ips":     updated_ips,
            "domains": updated_domains
        }}
    )

    print(f"Updated document {doc_id} — IPs: {len(updated_ips)}, Domains: {len(updated_domains)}")

print("\nAll documents updated successfully.")