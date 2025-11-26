import os
import subprocess
import json
import re
from collections import defaultdict
import argparse


## Usage: python mutmut_run_and_export.py --all 
##        python mutmut_run_and_export.py --runs run_id_4 run_id_5


def run_mutmut(run_workspace):
    """
    Run mutmut inside a given workspace and save JSON results in the same folder.
    """
    print(f"\nRunning mutmut in {run_workspace}...")

    # Run mutation testing
    subprocess.run(["mutmut", "run"], cwd=run_workspace, check=True)

    # Fetch results
    result = subprocess.run(
        ["mutmut", "results"],
        cwd=run_workspace,
        capture_output=True,
        text=True,
        check=True
    )
    lines = result.stdout.splitlines()

    # Parse results
    mutants = []
    pattern = re.compile(
        r"(?P<module>[\w\.]+)\.(?P<function>\w+)__mutmut_(?P<id>\d+): (?P<status>\w+)"
    )

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            m = match.groupdict()
            m["id"] = int(m["id"])
            m["status"] = m["status"].lower()
            mutants.append(m)

    # Save JSON inside the run workspace
    output_file = os.path.join(run_workspace, "mutmut_results.json")
    with open(output_file, "w") as f:
        json.dump(mutants, f, indent=2)

    print(f"Saved mutmut_results.json in {run_workspace}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mutmut on selected run folders.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="Run mutmut on all run folders"
    )
    group.add_argument(
        "--runs",
        nargs="+",
        help="Run mutmut only on specified run folders (e.g., run_id_4 run_id_5)"
    )

    args = parser.parse_args()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Determine which runs to execute
    if args.all:
        run_folders = [
            os.path.join(BASE_DIR, entry)
            for entry in os.listdir(BASE_DIR)
            if os.path.isdir(os.path.join(BASE_DIR, entry)) and entry.startswith("run_id_")
        ]
    else:
        # Only use specified run folders
        run_folders = [
            os.path.join(BASE_DIR, run_id)
            for run_id in args.runs
            if os.path.isdir(os.path.join(BASE_DIR, run_id))
        ]

    if not run_folders:
        print("No valid run folders found. Exiting.")
        exit(1)

    # Run mutmut for each selected folder
    for folder in run_folders:
        run_mutmut(folder)
