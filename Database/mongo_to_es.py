from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "Threat"
MONGO_COLLECTION = "osint_threat"
ES_HOST = "http://localhost:9200"
ES_USER = "elastic"
ES_PASS = "Enter Your Password" #Enter your Elastcsearch password
ES_INDEX = "threat-osint"

def parse_date(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.replace(" ", "T")
    return value

def get_es_client():
    return Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS))

def create_index(es):
    if es.indices.exists(index=ES_INDEX):
        print(f"Index '{ES_INDEX}' already exists, skipping creation.")
        return
    mapping = {
        "mappings": {
            "properties": {
                "ip":               {"type": "ip"},
                "domain":           {"type": "keyword"},
                "record_type":      {"type": "keyword"},
                "source":           {"type": "keyword"},
                "country":          {"type": "keyword"},
                "asn":              {"type": "long"},
                "malicious_score":  {"type": "integer"},
                "suspicious_score": {"type": "integer"},
                "reputation":       {"type": "integer"},
                "added_at":         {"type": "date"},
                "generated_at":     {"type": "date"},
                "ingested_at":      {"type": "date"}
            }
        }
    }
    es.indices.create(index=ES_INDEX, body=mapping)
    print(f"Index '{ES_INDEX}' created.")

def generate_docs(collection):
    ip_count = 0
    domain_count = 0

    for doc in collection.find():
        generated_at = parse_date(doc.get("generated_at"))
        now = datetime.now(timezone.utc).isoformat()

        # process IPs
        for entry in doc.get("ips", []):
            if entry.get("ip") is None:
                continue
            ip_count += 1
            yield {
                "_t(f"ES cluster: {es.info()['cluster_name']}")
    create_index(es)
    print("Syncing data...")
    success, failed = helpers.bulk(es, generate_docs(collection), raise_on_error=False, stats_only=False)
    print(f"Indexed: {success} | Failed: {len(failed) if isinstance(failed, list) else failed}")

if __name__ == "__main__":
    main()
