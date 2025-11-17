#!/usr/bin/env python3
"""
analyze_results.py

Analyze all metadata.json files from runs and count statistics.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# python scripts/analyze_results.py --runs-dir old_runs/run_id_3 --output run_id_3_results_summary.json


def analyze_runs(runs_dir: Path = Path("runs")) -> Dict:
    """Analyze all metadata.json files in runs directory."""
    
    if not runs_dir.exists():
        return {}
    
    stats = {
        "total_modules": 0,
        "passed": 0,
        "failed": 0,
        "compiled": 0,
        "ran": 0,
        "passed_after_repair": 0,
        "by_model": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0}),
        "by_prompt": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0}),
        "by_status": defaultdict(int),
        "by_failure_type": defaultdict(int),
        "passed_modules_after_repair": [],
        "passed_modules_without_repair": [],
        "failed_modules": [],
    }
    
    metadata_files = list(runs_dir.rglob("metadata.json"))
    
    for metadata_file in sorted(metadata_files):
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            
            module_id = data.get("module_id", "unknown")
            model = data.get("model", "unknown")
            prompt_id = data.get("prompt_id", "unknown")
            final_status = data.get("final_status", "unknown")
            final_failure_type = data.get("final_failure_type")
            iterations = data.get("iterations", [])
            number_of_iterations = len(iterations)
            
            stats["total_modules"] += 1
            stats["by_status"][final_status] += 1
            
            module_info = {
                "module_id": module_id,
                "model": model,
                "prompt_id": prompt_id,
                "number_of_iterations": number_of_iterations,
                "final_status": final_status,
                "final_failure_type": final_failure_type,
                "path": str(metadata_file.relative_to(runs_dir)),
            }
            
            if final_status == "passed":
                stats["passed"] += 1
                
                if iterations and len(iterations) > 0:
                    first_iteration_status = iterations[0].get("status", "unknown")
                    if first_iteration_status != "passed":
                        stats["passed_after_repair"] += 1
                        stats["passed_modules_after_repair"].append(module_info)
                    else:
                        stats["passed_modules_without_repair"].append(module_info)
                else:
                    stats["failed_modules"].append(module_info)

            elif final_status == "failed":
                stats["failed"] += 1
                stats["failed_modules"].append(module_info)
            elif final_status == "compiled":
                stats["compiled"] += 1
            elif final_status == "ran":
                stats["ran"] += 1
            
            if final_failure_type:
                stats["by_failure_type"][final_failure_type] += 1
            
            # Track by model
            stats["by_model"][model]["total"] += 1
            if final_status == "passed":
                stats["by_model"][model]["passed"] += 1
            else:
                stats["by_model"][model]["failed"] += 1
            
            # Track by prompt
            stats["by_prompt"][prompt_id]["total"] += 1
            if final_status == "passed":
                stats["by_prompt"][prompt_id]["passed"] += 1
            else:
                stats["by_prompt"][prompt_id]["failed"] += 1
            
        except Exception as e:
            pass
    
    for key in ["by_model", "by_prompt", "by_status", "by_failure_type"]:
        stats[key] = dict(stats[key])
    
    return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze test generation results from runs")
    parser.add_argument("--runs-dir", default="runs", help="Directory containing run results")
    parser.add_argument("--output", help="Output JSON file for detailed stats")
    
    args = parser.parse_args()
    
    runs_dir = Path(args.runs_dir)
    stats = analyze_runs(runs_dir)
    
    if stats.get("total_modules", 0) == 0:
        print("No modules found to analyze")
        return
    
    if args.output:
        output_path = Path(args.output)
    else:
        runs_dir_name = runs_dir.name
        if runs_dir_name.startswith("run_id_"):
            output_path = Path(f"{runs_dir_name}_results_summary.json")
        else:
            output_path = Path("results_summary.json")
    
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"Total modules: {stats['total_modules']}")
    print(f"Passed modules: {stats['passed']}")
    print(f"Failed modules: {stats['failed']}")
    print(f"Compiled modules: {stats['compiled']}")
    print(f"Ran modules: {stats['ran']}")
    print(f"Passed modules after repair: {len(stats['passed_modules_after_repair'])}")
    print(f"Passed modules without repair: {len(stats['passed_modules_without_repair'])}")

if __name__ == "__main__":
    main()

