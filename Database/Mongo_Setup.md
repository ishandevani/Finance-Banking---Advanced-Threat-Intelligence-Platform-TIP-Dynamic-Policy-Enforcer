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

## Install MongoDB Server

Visit https://www.mongodb.com/ and go to Products > Community Edition, then click the Download Free button and select your operating system.

![MongoDB](./screenshots/Mongo3.png)

Install MongoDB Server.

```bash
sudo dpkg -i mongodb-org-server_8.3.1_amd64.deb
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

install MongoDB Compass

```bash
sudo dpkg -i mongodb-compass_1.49.6_amd64.deb
```

Once MongoDB Compass is installed, open it and connect it to the MongoDB server. By default, it connects to **localhost:27017**.

![MongoDB](screenshots/MongoDB1.png)

Create a database named osint_threat and set the collection name as osint_threat.

![MongoDB](screenshots/MongoDB2.png)

we uplode json file into MongoDB.