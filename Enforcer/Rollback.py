import sys
import subprocess
from datetime import datetime
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Threat"]

blocked_collection = db["blocked_ips"]

# Check command-line argument
if len(sys.argv) != 2:
    print("Usage: python3 rollback.py <IP_ADDRESS>")
    sys.exit(1)

ip = sys.argv[1]

# Verify IP exists and is currently blocked
record = blocked_collection.find_one({
    "ip": ip,
    "status": "blocked"
})

if not record:
    print(f"[!] IP {ip} not found or already unblocked")
    sys.exit(1)

try:
    # Remove iptables rule
    subprocess.run(
        [
            "sudo",
            "iptables",
            "-D",
            "INPUT",
            "-s",
            ip,
            "-j",
            "DROP"
        ],
        check=True
    )

    print(f"[+] Firewall rule removed for {ip}")

    # Update MongoDB status
    blocked_collection.update_one(
        {"ip": ip},
        {
            "$set": {
                "status": "unblocked",
                "unblocked_at": datetime.utcnow()
            }
        }
    )

    print(f"[+] MongoDB updated")
    print(f"[+] IP {ip} successfully unblocked")

except subprocess.CalledProcessError:
    print(f"[-] Firewall rule not found or already removed")

except Exception as e:
    print(f"[-] Error: {e}")
