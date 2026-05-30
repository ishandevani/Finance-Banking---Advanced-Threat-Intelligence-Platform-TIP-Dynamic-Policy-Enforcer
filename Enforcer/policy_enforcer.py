import daemon
import time
import subprocess
from datetime import datetime
from pymongo import MongoClient

RISK_THRESHOLD = 8

client = MongoClient("mongodb://localhost:27017/")
db = client["Threat"]

threat_collection = db["osint_threat"]
blocked_collection = db["blocked_ips"]


def is_already_blocked(ip):
    return blocked_collection.find_one({"ip": ip}) is not None


def firewall_rule_exists(ip):
    result = subprocess.run(
        ["iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.returncode == 0


def block_ip(ip, risk_score):
    try:
        subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )

        blocked_collection.insert_one({
            "ip": ip,
            "risk_score": risk_score,
            "status": "blocked",
            "blocked_at": datetime.utcnow()
        })

    except Exception as e:
        print(e)


def monitor_threats():

    while True:

        documents = threat_collection.find()

        for doc in documents:

            if "ips" not in doc:
                continue

            for threat in doc["ips"]:

                ip = threat.get("ip")
                risk_score = threat.get("risk_score", 0)

                if not ip:
                    continue

                if risk_score >= RISK_THRESHOLD:

                    if is_already_blocked(ip):
                        continue

                    if firewall_rule_exists(ip):
                        continue

                    block_ip(ip, risk_score)

        time.sleep(60)


with daemon.DaemonContext():
    monitor_threats()