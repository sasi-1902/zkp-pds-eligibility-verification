import csv
import random
from faker import Faker

fake = Faker("en_IN")

NUM_CITIZENS = 20
OUTPUT_FILE = "citizens.csv"
TEST_OUTPUT_FILE = "test_citizens.csv"
STATE_CODE = "AP"

DISTRICT_REGISTRY = {
    "101": "Chittoor",
    "102": "East Godavari",
    "103": "Guntur",
    "104": "Krishna",
    "105": "Kurnool",
    "106": "Prakasam",
    "107": "Srikakulam",
    "108": "Visakhapatnam",
    "109": "Vizianagaram",
    "110": "West Godavari",
}

DISTRICT_CODES = list(DISTRICT_REGISTRY.keys())

INCOME_SOURCES = [
    "Government",
    "Private Salaried",
    "Self-Employed",
    "Farmer",
    "Daily Wage Worker",
    "Pensioner",
    "Unemployed",
    "Homemaker",
]

NON_GOVERNMENT_SOURCES = [
    "Private Salaried",
    "Self-Employed",
    "Farmer",
    "Daily Wage Worker",
    "Pensioner",
    "Unemployed",
    "Homemaker",
]

VEHICLE_TYPES = ["none", "Two Wheeler", "Four Wheeler"]
GENDERS = ["Male", "Female"]

INCOME_THRESHOLD = 100000

NON_ELIGIBLE_MODES = [
    "income_over",
    "income_over",
    "identity_fail",
    "residency_fail",
    "four_wheeler",
    "government_employee",
    "income_and_government",
    "four_wheeler_and_income",
    "identity_and_residency",
    "income_over",
]


def pick_district():
    code = random.choice(DISTRICT_CODES)
    return code, DISTRICT_REGISTRY[code]


def pick_vehicle(exclude_four_wheeler=False):
    if exclude_four_wheeler:
        return random.choice(["none", "Two Wheeler"])
    return random.choice(VEHICLE_TYPES)


def generate_name_by_gender(gender):
    if gender == "Male":
        return fake.name_male()
    return fake.name_female()


def generate_age(income_source):
    if income_source == "Pensioner":
        return random.randint(60, 70)
    return random.randint(18, 59)


def base_citizen(citizen_id, income_source=None):
    district_code, district_name = pick_district()

    if income_source is None:
        income_source = random.choice(INCOME_SOURCES)

    gender = random.choice(GENDERS)
    name = generate_name_by_gender(gender)
    age = generate_age(income_source)

    return {
        "citizen_id": citizen_id,
        "name": name,
        "age": age,
        "gender": gender,
        "state_code": STATE_CODE,
        "district_code": district_code,
        "district_name": district_name,
        "income_value": random.randint(15000, 200000),
        "income_source": income_source,
        "household_size": random.randint(1, 10),
        "vehicle_type": pick_vehicle(),
        "is_government_employee": income_source == "Government",
        "identity_verified": random.choice([True, False]),
        "residency_verified": random.choice([True, False]),
    }


def generate_eligible_citizen(citizen_id):
    income_source = random.choice(NON_GOVERNMENT_SOURCES)
    citizen = base_citizen(citizen_id, income_source=income_source)

    citizen["income_value"] = random.randint(15000, INCOME_THRESHOLD)
    citizen["vehicle_type"] = pick_vehicle(exclude_four_wheeler=True)
    citizen["is_government_employee"] = False
    citizen["identity_verified"] = True
    citizen["residency_verified"] = True
    citizen["expected_eligibility"] = "Eligible"

    return citizen


def generate_non_eligible_citizen(citizen_id, failure_mode):
    income_source = random.choice(NON_GOVERNMENT_SOURCES)
    citizen = base_citizen(citizen_id, income_source=income_source)

    # Start from an eligible-style baseline
    citizen["income_value"] = random.randint(15000, INCOME_THRESHOLD)
    citizen["vehicle_type"] = pick_vehicle(exclude_four_wheeler=True)
    citizen["is_government_employee"] = False
    citizen["identity_verified"] = True
    citizen["residency_verified"] = True

    if failure_mode == "income_over":
        citizen["income_value"] = random.randint(INCOME_THRESHOLD + 1, 200000)

    elif failure_mode == "identity_fail":
        citizen["identity_verified"] = False

    elif failure_mode == "residency_fail":
        citizen["residency_verified"] = False

    elif failure_mode == "four_wheeler":
        citizen["vehicle_type"] = "Four Wheeler"

    elif failure_mode == "government_employee":
        citizen["income_source"] = "Government"
        citizen["is_government_employee"] = True
        citizen["age"] = generate_age("Government")

    elif failure_mode == "income_and_government":
        citizen["income_value"] = random.randint(INCOME_THRESHOLD + 1, 200000)
        citizen["income_source"] = "Government"
        citizen["is_government_employee"] = True
        citizen["age"] = generate_age("Government")

    elif failure_mode == "four_wheeler_and_income":
        citizen["vehicle_type"] = "Four Wheeler"
        citizen["income_value"] = random.randint(INCOME_THRESHOLD + 1, 200000)

    elif failure_mode == "identity_and_residency":
        citizen["identity_verified"] = False
        citizen["residency_verified"] = False

    citizen["expected_eligibility"] = "Not Eligible"
    return citizen


def main():
    rows = []

    # 10 eligible citizens
    rows.extend(generate_eligible_citizen(i) for i in range(1, 11))

    # 10 non-eligible citizens
    failure_modes = NON_ELIGIBLE_MODES.copy()
    random.shuffle(failure_modes)

    for i, mode in enumerate(failure_modes, start=11):
        rows.append(generate_non_eligible_citizen(i, mode))

    # Shuffle records so they are mixed
    random.shuffle(rows)

    # Reassign IDs after shuffle
    for idx, row in enumerate(rows, start=1):
        row["citizen_id"] = idx

    main_fieldnames = [
        "citizen_id",
        "name",
        "age",
        "gender",
        "state_code",
        "district_code",
        "district_name",
        "income_value",
        "income_source",
        "household_size",
        "vehicle_type",
        "is_government_employee",
        "identity_verified",
        "residency_verified",
    ]

    test_fieldnames = main_fieldnames + ["expected_eligibility"]

    # Write citizens.csv without eligibility label
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=main_fieldnames)
        writer.writeheader()
        for row in rows:
            clean_row = {key: row[key] for key in main_fieldnames}
            writer.writerow(clean_row)

    # Write test_citizens.csv with eligibility label
    with open(TEST_OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=test_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {OUTPUT_FILE} with {NUM_CITIZENS} citizens.")
    print(f"Generated {TEST_OUTPUT_FILE} with {NUM_CITIZENS} citizens.")


if __name__ == "__main__":
    main()