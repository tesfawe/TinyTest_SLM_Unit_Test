#!/usr/bin/env python3
import argparse
import coverage
import pytest
from pathlib import Path


# python -m scripts.run_coverage --test-dir consolidated_tests/run_id_3 --source data/modules --output coverage_summary_run_id_3.txt

def run_coverage(test_dir: str, source_dir: str, output_file: str):
    cov = coverage.Coverage(source=[source_dir])
    cov.start()
    pytest.main([test_dir, "-q"])
    cov.stop()
    cov.save()
    with open(output_file, "w") as f:
        cov.report(file=f, show_missing=True)
    print(f"Coverage summary saved to {output_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-dir", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="coverage_summary.txt")
    args = parser.parse_args()
    run_coverage(args.test_dir, args.source, args.output)


if __name__ == "__main__":
    main()
