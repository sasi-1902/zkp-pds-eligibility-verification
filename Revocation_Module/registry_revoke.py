import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

INDEX_FILE = os.path.join(
    PROJECT_ROOT,
    "Issuer_Modules",
    "Credential_Generation",
    "Outputs",
    "index",
    "citizen_credential_index.json"
)

CREDENTIALS_DIR = os.path.join(
    PROJECT_ROOT,
    "Issuer_Modules",
    "Credential_Generation",
    "Outputs",
    "credentials"
)

REGISTRY_FILE = os.path.join(BASE_DIR, "Outputs", "revocation_registry.json")
SNAPSHOT_FILE = os.path.join(BASE_DIR, "Outputs", "revocation_registry_snapshot.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    if len(sys.argv) != 2:
        print("Usage: python Revocation_Module/registry_revoke.py <citizen_id>")
        sys.exit(1)

    citizen_id = int(sys.argv[1])

    index_data = load_json(INDEX_FILE)
    registry = load_json(REGISTRY_FILE)

    match = None
    for entry in index_data["entries"]:
        if entry["citizen_id"] == citizen_id:
            match = entry
            break

    if match is None:
        print(f"No credential found for citizen_id={citizen_id}")
        sys.exit(1)

    credential_id = match["credential_id"]
    revocation_nonce = match["revocation_nonce"]
    credential_file = os.path.join(CREDENTIALS_DIR, f"{credential_id}.json")
    credential_data = load_json(credential_file)


    for item in registry["revoked"]:
        if item["revocation_nonce"] == revocation_nonce:
            print(f"Credential {credential_id} is already revoked.")
            return
    if credential_data.get("status") == "revoked":
        print(f"Credential {credential_id} is already marked revoked in credential file.")
        return

    registry["revoked"].append({
        "citizen_id": citizen_id,
        "credential_id": credential_id,
        "revocation_nonce": revocation_nonce,
        "revoked_at": utc_now(),
        "reason": "manual_test_revocation"
    })
    credential_data["status"] = "revoked"
    save_json(credential_file, credential_data)

    registry["state"]["version"] += 1
    registry["state"]["updated_at"] = utc_now()

    # Placeholder root for now
    registry["state"]["root"] = hex(len(registry["revoked"]))

    snapshot = {
        "issuer_id": registry["issuer_id"],
        "registry_id": registry["registry_id"],
        "state": registry["state"]
    }

    save_json(REGISTRY_FILE, registry)
    save_json(SNAPSHOT_FILE, snapshot)

    print(f"Revoked credential {credential_id} for citizen_id={citizen_id}")
    print(f"New root: {registry['state']['root']}")
    print(f"New version: {registry['state']['version']}")


if __name__ == "__main__":
    main()