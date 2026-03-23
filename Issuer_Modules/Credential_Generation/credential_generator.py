import csv
import json
import os
import secrets
from datetime import date, timedelta


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

CITIZENS_CSV = os.path.join(PROJECT_ROOT, "Issuer_Modules", "Mock_Data", "citizens.csv")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "Outputs", "credentials")
INDEX_DIR = os.path.join(BASE_DIR, "Outputs", "index")
INDEX_FILE = os.path.join(INDEX_DIR, "citizen_credential_index.json")

ISSUER_ID = "ISSUER-PDS-AP-001"
REGISTRY_ID = "REVREG-PDS-AP-001"


def parse_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def generate_revocation_nonce():
    # 128-bit nonce
    return "0x" + secrets.token_hex(16)


def ensure_output_dirs():
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)


def normalize_row(row):
    return {
        "citizen_id": int(row["citizen_id"]),
        "name": row["name"],
        "age": int(row["age"]),
        "gender": row["gender"],
        "state_code": row["state_code"],
        "district_code": int(row["district_code"]),
        "district_name": row["district_name"],
        "income_value": int(row["income_value"]),
        "income_source": row["income_source"],
        "household_size": int(row["household_size"]),
        "vehicle_type": row["vehicle_type"],
        "is_government_employee": parse_bool(row["is_government_employee"]),
        "identity_verified": parse_bool(row["identity_verified"]),
        "residency_verified": parse_bool(row["residency_verified"]),
    }


def build_credential(citizen):
    today = date.today()

    credential_id = f"CRED-{citizen['citizen_id']:04d}"
    revocation_nonce = generate_revocation_nonce()

    credential = {
        "credential_id": credential_id,
        "issuer_id": ISSUER_ID,
        "citizen_id": citizen["citizen_id"],
        "issued_at": today.isoformat(),
        "valid_until": (today + timedelta(days=365)).isoformat(),
        "claims": {
            "name": citizen["name"],
            "age": citizen["age"],
            "gender": citizen["gender"],
            "state_code": citizen["state_code"],
            "district_code": citizen["district_code"],
            "district_name": citizen["district_name"],
            "income_value": citizen["income_value"],
            "income_source": citizen["income_source"],
            "household_size": citizen["household_size"],
            "vehicle_type": citizen["vehicle_type"],
            "is_government_employee": citizen["is_government_employee"],
            "identity_verified": citizen["identity_verified"],
            "residency_verified": citizen["residency_verified"],
        },
        "revocation": {
            "registry_id": REGISTRY_ID,
            "revocation_nonce": revocation_nonce,
            "method": "merkle-revocation-v1",
        },
        "status": "active",
    }

    return credential


def save_credential(credential):
    output_path = os.path.join(CREDENTIALS_DIR, f"{credential['credential_id']}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(credential, f, indent=2)


def main():
    ensure_output_dirs()

    index = {
        "issuer_id": ISSUER_ID,
        "registry_id": REGISTRY_ID,
        "entries": []
    }

    with open(CITIZENS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            citizen = normalize_row(row)
            credential = build_credential(citizen)
            save_credential(credential)

            index["entries"].append({
                "citizen_id": citizen["citizen_id"],
                "credential_id": credential["credential_id"],
                "revocation_nonce": credential["revocation"]["revocation_nonce"],
                "issued_at": credential["issued_at"],
            })

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"Credentials written to: {CREDENTIALS_DIR}")
    print(f"Index written to: {INDEX_FILE}")
    print(f"Total credentials generated: {len(index['entries'])}")


if __name__ == "__main__":
    main()