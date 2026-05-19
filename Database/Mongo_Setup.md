## MongoDB & MongoDB Compass

### Why MongoDB?
- Threat data from different feeds has **inconsistent structure**
- MongoDB is a NoSQL database — it stores data as JSON-like documents
- No fixed schema needed, each document can have different fields
- Easy to query and filter by fields like `risk_score`, `type`, `ip`

### Why MongoDB Compass?
- It is a **visual interface** for MongoDB
- Without it you can only see data via terminal commands
- Compass lets you view, filter and verify your collected data visually
- Useful for checking if ingestion scripts are working correctly

### How we use it?

**MongoDB** stores every threat indicator collected from OSINT feeds:
```json
{
  "ip": "185.220.101.45",
  "type": "malware",
  "source": "AlienVault",
  "risk_score": 8,
  "last_seen": "2025-05-10"
}
```

**MongoDB Compass** is used to:
- View collected documents visually
- Verify deduplication is working
- Filter high risk indicators manually before automation is built

## install MongoDB Server

visit https://www.mongodb.com/ 
Go to Products > community-edition and click **Download free** button.
select your oprating system.

![MongoDB](screenshots/Mongo3.png)

install MongoDB Server

```bash
sudo dbkg -i mongodb-org-server_8.3.1_amd64.deb
```

start and check service

```bash
sudo systemctl enable mongod.service
sudo systemctl start mongod.service
sudo systemctl status mongod.service
```

Install Mongodb Compass

go to tool and click the Mongodb Compass (GUI)

![MongoDB](screenshots/Mongo4.png)