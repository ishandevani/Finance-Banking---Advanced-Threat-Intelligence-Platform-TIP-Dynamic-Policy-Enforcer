"""
mongo_to_es.py
--------------
Syncs MongoDB (Threat DB) → Elasticsearch every 15 minutes.

Collections handled:
  1. osint_threat  → index: threat-osint
  2. blocked_ips   → index: threat-blocked-ips

Logic:
  - Deduplicates by IP or domain (uses deterministic ES _id)
  - Detects updates via updated_at / blocked_at timestamps
  - Detects deletes: removes ES docs no longer in MongoDB
  - Runs forever, syncs every 15 minutes
"""

import time
import hashlib
import logging
from datetime import datetime, timezone

from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers, NotFoundError

# ─── CONFIG ───────────────────────────────────────────────────────────────────

MONGO_URI        = "mongodb://localhost:27017"   # Change to Tailscale IP if remote
MONGO_DB         = "Threat"

ES_HOST          = "http://localhost:9200"        # Change to Tailscale IP if remote
ES_USER          = "elastic"
ES_PASS          = "Enter your password"

INDEX_OSINT      = "threat-osint"
INDEX_BLOCKED    = "threat-blocked-ips"

SYNC_INTERVAL    = 15 * 60  # 15 minutes in seconds

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def parse_date(value):
    """Normalize date strings to ISO format for Elasticsearch."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value.replace(" ", "T")
    return str(value)

def make_id(value: str) -> str:
    """
    Create a deterministic Elasticsearch _id from an IP or domain.
    Same IP/domain always maps to same _id — this is how deduplication works.
    """
    return hashlib.md5(value.strip().lower().encode()).hexdigest()

# ─── ELASTICSEARCH SETUP ──────────────────────────────────────────────────────

def get_es_client():
    return Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS))

def create_indices(es):
    """Create ES indices with proper mappings if they don't exist."""

    osint_mapping = {
        "mappings": {
            "properties": {
                "record_type":      {"type": "keyword"},
                "ip":               {"type": "ip"},
                "domain":           {"type": "keyword"},
                "source":           {"type": "keyword"},
                "country":          {"type": "keyword"},
                "asn":              {"type": "long"},
                "malicious_score":  {"type": "integer"},
                "suspicious_score": {"type": "integer"},
                "risk_score":       {"type": "float"},
                "severity":         {"type": "keyword"},
                "reputation":       {"type": "integer"},
                "added_at":         {"type": "date"},
                "generated_at":     {"type": "date"},
                "ingested_at":      {"type": "date"},
                "updated_at":       {"type": "date"}
            }
        }
    }

    blocked_mapping = {
        "mappings": {
            "properties": {
                "ip":           {"type": "ip"},
                "risk_score":   {"type": "float"},
                "status":       {"type": "keyword"},
                "blocked_at":   {"type": "date"},
                "unblocked_at": {"type": "date"},
                "ingested_at":  {"type": "date"}
            }
        }
    }

    for index, mapping in [(INDEX_OSINT, osint_mapping), (INDEX_BLOCKED, blocked_mapping)]:
        if not es.indices.exists(index=index):
            es.indices.create(index=index, body=mapping)
            log.info(f"Created index: {index}")
        else:
            log.info(f"Index already exists: {index}")

# ─── OSINT THREAT SYNC ────────────────────────────────────────────────────────

def get_existing_es_ids(es, index):
    """
    Fetch all _ids currently in an ES index.
    Used to detect deletes (docs in ES but no longer in MongoDB).
    """
    ids = set()
    try:
        resp = helpers.scan(
            es,
            index=index,
            query={"query": {"match_all": {}}},
            _source=False  # Only need _id, not full doc
        )
        for hit in resp:
            ids.add(hit["_id"])
    except Exception as e:
        log.warning(f"Could not fetch existing IDs from {index}: {e}")
    return ids

