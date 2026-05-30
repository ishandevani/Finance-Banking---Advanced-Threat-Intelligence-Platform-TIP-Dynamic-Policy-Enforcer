from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Threat"]
collection = db["osint_threat"]

documents = collection.find()

for doc in documents:

    # ---------------- IPs ----------------
    if "ips" in doc:

        updated_ips = []

        for ip_data in doc["ips"]:

            malicious = ip_data.get("malicious_score", 0)
            suspicious = ip_data.get("suspicious_score", 0)
            reputation = ip_data.get("reputation", 0)

            # Risk score out of 10
            risk_score = (
                (malicious * 0.6) +
                (suspicious * 0.3)
            )

            # Bad reputation increases score
            if reputation < 0:
                risk_score += 1

            # Maximum score = 10
            risk_score = round(min(risk_score, 10), 1)

            # Severity
            if risk_score >= 8:
                severity = "critical"
            elif risk_score >= 6:
                severity = "high"
            elif risk_score >= 3:
                severity = "medium"
            else:
                severity = "low"

            ip_data["risk_score"] = risk_score
            ip_data["severity"] = severity

            updated_ips.append(ip_data)

        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"ips": updated_ips}}
        )

    # ---------------- Domains ----------------
    if "domains" in doc:

        updated_domains = []

        for domain_data in doc["domains"]:

            malicious = domain_data.get("malicious_score", 0)
            suspicious = domain_data.get("suspicious_score", 0)
            reputation = domain_data.get("reputation", 0)

            # Risk score out of 10
            risk_score = (
                (malicious * 0.6) +
                (suspicious * 0.3)
            )

            if reputation < 0:
                risk_score += 1

            # Maximum score = 10
            risk_score = round(min(risk_score, 10), 1)

            # Severity
            if risk_score >= 8:
                severity = "critical"
            elif risk_score >= 6:
                severity = "high"
            elif risk_score >= 3:
                severity = "medium"
            else:
                severity = "low"

            domain_data["risk_score"] = risk_score
            domain_data["severity"] = severity

            updated_domains.append(domain_data)

        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"domains": updated_domains}}
        )

print("Risk scores added successfully!")