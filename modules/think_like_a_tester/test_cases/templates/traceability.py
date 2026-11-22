# Template from myOpenSDET: https://myopensdet.github.io/
"""Show which requirements have test cases, and which have none.

    python traceability.py requirements.txt test_cases.csv

requirements.txt has one requirement per line:   REF-1: short description
test_cases.csv has a "Covers" column with one or more IDs: REF-1 or REF-1;REF-4
Lines starting with # are ignored in both files.

Ends with exit code 1 if a requirement has no test case, so it can run in a pipeline.
"""

import csv
import sys


def read_requirements(path: str) -> dict[str, str]:
    requirements = {}
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                requirement, _, text = line.partition(":")
                requirements[requirement.strip()] = text.strip()
    return requirements


def read_test_cases(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as file:
        lines = [line for line in file if not line.startswith("#")]
    return list(csv.DictReader(lines))


def trace(requirements: dict[str, str], cases: list[dict[str, str]]):
    """Return {requirement: [case IDs]} and the cases that point to unknown IDs."""
    matrix = {requirement: [] for requirement in requirements}
    unknown = []
    for case in cases:
        for requirement in case["Covers"].replace(";", ",").split(","):
            requirement = requirement.strip()
            if requirement in matrix:
                matrix[requirement].append(case["ID"])
            elif requirement:
                unknown.append((case["ID"], requirement))
    return matrix, unknown


def main(args: list[str]) -> int:
    if len(args) != 2:
        print("Usage: python traceability.py requirements.txt test_cases.csv")
        return 2
    requirements = read_requirements(args[0])
    matrix, unknown = trace(requirements, read_test_cases(args[1]))
    print("| Requirement | Test cases | Count |")
    print("| --- | --- | --- |")
    for requirement, case_ids in matrix.items():
        print(f"| {requirement} | {', '.join(case_ids) or 'NONE'} | {len(case_ids)} |")
    gaps = [requirement for requirement, case_ids in matrix.items() if not case_ids]
    print()
    for requirement in gaps:
        print(f"No test case: {requirement} ({requirements[requirement]})")
    for case_id, requirement in unknown:
        print(f"{case_id} covers {requirement}, which is not in the requirements (typo or new?)")
    if not gaps and not unknown:
        print("Every requirement has at least one test case.")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
