# sudo python3 Rollback.py <enter IP>

import sys
import subprocess
from datetime import datetime
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Threat"]

blocked_collection = db["blocked_ips"]

# Check IP argument
if len(sys.argv) != 2:
    print("Usage: python3 rollback.py <IP_ADDRESS>")
    sys.exit(1)

ip = sys.argv[1]

# Verify IP exists in blocked collection
record = blocked_collection.find_one({
    "ip": ip,
    "status": "blocked"
})

if not record:
    print(f"[!] IP {ip} not found or already unblocked")
    sys.exit(1)

try:
    # Remove UFW rule
    subprocess.run(
        ["sudo", "ufw", "delete", "deny", "from", ip],
        check=True
    )

    print(f"[+] Firewall rule removed for {ip}")

    # Update MongoDB record
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
    print(f"[-] Failed to remove firewall rule")
except Exception as e:
    print(f"[-] Error: {e}")
