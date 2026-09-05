"""
Shared helpers for reading the raw CSV as plain Python data (no pandas).

Used by every checkpoint that needs to compare against the original raw
values - cleaning must not silently change them, and neither should any
later stage.
"""

import csv

# Fields whose raw text should pass through cleaning and enrichment
# completely unchanged (empty string in the CSV means "missing").
PASSTHROUGH_FIELDS = ["Age", "DevType", "LearnCodeChoose", "LearnCodeAI", "AISelect", "AIAcc", "AISent"]


def _normalize(value):
    return None if value == "" else value


def load_raw_ids(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {int(row["ResponseId"]) for row in reader}


def load_raw_by_id(path):
    """Returns {ResponseId: {field: value-or-None}} for the passthrough fields."""
    raw_by_id = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_by_id[int(row["ResponseId"])] = {
                field: _normalize(row[field]) for field in PASSTHROUGH_FIELDS
            }
    return raw_by_id