def sync_osint(es, collection):
    """
    Sync osint_threat collection → threat-osint index.
    - Upserts all IP and domain records
    - Deduplicates by IP/domain (deterministic _id)
    - Detects and removes deleted records
    """
    log.info("Syncing osint_threat...")

    # Track all IDs we see in MongoDB this run
    mongo_ids = set()
    actions   = []
    now       = now_utc()

    ip_count     = 0
    domain_count = 0

    for doc in collection.find():
        generated_at = parse_date(doc.get("generated_at"))
        updated_at   = parse_date(doc.get("updated_at"))

        # ── IPs ──
        for entry in doc.get("ips", []):
            ip = entry.get("ip")
            if not ip:
                continue

            doc_id = make_id(f"ip:{ip}")
            mongo_ids.add(doc_id)
            ip_count += 1

            actions.append({
                "_op_type": "index",   # index = upsert (overwrites if exists)
                "_index":   INDEX_OSINT,
                "_id":      doc_id,
                "_source": {
                    "record_type":      "ip",
                    "ip":               ip,
                    "source":           entry.get("source"),
                    "country":          entry.get("country"),
                    "asn":              entry.get("asn"),
                    "malicious_score":  entry.get("malicious_score"),
                    "suspicious_score": entry.get("suspicious_score"),
                    "risk_score":       entry.get("risk_score", 0),
                    "severity":         entry.get("severity", "unknown"),
                    "reputation":       entry.get("reputation"),
                    "added_at":         parse_date(entry.get("added_at")),
                    "generated_at":     generated_at,
                    "updated_at":       updated_at,
                    "ingested_at":      now
                }
            })

        # ── Domains ──
        for entry in doc.get("domains", []):
            domain = entry.get("domain")
            if not domain:
                continue

            doc_id = make_id(f"domain:{domain}")
            mongo_ids.add(doc_id)
            domain_count += 1

            actions.append({
                "_op_type": "index",
                "_index":   INDEX_OSINT,
                "_id":      doc_id,
                "_source": {
                    "record_type":      "domain",
                    "domain":           domain,
                    "source":           entry.get("source"),
                    "malicious_score":  entry.get("malicious_score"),
                    "suspicious_score": entry.get("suspicious_score"),
                    "risk_score":       entry.get("risk_score", 0),
                    "severity":         entry.get("severity", "unknown"),
                    "reputation":       entry.get("reputation"),
                    "added_at":         parse_date(entry.get("added_at")),
                    "generated_at":     generated_at,
                    "updated_at":       updated_at,
                    "ingested_at":      now
                }
            })

    # ── Upsert all records ──
    if actions:
        success, failed = helpers.bulk(
            es, actions,
            raise_on_error=False,
            stats_only=False
        )
        log.info(f"osint_threat → Indexed: {success} | Failed: {len(failed) if isinstance(failed, list) else failed}")
        log.info(f"  IPs: {ip_count} | Domains: {domain_count}")
    else:
        log.info("osint_threat → No records found in MongoDB")

    # ── Delete records removed from MongoDB ──
    es_ids      = get_existing_es_ids(es, INDEX_OSINT)
    deleted_ids = es_ids - mongo_ids

    if deleted_ids:
        delete_actions = [
            {"_op_type": "delete", "_index": INDEX_OSINT, "_id": doc_id}
            for doc_id in deleted_ids
        ]
        del_success, del_failed = helpers.bulk(
            es, delete_actions,
            raise_on_error=False,
            stats_only=False
        )
        log.info(f"osint_threat → Deleted {del_success} stale records from Elasticsearch")
    else:
        log.info("osint_threat → No stale records to delete")

# ─── BLOCKED IPS SYNC ─────────────────────────────────────────────────────────

def sync_blocked_ips(es, collection):
    """
    Sync blocked_ips collection → threat-blocked-ips index.
    - Upserts all blocked/unblocked IP records
    - Deduplicates by IP
    - Detects and removes deleted records
    """
    log.info("Syncing blocked_ips...")

    mongo_ids = set()
    actions   = []
    now       = now_utc()
    count     = 0

    for doc in collection.find():
        ip = doc.get("ip")
        if not ip:
            continue

        doc_id = make_id(f"blocked:{ip}")
        mongo_ids.add(doc_id)
        count += 1

        actions.append({
            "_op_type": "index",
            "_index":   INDEX_BLOCKED,
            "_id":      doc_id,
            "_source": {
                "ip":           ip,
                "risk_score":   doc.get("risk_score"),
                "status":       doc.get("status", "unknown"),
                "blocked_at":   parse_date(doc.get("blocked_at")),
                "unblocked_at": parse_date(doc.get("unblocked_at")),
                "ingested_at":  now
            }
        })

    if actions:
        success, failed = helpers.bulk(
            es, actions,
            raise_on_error=False,
            stats_only=False
        )
        log.info(f"blocked_ips → Indexed: {success} | Failed: {len(failed) if isinstance(failed, list) else failed}")
        log.info(f"  Total blocked IP records: {count}")
    else:
        log.info("blocked_ips → No records found in MongoDB")

    # ── Delete records removed from MongoDB ──
    es_ids      = get_existing_es_ids(es, INDEX_BLOCKED)
    deleted_ids = es_ids - mongo_ids

    if deleted_ids:
        delete_actions = [
            {"_op_type": "delete", "_index": INDEX_BLOCKED, "_id": doc_id}
            for doc_id in deleted_ids
        ]
        del_success, _ = helpers.bulk(
            es, delete_actions,
            raise_on_error=False,
            stats_only=False
        )
        log.info(f"blocked_ips → Deleted {del_success} stale records from Elasticsearch")
    else:
        log.info("blocked_ips → No stale records to delete")

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────

def run_sync():
    """Single sync run — connects, syncs both collections, disconnects."""
    log.info("=" * 60)
    log.info("Starting sync run...")

    try:
        # Connect MongoDB
        mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo.server_info()  # Raises if can't connect
        db = mongo[MONGO_DB]
        log.info(f"MongoDB connected: {MONGO_URI}")

        # Connect Elasticsearch
        es = get_es_client()
        cluster_name = es.info()["cluster_name"]
        log.info(f"Elasticsearch connected: {cluster_name}")

        # Ensure indices exist
        create_indices(es)

        # Sync both collections
        sync_osint(es, db["osint_threat"])
        sync_blocked_ips(es, db["blocked_ips"])

        log.info("Sync run complete.")

    except Exception as e:
        log.error(f"Sync failed: {e}")

    finally:
        try:
            mongo.close()
        except:
            pass

def main():
    log.info("mongo_to_es.py started — syncing every 15 minutes")
    log.info(f"MongoDB : {MONGO_URI}")
    log.info(f"ES Host : {ES_HOST}")

    while True:
        run_sync()
        log.info(f"Next sync in {SYNC_INTERVAL // 60} minutes...")
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()