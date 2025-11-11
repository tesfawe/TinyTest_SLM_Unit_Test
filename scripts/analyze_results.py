#!/usr/bin/env python3
"""
analyze_results.py

Analyze all metadata.json files from runs and count statistics.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


def analyze_runs(runs_dir: Path = Path("runs")) -> Dict:
    """Analyze all metadata.json files in runs directory."""
    
    if not runs_dir.exists():
        print(f"Runs directory not found: {runs_dir}")
        return {}
    
    stats = {
        "total_modules": 0,
        "passed": 0,
        "failed": 0,
        "compiled": 0,
        "ran": 0,
        "by_model": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0}),
        "by_prompt": defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0}),
        "by_status": defaultdict(int),
        "by_failure_type": defaultdict(int),
        "modules": [],
    }
    
    # Find all metadata.json files
    metadata_files = list(runs_dir.rglob("metadata.json"))
    
    print(f"Found {len(metadata_files)} metadata files\n")
    
    for metadata_file in sorted(metadata_files):
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            
            module_id = data.get("module_id", "unknown")
            model = data.get("model", "unknown")
            prompt_id = data.get("prompt_id", "unknown")
            final_status = data.get("final_status", "unknown")
            final_failure_type = data.get("final_failure_type")
            
            stats["total_modules"] += 1
            stats["by_status"][final_status] += 1
            
            if final_status == "passed":
                stats["passed"] += 1
            elif final_status == "failed":
                stats["failed"] += 1
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
            
            # Store module info
            stats["modules"].append({
                "module_id": module_id,
                "model": model,
                "prompt_id": prompt_id,
                "final_status": final_status,
                "final_failure_type": final_failure_type,
                "path": str(metadata_file.relative_to(runs_dir)),
            })
            
        except Exception as e:
            print(f"Error reading {metadata_file}: {e}")
    
    return stats


def print_summary(stats: Dict):
    """Print analysis summary."""
    
    print("=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"\nTotal Modules: {stats['total_modules']}")
    print(f"\nFinal Status Breakdown:")
    print(f"  Passed:   {stats['passed']:4d} ({stats['passed']/stats['total_modules']*100:.1f}%)")
    print(f"  Failed:   {stats['failed']:4d} ({stats['failed']/stats['total_modules']*100:.1f}%)")
    print(f"  Compiled: {stats['compiled']:4d} ({stats['compiled']/stats['total_modules']*100:.1f}%)")
    print(f"  Ran:      {stats['ran']:4d} ({stats['ran']/stats['total_modules']*100:.1f}%)")
    
    if stats['by_failure_type']:
        print(f"\nFailure Types:")
        for failure_type, count in sorted(stats['by_failure_type'].items(), key=lambda x: -x[1]):
            print(f"  {failure_type:15s}: {count:4d}")
    
    if stats['by_model']:
        print(f"\nBy Model:")
        for model in sorted(stats['by_model'].keys()):
            model_stats = stats['by_model'][model]
            total = model_stats['total']
            passed = model_stats['passed']
            print(f"  {model:20s}: {passed:3d}/{total:3d} passed ({passed/total*100:.1f}%)")
    
    if stats['by_prompt']:
        print(f"\nBy Prompt Template:")
        for prompt in sorted(stats['by_prompt'].keys()):
            prompt_stats = stats['by_prompt'][prompt]
            total = prompt_stats['total']
            passed = prompt_stats['passed']
            print(f"  {prompt:15s}: {passed:3d}/{total:3d} passed ({passed/total*100:.1f}%)")
    
    print("\n" + "=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze test generation results from runs")
    parser.add_argument("--runs-dir", default="runs", help="Directory containing run results")
    parser.add_argument("--output", help="Output JSON file for detailed stats")
    parser.add_argument("--list-passed", action="store_true", help="List all modules with passed status")
    parser.add_argument("--list-failed", action="store_true", help="List all modules with failed status")
    
    args = parser.parse_args()
    
    runs_dir = Path(args.runs_dir)
    stats = analyze_runs(runs_dir)
    
    if stats["total_modules"] == 0:
        print("No metadata files found.")
        return
    
    print_summary(stats)
    
    if args.list_passed:
        print("\nModules with PASSED status:")
        for module in stats["modules"]:
            if module["final_status"] == "passed":
                print(f"  {module['module_id']:15s} | {module['model']:20s} | {module['prompt_id']:10s} | {module['path']}")
    
    if args.list_failed:
        print("\nModules with FAILED status:")
        for module in stats["modules"]:
            if module["final_status"] == "failed":
                print(f"  {module['module_id']:15s} | {module['model']:20s} | {module['prompt_id']:10s} | {module['final_failure_type']:10s} | {module['path']}")
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\nDetailed stats saved to: {output_path}")


if __name__ == "__main__":
    main()

