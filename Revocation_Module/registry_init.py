import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "Outputs")

REGISTRY_FILE = os.path.join(OUTPUT_DIR, "revocation_registry.json")
SNAPSHOT_FILE = os.path.join(OUTPUT_DIR, "revocation_registry_snapshot.json")

ISSUER_ID = "ISSUER-PDS-AP-001"
REGISTRY_ID = "REVREG-PDS-AP-001"


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main():
    registry = {
        "issuer_id": ISSUER_ID,
        "registry_id": REGISTRY_ID,
        "tree_type": "revoked_nonce_registry",
        "hash_type": "merkle-placeholder-v1",
        "state": {
            "root": "0x0",
            "version": 1,
            "updated_at": utc_now()
        },
        "revoked": []
    }

    snapshot = {
        "issuer_id": ISSUER_ID,
        "registry_id": REGISTRY_ID,
        "state": registry["state"]
    }

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print("Revocation registry initialized.")
    print(f"Registry file: {REGISTRY_FILE}")
    print(f"Snapshot file: {SNAPSHOT_FILE}")


if __name__ == "__main__":
    main()