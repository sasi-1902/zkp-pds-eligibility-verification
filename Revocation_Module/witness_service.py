import json
import os
import sys

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

INPUT_JSON_DIR = os.path.join(
    PROJECT_ROOT,
    "Issuer_Modules",
    "Credential_Generation",
    "Outputs",
    "input_json"
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
WITNESSES_DIR = os.path.join(BASE_DIR, "Outputs", "witnesses")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    if len(sys.argv) != 2:
        print("Usage: python Revocation_Module/witness_service.py <citizen_id>")
        sys.exit(1)

    citizen_id = int(sys.argv[1])

    os.makedirs(WITNESSES_DIR, exist_ok=True)

    index_data = load_json(INDEX_FILE)
    registry = load_json(REGISTRY_FILE)
    snapshot = load_json(SNAPSHOT_FILE)

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
    claims = credential_data["claims"]

    os.makedirs(INPUT_JSON_DIR, exist_ok=True)
    
    is_revoked = False
    revoked_record = None

    for item in registry["revoked"]:
        if item["revocation_nonce"] == revocation_nonce:
            is_revoked = True
            revoked_record = item
            break

    input_data = {
        "citizen_id": citizen_id,
        "credential_id": credential_id,

        # CLAIMS (for circuit)
        "income_value": claims["income_value"],
        "household_size": claims["household_size"],
        "district_code": claims["district_code"],
        "is_government_employee": claims["is_government_employee"],
        "identity_verified": claims["identity_verified"],
        "residency_verified": claims["residency_verified"],

        # REVOCATION
        "revocation_nonce": revocation_nonce,
        "revocation_root": snapshot["state"]["root"],
        "revocation_root_version": snapshot["state"]["version"],
        "revocation_status_expected": "revoked" if is_revoked else "not_revoked"
    }
    
    input_file = os.path.join(INPUT_JSON_DIR, f"{credential_id}_input.json")
    save_json(input_file, input_data)
    print(f"Input file written: {input_file}")

    witness_data = {
        "citizen_id": citizen_id,
        "credential_id": credential_id,
        "revocation_nonce": revocation_nonce,
        "revocation_status": "revoked" if is_revoked else "not_revoked",
        "registry_state": {
            "root": snapshot["state"]["root"],
            "version": snapshot["state"]["version"],
            "updated_at": snapshot["state"]["updated_at"]
        },
        "witness_type": "placeholder-status-check-v1",
        "smt_witness": None
    }

    if revoked_record:
        witness_data["revoked_at"] = revoked_record["revoked_at"]
        witness_data["reason"] = revoked_record["reason"]

    witness_file = os.path.join(WITNESSES_DIR, f"{credential_id}_witness.json")
    save_json(witness_file, witness_data)

    print(f"Witness/status file written: {witness_file}")
    print(f"Credential: {credential_id}")
    print(f"Revocation status: {witness_data['revocation_status']}")


if __name__ == "__main__":
    main()