"""
Checkpoint 2 - Processed / Enriched Data

Validates a candidate processed JSONL file against the operational schema
and enrichment contract (see PROJECT_GUIDE.md Section 11). Validates
OUTCOMES, not implementation.

Usage:
    python3 validate_processed.py path/to/your_processed.jsonl
"""

import json
import sys
from pathlib import Path

from checkpoint_utils import Checkpoint
from raw_utils import load_raw_ids, load_raw_by_id
from processed_contract import run_processed_contract_checks, check_golden_sample

THIS_DIR = Path(__file__).resolve().parent
DAY4_DIR = THIS_DIR.parent
RAW_FILE = DAY4_DIR / "AllDataFiles"/"developer_ai_learning_raw.csv"
GOLDEN_FILE = DAY4_DIR / "instructor" / "expected" / "golden_sample_cleaned.json"

# processed field -> raw CSV field, for fields that should pass straight
# through cleaning and enrichment without changing their value.
PASSTHROUGH_MAP = {
    "age": "Age",
    "devType": "DevType",
    "learnCodeChoose": "LearnCodeChoose",
    "learnCodeAI": "LearnCodeAI",
    "aiUsage": "AISelect",
    "aiTrust": "AIAcc",
    "aiSentiment": "AISent",
}


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_processed.py path/to/your_file.jsonl")
        sys.exit(2)
    candidate_path = Path(sys.argv[1])
    print(f"Validating: {candidate_path}\n")

    records = load_jsonl(candidate_path)
    raw_ids = load_raw_ids(RAW_FILE)
    raw_by_id = load_raw_by_id(RAW_FILE)

    cp = Checkpoint("PROCESSED DATA")

    run_processed_contract_checks(cp, records, raw_ids=raw_ids)

    bad_record = None
    bad_field = None
    for record in records:
        raw_row = raw_by_id.get(record.get("responseId"))
        if raw_row is None:
            continue
        for processed_field, raw_field in PASSTHROUGH_MAP.items():
            if record.get(processed_field) != raw_row[raw_field]:
                bad_record, bad_field = record, processed_field
                break
        if bad_record:
            break
    cp.check(
        bad_record is None,
        "Pass-through fields (age, devType, learnCodeChoose, learnCodeAI, aiUsage, aiTrust, aiSentiment) are unchanged",
        problem=(
            f"responseId={bad_record.get('responseId')}: {bad_field} = {bad_record.get(bad_field)!r}, "
            f"but the raw CSV has {raw_by_id[bad_record.get('responseId')][PASSTHROUGH_MAP[bad_field]]!r}"
            if bad_record else None
        ),
        expected="The exact same text as the raw CSV (or null when missing) - only the field name changed.",
        check="Check your schema-mapping step for accidental transformation of a pass-through field.",
    )

    if GOLDEN_FILE.exists():
        golden_records = json.load(open(GOLDEN_FILE, encoding="utf-8"))
        by_id = {r.get("responseId"): r for r in records}
        check_golden_sample(cp, by_id, golden_records)

    cp.print_report_and_exit()


if __name__ == "__main__":
    main()
