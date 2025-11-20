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
        # Iteration distribution
        "by_iterations": defaultdict(int),  # How many modules took 1, 2, 3... iterations
        # Token statistics
        "token_stats": {
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "average_tokens_per_module": 0,
            "tokens_by_iteration_type": {"initial": 0, "repair": 0},
            "tokens_by_status": {"passed": 0, "failed": 0, "compiled": 0, "ran": 0},
        },
        # Performance statistics
        "performance_stats": {
            "total_time": 0,
            "total_duration": 0,  # Sum of all total_duration from iterations
            "total_eval_duration": 0,  # Sum of eval_duration for tokens/sec calculation
            "average_tokens_per_second": 0,
            "average_time_per_module": 0,
        },
        # Efficiency metrics
        "efficiency_stats": {
            "tokens_per_passed_module": 0,
            "tokens_per_successful_test": 0,
            "total_tests_passed": 0,
            "total_tests_generated": 0,
        },
        # Repair statistics
        "repair_stats": {
            "total_repair_iterations": 0,
            "total_repair_tokens": 0,
            "repair_success_rate": 0,  # How many repairs led to passing
            "average_tokens_per_repair": 0,
        },
        "passed_modules_after_repair": [],
        "passed_modules_without_repair": [],
        "failed_modules": [],
        "modules": [],
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
            stats["by_iterations"][number_of_iterations] += 1
            
            module_info = {
                "module_id": module_id,
                "model": model,
                "prompt_id": prompt_id,
                "number_of_iterations": number_of_iterations,
                "final_status": final_status,
                "final_failure_type": final_failure_type,
                "path": str(metadata_file.relative_to(runs_dir)),
            }
            
            # Always add full details to modules list
            stats["modules"].append(module_info)
            
            # Dynamic repair detection: if final_status is "passed" and there are multiple iterations,
            # then repairs were needed (otherwise we would have stopped after the first iteration)
            needed_repair = False
            if final_status == "passed" and iterations and len(iterations) > 1:
                needed_repair = True
            
            if final_status == "passed":
                stats["passed"] += 1
                
                if needed_repair:
                    stats["passed_after_repair"] += 1
                    stats["passed_modules_after_repair"].append(module_id)
                else:
                    stats["passed_modules_without_repair"].append(module_id)

            elif final_status == "failed":
                stats["failed"] += 1
                stats["failed_modules"].append(module_id)
            elif final_status == "compiled":
                stats["compiled"] += 1
            elif final_status == "ran":
                stats["ran"] += 1
            
            if final_failure_type:
                stats["by_failure_type"][final_failure_type] += 1
            
            # Collect token and performance statistics from iterations
            for iteration in iterations:
                # Token statistics
                total_tokens = iteration.get("total_tokens") or 0
                prompt_tokens = iteration.get("prompt_eval_count") or 0
                completion_tokens = iteration.get("eval_count") or 0
                iteration_kind = iteration.get("kind", "unknown")
                iteration_status = iteration.get("status", "unknown")
                tokens_per_second = iteration.get("tokens_per_second")
                total_duration = iteration.get("total_duration") or 0
                time_elapsed = iteration.get("time") or 0
                
                stats["token_stats"]["total_tokens"] += total_tokens
                stats["token_stats"]["total_prompt_tokens"] += prompt_tokens
                stats["token_stats"]["total_completion_tokens"] += completion_tokens
                
                # Tokens by iteration type
                if iteration_kind == "initial":
                    stats["token_stats"]["tokens_by_iteration_type"]["initial"] += total_tokens
                elif iteration_kind == "repair":
                    stats["token_stats"]["tokens_by_iteration_type"]["repair"] += total_tokens
                    stats["repair_stats"]["total_repair_iterations"] += 1
                    stats["repair_stats"]["total_repair_tokens"] += total_tokens
                
                # Tokens by status
                if iteration_status in stats["token_stats"]["tokens_by_status"]:
                    stats["token_stats"]["tokens_by_status"][iteration_status] += total_tokens
                
                # Performance statistics
                stats["performance_stats"]["total_time"] += time_elapsed
                stats["performance_stats"]["total_duration"] += total_duration
                eval_duration = iteration.get("eval_duration") or 0
                stats["performance_stats"]["total_eval_duration"] += eval_duration
                
                # Test statistics
                tests_passed = iteration.get("tests_passed") or 0
                tests_total = iteration.get("tests_total") or 0
                stats["efficiency_stats"]["total_tests_passed"] += tests_passed
                stats["efficiency_stats"]["total_tests_generated"] += tests_total
            
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

            stats["modules"].append(module_info)
            
        except Exception as e:
            pass
    
    # Convert defaultdicts to dicts
    for key in ["by_model", "by_prompt", "by_status", "by_failure_type", "by_iterations"]:
        stats[key] = dict(stats[key])
    
    # Calculate averages and final statistics
    total_modules = stats["total_modules"]
    if total_modules > 0:
        # Token statistics
        stats["token_stats"]["average_tokens_per_module"] = stats["token_stats"]["total_tokens"] / total_modules
        
        # Performance statistics
        stats["performance_stats"]["average_time_per_module"] = stats["performance_stats"]["total_time"] / total_modules
        
        # Calculate average tokens per second
        total_completion_tokens = stats["token_stats"]["total_completion_tokens"]
        total_eval_duration = stats["performance_stats"]["total_eval_duration"]
        if total_eval_duration > 0:
            stats["performance_stats"]["average_tokens_per_second"] = (total_completion_tokens / total_eval_duration) * 1_000_000_000
        
        # Efficiency metrics
        if stats["passed"] > 0:
            stats["efficiency_stats"]["tokens_per_passed_module"] = stats["token_stats"]["total_tokens"] / stats["passed"]
        
        if stats["efficiency_stats"]["total_tests_passed"] > 0:
            stats["efficiency_stats"]["tokens_per_successful_test"] = stats["token_stats"]["total_tokens"] / stats["efficiency_stats"]["total_tests_passed"]
        
        # Repair statistics
        if stats["repair_stats"]["total_repair_iterations"] > 0:
            stats["repair_stats"]["average_tokens_per_repair"] = stats["repair_stats"]["total_repair_tokens"] / stats["repair_stats"]["total_repair_iterations"]
        
        # Repair success rate: how many modules that had repairs ended up passing
        modules_with_repairs = sum(1 for m in stats["modules"] if m["number_of_iterations"] > 1)
        if modules_with_repairs > 0:
            passed_with_repairs = len(stats["passed_modules_after_repair"])
            stats["repair_stats"]["repair_success_rate"] = passed_with_repairs / modules_with_repairs
    
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
    print(f"\nIteration Distribution:")
    for num_iter, count in sorted(stats['by_iterations'].items()):
        print(f"  {num_iter} iteration(s): {count} modules")
    print(f"\nToken Statistics:")
    print(f"  Total tokens: {stats['token_stats']['total_tokens']:,}")
    print(f"  Average tokens per module: {stats['token_stats']['average_tokens_per_module']:.1f}")
    print(f"  Tokens (initial): {stats['token_stats']['tokens_by_iteration_type']['initial']:,}")
    print(f"  Tokens (repair): {stats['token_stats']['tokens_by_iteration_type']['repair']:,}")
    print(f"\nPerformance Statistics:")
    print(f"  Average tokens/second: {stats['performance_stats']['average_tokens_per_second']:.1f}")
    print(f"  Average time per module: {stats['performance_stats']['average_time_per_module']:.2f}s")
    print(f"\nEfficiency Metrics:")
    if stats['efficiency_stats']['tokens_per_passed_module'] > 0:
        print(f"  Tokens per passed module: {stats['efficiency_stats']['tokens_per_passed_module']:.1f}")
    if stats['efficiency_stats']['tokens_per_successful_test'] > 0:
        print(f"  Tokens per successful test: {stats['efficiency_stats']['tokens_per_successful_test']:.1f}")
    print(f"  Total tests passed: {stats['efficiency_stats']['total_tests_passed']}")
    print(f"\nRepair Statistics:")
    print(f"  Total repair iterations: {stats['repair_stats']['total_repair_iterations']}")
    print(f"  Repair success rate: {stats['repair_stats']['repair_success_rate']:.1%}")
    if stats['repair_stats']['average_tokens_per_repair'] > 0:
        print(f"  Average tokens per repair: {stats['repair_stats']['average_tokens_per_repair']:.1f}")

if __name__ == "__main__":
    main()

