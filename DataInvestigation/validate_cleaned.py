"""
Checkpoint 1 - Clean Data

Validates a candidate cleaned JSONL file against the cleaning contract
described in PROJECT_GUIDE.md Section 6-8. Validates OUTCOMES, not
implementation - it doesn't care how the file was produced, only whether
the result satisfies the contract.

Usage:
    python3 validate_cleaned.py path/to/your_cleaned.jsonl
"""

import json
import sys
from collections import Counter
from pathlib import Path

from checkpoint_utils import Checkpoint
from raw_utils import load_raw_ids, load_raw_by_id, PASSTHROUGH_FIELDS

THIS_DIR = Path(__file__).resolve().parent
DAY4_DIR = THIS_DIR.parent
RAW_FILE = DAY4_DIR / "AllDataFiles"/"developer_ai_learning_raw.csv"
GOLDEN_FILE = DAY4_DIR / "instructor" / "expected" / "golden_sample_cleaned.json"

EXPECTED_FIELDS = {
    "ResponseId", "Age", "YearsCode", "DevType", "LearnCodeChoose",
    "LearnCode", "LearnCodeAI", "AILearnHow", "AISelect", "AIAcc", "AISent",
}

VALID_CATEGORIES = {
    "AISelect": {
        "Yes, I use AI tools daily", "Yes, I use AI tools weekly",
        "Yes, I use AI tools monthly or infrequently",
        "No, and I don't plan to", "No, but I plan to soon", None,
    },
    "AIAcc": {
        "Highly trust", "Somewhat trust", "Neither trust nor distrust",
        "Somewhat distrust", "Highly distrust", None,
    },
    "AISent": {
        "Very favorable", "Favorable", "Indifferent", "Unfavorable",
        "Very unfavorable", "Unsure", None,
    },
}


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def first_bad(records, predicate):
    for record in records:
        if not predicate(record):
            return record
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_cleaned.py path/to/your_file.jsonl")
        sys.exit(2)
    candidate_path = Path(sys.argv[1])
    print(f"Validating: {candidate_path}\n")

    records = load_jsonl(candidate_path)
    raw_ids = load_raw_ids(RAW_FILE)
    raw_by_id = load_raw_by_id(RAW_FILE)

    cp = Checkpoint("CLEAN DATA")

    cp.check(
        len(records) == len(raw_ids),
        "Record count matches raw",
        problem=f"Found {len(records)} records, expected {len(raw_ids)}.",
        expected="Same number of records as the raw CSV - nothing removed unless real duplicates were found.",
        check="Check whether you accidentally dropped rows (e.g. with dropna()).",
    )

    bad_fields_record = first_bad(records, lambda r: set(r.keys()) == EXPECTED_FIELDS)
    cp.check(
        bad_fields_record is None,
        "Every record has exactly the 11 expected fields",
        problem=(
            f"ResponseId={bad_fields_record.get('ResponseId', '?')} has fields "
            f"{sorted(bad_fields_record.keys())}" if bad_fields_record else None
        ),
        expected=f"Exactly these 11 fields: {sorted(EXPECTED_FIELDS)}",
        check="Check whether a column was renamed, dropped, or an extra column was added.",
    )

    response_ids = [r.get("ResponseId") for r in records]
    id_counts = Counter(response_ids)
    duplicate_ids = {rid for rid, count in id_counts.items() if count > 1}
    cp.check(
        len(duplicate_ids) == 0,
        "ResponseId is unique",
        problem=f"Duplicate ResponseId value(s): {sorted(duplicate_ids)[:5]}",
        expected="Every ResponseId appears exactly once.",
        check="Check your duplicate-row handling logic.",
    )
    cp.check(
        set(response_ids) == raw_ids,
        "Same ResponseIds as raw dataset",
        problem="The set of ResponseIds in your cleaned file does not match the raw CSV.",
        expected="Identical ResponseId set to the raw CSV.",
        check="Check whether any respondent was accidentally added or removed.",
    )

    bad_years = first_bad(
        records, lambda r: r.get("YearsCode") is None or isinstance(r.get("YearsCode"), int)
    )
    cp.check(
        bad_years is None,
        "YearsCode is integer or null for every record",
        problem=(
            f"ResponseId={bad_years.get('ResponseId')} has YearsCode="
            f"{bad_years.get('YearsCode')!r} ({type(bad_years.get('YearsCode')).__name__})"
            if bad_years else None
        ),
        expected="integer or null",
        check="Review the YearsCode conversion in your cleaning step (nullable integer, not float or string).",
    )

    bad_learn_code = first_bad(
        records, lambda r: r.get("LearnCode") is None or isinstance(r.get("LearnCode"), list)
    )
    cp.check(
        bad_learn_code is None,
        "LearnCode is list or null for every record",
        problem=(
            f"ResponseId={bad_learn_code.get('ResponseId')} has LearnCode="
            f"{bad_learn_code.get('LearnCode')!r}" if bad_learn_code else None
        ),
        expected="A list of strings, or null.",
        check="Check your multi-select splitting logic for LearnCode - did you handle missing values before splitting?",
    )

    bad_ai_learn_how = first_bad(
        records, lambda r: r.get("AILearnHow") is None or isinstance(r.get("AILearnHow"), list)
    )
    cp.check(
        bad_ai_learn_how is None,
        "AILearnHow is list or null for every record",
        problem=(
            f"ResponseId={bad_ai_learn_how.get('ResponseId')} has AILearnHow="
            f"{bad_ai_learn_how.get('AILearnHow')!r}" if bad_ai_learn_how else None
        ),
        expected="A list of strings, or null.",
        check="Check your multi-select splitting logic for AILearnHow - did you handle missing values before splitting?",
    )

    for field, valid_values in VALID_CATEGORIES.items():
        bad_record = first_bad(records, lambda r, f=field: r.get(f) in valid_values)
        cp.check(
            bad_record is None,
            f"{field} values are within the known valid category set",
            problem=(
                f"ResponseId={bad_record.get('ResponseId')} has {field}="
                f"{bad_record.get(field)!r}, which is not one of the known survey answers"
                if bad_record else None
            ),
            expected="One of the real survey category values, unchanged, or null.",
            check=f"Check whether {field} text was reworded, trimmed, or otherwise normalized.",
        )

    bad_passthrough_record = None
    bad_passthrough_field = None
    for record in records:
        raw_row = raw_by_id.get(record.get("ResponseId"))
        if raw_row is None:
            continue
        for field in PASSTHROUGH_FIELDS:
            if record.get(field) != raw_row[field]:
                bad_passthrough_record = record
                bad_passthrough_field = field
                break
        if bad_passthrough_record:
            break
    cp.check(
        bad_passthrough_record is None,
        "Original survey answers (Age, DevType, LearnCodeChoose, LearnCodeAI, AISelect, AIAcc, AISent) are unchanged",
        problem=(
            f"ResponseId={bad_passthrough_record.get('ResponseId')}: {bad_passthrough_field} = "
            f"{bad_passthrough_record.get(bad_passthrough_field)!r}, but the raw CSV has "
            f"{raw_by_id[bad_passthrough_record.get('ResponseId')][bad_passthrough_field]!r}"
            if bad_passthrough_record else None
        ),
        expected="The exact same text as the raw CSV (or null when the raw value was empty).",
        check="Check for any normalization, trimming, or 'fixing' applied to fields that should pass through unchanged.",
    )

    if GOLDEN_FILE.exists():
        golden_records = json.load(open(GOLDEN_FILE, encoding="utf-8"))
        by_id = {r.get("ResponseId"): r for r in records}
        missing = [g["ResponseId"] for g in golden_records if g["ResponseId"] not in by_id]
        cp.check(
            not missing,
            "Golden sample: all 18 known respondents are present",
            problem=f"Missing ResponseId(s): {missing}",
            expected="All 18 known respondents used for spot-checking must be present.",
            check="Check whether these specific respondents were dropped somewhere in cleaning.",
        )
        mismatches = [
            (g["ResponseId"], sorted(k for k in g if by_id[g["ResponseId"]].get(k) != g.get(k)))
            for g in golden_records
            if g["ResponseId"] in by_id and by_id[g["ResponseId"]] != g
        ]
        problem_text = None
        if mismatches:
            rid, fields = mismatches[0]
            problem_text = f"ResponseId={rid} differs in field(s): {fields}"
        cp.check(
            not mismatches,
            "Golden sample: known respondents match the reference values exactly",
            problem=problem_text,
            expected="Every field of a known respondent must match the authoritative reference exactly.",
            check="This respondent was picked to test a specific edge case - trace their raw CSV row through your own cleaning step to find where your result diverges. The 'Problem' line above already names the exact differing field(s).",
        )

    cp.print_report_and_exit()


if __name__ == "__main__":
    main()
