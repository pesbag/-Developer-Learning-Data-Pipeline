"""
Shared "processed record" contract checks.

This is the single place that knows what a correct processed record looks
like (15 fields, correct types, correct experienceLevel/boolean business
rules). It is imported by every checkpoint that deals with processed-shape
records, wherever those records come from:

- validate_processed.py         (Pandas/enrichment output)
- validate_kafka_processing.py  (records consumed from the processed Kafka topic)
- validate_mongo_storage.py     (records exported from MongoDB)

Keeping this logic in one place means all three checkpoints agree on
exactly the same contract - there is no separate "Kafka version" or
"Mongo version" of what a correct record looks like.

Reuses the exact option strings and PROCESSED_FIELDS from enrichment.py
(the single source of truth for the enrichment business rules) instead of
redefining them here.
"""

from collections import Counter

# Constants from enrichment.py - these define the exact option strings
# and field list that the enrichment step must produce
TECH_DOCUMENTATION_OPTION = "Technical documentation (is generated for/by the tool or system)"
AI_CODEGEN_OPTION = "AI CodeGen tools or AI-enabled apps"
STACK_OVERFLOW_OPTION = "Stack Overflow or Stack Exchange"

PROCESSED_FIELDS = [
    "responseId", "age", "yearsCode", "devType", "learnCodeChoose",
    "learningMethods", "learnCodeAI", "aiLearningMethods", "aiUsage",
    "aiTrust", "aiSentiment", "experienceLevel", "usesDocumentation",
    "usesAIForLearning", "usesStackOverflow",
]

EXPECTED_FIELDS = set(PROCESSED_FIELDS)


def expected_experience_level(years_code):
    if years_code is None:
        return "Unknown"
    if years_code <= 2:
        return "Beginner"
    if years_code <= 5:
        return "Early Career"
    if years_code <= 10:
        return "Experienced"
    return "Highly Experienced"


def _first_bad(records, predicate):
    """Return the first record for which predicate(record) is False, or None."""
    for record in records:
        if not predicate(record):
            return record
    return None


