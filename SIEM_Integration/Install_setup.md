# =========================================
# ELK Stack Installation & Setup Script
# Ubuntu 22.04 / 24.04
# =========================================

# Update System
sudo apt update && sudo apt upgrade -y

# Install Required Packages
sudo apt install apt-transport-https wget curl gnupg -y

# Import Elastic GPG Key
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | \
sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg

# Add Elastic Repository
echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | \
sudo tee /etc/apt/sources.list.d/elastic-8.x.list

# Update Repository
sudo apt update

# Install Elasticsearch
sudo apt install elasticsearch -y

# Configure Elasticsearch
sudo bash -c 'cat > /etc/elasticsearch/elasticsearch.yml <<EOF
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
EOF'

# Enable & Start Elasticsearch
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Check Elasticsearch Status
sudo systemctl status elasticsearch --no-pager

# Test Elasticsearch
curl localhost:9200

# Install Kibana
sudo apt install kibana -y

# Configure Kibana
sudo bash -c 'cat > /etc/kibana/kibana.yml <<EOF
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
EOF'

# Enable & Start Kibana
sudo systemctl enable kibana
sudo systemctl start kibana

# Check Kibana Status
sudo systemctl status kibana --no-pager

# Install Logstash
sudo apt install logstash -y

# Check Logstash Version
/usr/share/logstash/bin/logstash --version

# Enable & Start Logstash
sudo systemctl enable logstash
sudo systemctl start logstash

# Check Logstash Status
sudo systemctl status logstash --no-pager

# Allow Firewall Ports
sudo ufw allow 9200
sudo ufw allow 5601

# Restart All Services
sudo systemctl restart elasticsearch
sudo systemctl restart kibana
sudo systemctl restart logstash

# =========================================
# Access Kibana
# =========================================
# Open Browser:
# http://YOUR-IP:5601
#
# Example:
# http://192.168.1.10:5601
# =========================================

![ELK.png](/screenshots/ELK.png)