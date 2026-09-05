"""
Shared terminal-report engine for all checkpoint validators.

Every validator in this folder (clean data, processed data, processor,
Kafka, MongoDB, API) uses this so the PASS/FAIL output looks and behaves
the same everywhere:

========================================
CHECKPOINT — CLEAN DATA
========================================

[PASS] Record count
[PASS] ResponseId uniqueness
[FAIL] YearsCode type

Problem:
ResponseId 1842 contains an invalid YearsCode value.

Expected:
integer or null

Check:
Review the YearsCode conversion in your cleaning step.

RESULT: 2/3 checks passed
CHECKPOINT FAILED

The terminal only tells the student WHAT failed and WHERE to look. Full
explanations of WHY belong in each checkpoint's Student README, not here.
"""

import sys


class Checkpoint:
    def __init__(self, title):
        self.title = title
        self.results = []  # list of dicts: label, passed, problem, expected, check

    def check(self, condition, label, problem=None, expected=None, check=None):
        """
        condition: bool - did this check pass?
        label: short one-line name shown next to [PASS]/[FAIL]
        problem/expected/check: only used when condition is False - a
            concrete description of what went wrong, what was expected,
            and what part of the implementation to look at.
        """
        passed = bool(condition)
        self.results.append({
            "label": label,
            "passed": passed,
            "problem": problem,
            "expected": expected,
            "check": check,
        })
        return passed

    def print_report_and_exit(self):
        bar = "=" * 40
        print(bar)
        print(f"CHECKPOINT — {self.title}")
        print(bar)
        print()

        for result in self.results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"[{status}] {result['label']}")

        failed = [r for r in self.results if not r["passed"]]
        for result in failed:
            print()
            if result["problem"]:
                print("Problem:")
                print(result["problem"])
            if result["expected"]:
                print("\nExpected:")
                print(result["expected"])
            if result["check"]:
                print("\nCheck:")
                print(result["check"])

        total = len(self.results)
        passed_count = total - len(failed)
        print(f"\nRESULT: {passed_count}/{total} checks passed")

        if failed:
            print("CHECKPOINT FAILED")
            sys.exit(1)
        print("CHECKPOINT PASSED")