def run_processed_contract_checks(cp, records, raw_ids=None):
    """
    cp: a checkpoint_utils.Checkpoint instance to record results into.
    records: list of parsed processed-schema dicts (from Kafka, Mongo, or Pandas output).
    raw_ids: optional set of int ResponseIds from the raw CSV. When given,
        this also checks that the record set matches the raw respondents
        exactly. When omitted (e.g. a partial Kafka/Mongo sample), those
        two checks are skipped and only structural/business-rule checks run.
    """
    if raw_ids is not None:
        cp.check(
            len(records) == len(raw_ids),
            "Record count matches raw respondents",
            problem=f"Found {len(records)} records, expected {len(raw_ids)}.",
            expected="One record per respondent in the raw CSV - none added, none missing.",
            check="Check whether every raw row was processed and published/stored exactly once.",
        )

    bad_fields_record = _first_bad(
        records, lambda r: set(r.keys()) == EXPECTED_FIELDS and len(r) == 15
    )
    cp.check(
        bad_fields_record is None,
        "Exactly 15 operational fields per record",
        problem=(
            f"responseId={bad_fields_record.get('responseId', '?')} has fields "
            f"{sorted(bad_fields_record.keys())}" if bad_fields_record else None
        ),
        expected=f"Exactly these 15 fields: {sorted(EXPECTED_FIELDS)}",
        check="Check your schema-mapping step - are you adding, dropping, or renaming any field?",
    )

    response_ids = [r.get("responseId") for r in records]
    id_counts = Counter(response_ids)
    duplicate_ids = {rid for rid, count in id_counts.items() if count > 1}
    cp.check(
        len(duplicate_ids) == 0,
        "responseId is unique",
        problem=f"Duplicate responseId value(s) found: {sorted(duplicate_ids)[:5]}",
        expected="Every responseId appears exactly once.",
        check="Check for duplicate publishing/consuming, or a join that fanned out rows.",
    )

    if raw_ids is not None:
        missing = raw_ids - set(response_ids)
        extra = set(response_ids) - raw_ids
        cp.check(
            not missing and not extra,
            "Same respondents as raw dataset",
            problem=(
                f"Missing responseId(s): {sorted(missing)[:5]}" if missing
                else f"Unexpected responseId(s): {sorted(extra)[:5]}"
            ),
            expected="The exact same set of respondents as developer_ai_learning_raw.csv.",
            check="Check whether every raw record was read, processed, and forwarded.",
        )

    bad_array_record = _first_bad(
        records,
        lambda r: (r.get("learningMethods") is None or isinstance(r.get("learningMethods"), list))
        and (r.get("aiLearningMethods") is None or isinstance(r.get("aiLearningMethods"), list)),
    )
    cp.check(
        bad_array_record is None,
        "learningMethods / aiLearningMethods remain arrays or null",
        problem=(
            f"responseId={bad_array_record.get('responseId')} has "
            f"learningMethods={bad_array_record.get('learningMethods')!r}"
            if bad_array_record else None
        ),
        expected="A list of strings, or null. Never a single joined string, never exploded into extra records.",
        check="Check how the multi-select fields were serialized on their way through the pipeline.",
    )

    bad_exp_record = _first_bad(
        records, lambda r: r.get("experienceLevel") == expected_experience_level(r.get("yearsCode"))
    )
    cp.check(
        bad_exp_record is None,
        "experienceLevel matches the YearsCode rule",
        problem=(
            f"responseId={bad_exp_record.get('responseId')} has yearsCode="
            f"{bad_exp_record.get('yearsCode')!r} but experienceLevel="
            f"{bad_exp_record.get('experienceLevel')!r}" if bad_exp_record else None
        ),
        expected="Beginner (0-2), Early Career (3-5), Experienced (6-10), Highly Experienced (11+), Unknown (missing).",
        check="Check how a missing yearsCode is detected before bucketing - see PROJECT_GUIDE.md Phase 4.",
    )

    def _bool_ok(record, field, option):
        methods = record.get("learningMethods")
        expected_value = methods is not None and option in methods
        return record.get(field) == expected_value

    bad_doc_record = _first_bad(records, lambda r: _bool_ok(r, "usesDocumentation", TECH_DOCUMENTATION_OPTION))
    cp.check(
        bad_doc_record is None,
        "usesDocumentation matches the documentation-option rule",
        problem=(
            f"responseId={bad_doc_record.get('responseId')} has usesDocumentation="
            f"{bad_doc_record.get('usesDocumentation')!r} but learningMethods="
            f"{bad_doc_record.get('learningMethods')!r}" if bad_doc_record else None
        ),
        expected="True only when learningMethods contains the exact documentation option text.",
        check="Check the exact option string you are matching against (see PROJECT_GUIDE.md Phase 4).",
    )

    bad_ai_record = _first_bad(records, lambda r: _bool_ok(r, "usesAIForLearning", AI_CODEGEN_OPTION))
    cp.check(
        bad_ai_record is None,
        "usesAIForLearning matches the AI-CodeGen-option rule",
        problem=(
            f"responseId={bad_ai_record.get('responseId')} has usesAIForLearning="
            f"{bad_ai_record.get('usesAIForLearning')!r} but learningMethods="
            f"{bad_ai_record.get('learningMethods')!r}" if bad_ai_record else None
        ),
        expected="True only when learningMethods contains the exact AI CodeGen option text.",
        check="Check the exact option string you are matching against (see PROJECT_GUIDE.md Phase 4).",
    )

    bad_so_record = _first_bad(records, lambda r: _bool_ok(r, "usesStackOverflow", STACK_OVERFLOW_OPTION))
    cp.check(
        bad_so_record is None,
        "usesStackOverflow matches the Stack-Overflow-option rule",
        problem=(
            f"responseId={bad_so_record.get('responseId')} has usesStackOverflow="
            f"{bad_so_record.get('usesStackOverflow')!r} but learningMethods="
            f"{bad_so_record.get('learningMethods')!r}" if bad_so_record else None
        ),
        expected="True only when learningMethods contains the exact Stack Overflow option text.",
        check="Check the exact option string you are matching against (see PROJECT_GUIDE.md Phase 4).",
    )

    bad_null_record = _first_bad(
        records, lambda r: (r.get("yearsCode") is None) == (r.get("experienceLevel") == "Unknown")
    )
    cp.check(
        bad_null_record is None,
        "yearsCode is null if and only if experienceLevel is Unknown",
        problem=(
            f"responseId={bad_null_record.get('responseId')} has yearsCode="
            f"{bad_null_record.get('yearsCode')!r} and experienceLevel="
            f"{bad_null_record.get('experienceLevel')!r}" if bad_null_record else None
        ),
        expected="A missing yearsCode always means Unknown, and Unknown always means yearsCode is missing.",
        check="Check for a pandas NaN vs Python None mix-up in the experienceLevel calculation.",
    )


def check_golden_sample(cp, records_by_id, golden_records, label_prefix="Golden sample"):
    """
    records_by_id: dict {responseId: record} built from the candidate data.
    golden_records: list of authoritative processed records from
        instructor/expected/golden_sample_processed.json (instructor-only
        ground truth - the printed check messages deliberately do not point
        students at this file directly).
    """
    missing_ids = [g["responseId"] for g in golden_records if g["responseId"] not in records_by_id]
    cp.check(
        not missing_ids,
        f"{label_prefix}: all known respondents are present",
        problem=f"Missing responseId(s) from the known sample: {missing_ids}",
        expected="All 18 known respondents used for spot-checking must be present in your data.",
        check="Check whether these specific respondents were dropped somewhere in the pipeline.",
    )

    mismatches = []
    for golden in golden_records:
        candidate = records_by_id.get(golden["responseId"])
        if candidate is not None and candidate != golden:
            differing = sorted(k for k in golden if candidate.get(k) != golden.get(k))
            mismatches.append((golden["responseId"], differing))

    problem_text = None
    if mismatches:
        response_id, fields = mismatches[0]
        problem_text = f"responseId={response_id} differs in field(s): {fields}"

    cp.check(
        not mismatches,
        f"{label_prefix}: known respondents match the reference values exactly",
        problem=problem_text,
        expected="Every field of a known respondent must match the authoritative reference exactly.",
        check="This respondent was picked to test a specific edge case - trace their raw CSV row through your own pipeline step by step to find where your result diverges. The 'Problem' line above already names the exact differing field(s).",
    )
