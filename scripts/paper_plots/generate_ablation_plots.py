"""
generate_paper_plots.py

Generate comprehensive visualizations and statistics for paper results.
Analyzes 7 models × 5 configurations = 35 experiments.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Model and configuration mapping
MODEL_MAP = {
    1: "llama3.2",
    2: "gemma3:4b",
    3: "qwen2.5-coder",
    4: "phi3:3.8b",
    5: "mistral:7b",
    6: "gpt-4o-mini",
    7: "gemini-flash-2.5-lite"
}

CONFIG_MAP = {
    1: "Zero-shot + Repair + Docstring",
    2: "Few-shot + Repair + Docstring",
    3: "Few-shot + No Repair + Docstring",
    4: "Few-shot + Repair + No Docstring",
    5: "Few-shot + No Repair + No Docstring"
}

CONFIG_SHORT = {
    1: "ZS+R+D",
    2: "FS+R+D",
    3: "FS+NR+D",
    4: "FS+R+ND",
    5: "FS+NR+ND"
}


def load_all_results(results_dir: Path) -> pd.DataFrame:
    """Load all result summary files and create a unified dataframe."""
    data = []
    
    for run_file in sorted(results_dir.glob("run_id_*_results_summary.json")):
        run_id = run_file.stem.replace("_results_summary", "")
        # Extract model and config from run_id (e.g., run_id_12 -> model=1, config=2)
        parts = run_id.split("_")
        if len(parts) >= 3:
            run_num = parts[2]  # e.g., "12"
            if len(run_num) >= 2:
                model_id = int(run_num[0])
                config_id = int(run_num[1])
                
                try:
                    with open(run_file, 'r') as f:
                        result = json.load(f)
                    
                    total = result.get("total_modules", 0)
                    passed = result.get("passed", 0)
                    failed = result.get("failed", 0)
                    pass_rate = (passed / total * 100) if total > 0 else 0
                    
                    token_stats = result.get("token_stats", {})
                    perf_stats = result.get("performance_stats", {})
                    repair_stats = result.get("repair_stats", {})
                    efficiency_stats = result.get("efficiency_stats", {})
                    
                    data.append({
                        "run_id": run_id,
                        "model_id": model_id,
                        "config_id": config_id,
                        "model": MODEL_MAP.get(model_id, f"model_{model_id}"),
                        "config": CONFIG_MAP.get(config_id, f"config_{config_id}"),
                        "config_short": CONFIG_SHORT.get(config_id, f"C{config_id}"),
                        "total_modules": total,
                        "passed": passed,
                        "failed": failed,
                        "pass_rate": pass_rate,
                        "passed_after_repair": result.get("passed_after_repair", 0),
                        "total_tokens": token_stats.get("total_tokens", 0),
                        "avg_tokens_per_module": token_stats.get("average_tokens_per_module", 0),
                        "tokens_per_passed_module": efficiency_stats.get("tokens_per_passed_module", 0),
                        "avg_time_per_module": perf_stats.get("average_time_per_module", 0),
                        "repair_iterations": repair_stats.get("total_repair_iterations", 0),
                        "repair_success_rate": repair_stats.get("repair_success_rate", 0),
                        "avg_tokens_per_repair": repair_stats.get("average_tokens_per_repair", 0),
                        "total_tests_passed": efficiency_stats.get("total_tests_passed", 0),
                        "total_tests_generated": efficiency_stats.get("total_tests_generated", 0),
                        "syntax_errors": result.get("by_failure_type", {}).get("syntax", 0),
                        "assertion_errors": result.get("by_failure_type", {}).get("assertion", 0),
                    })
                except Exception as e:
                    print(f"Error loading {run_file}: {e}")
    
    return pd.DataFrame(data)



def plot_overall_performance(df: pd.DataFrame, output_dir: Path):
    """Create overall performance comparison plots."""
    
    # 1. Bar chart: Pass rate by model (averaged across configs)
    plt.figure(figsize=(10, 6))
    model_avg = df.groupby("model")["pass_rate"].mean().sort_values(ascending=False)
    bars = plt.bar(range(len(model_avg)), model_avg.values, color=sns.color_palette("husl", len(model_avg)))
    plt.xticks(range(len(model_avg)), model_avg.index, rotation=45, ha='right')
    plt.ylabel("Pass Rate (%)")
    plt.title("Average Pass Rate by Model (Across All Configurations)")
    plt.grid(axis='y', alpha=0.3)
    for i, (bar, val) in enumerate(zip(bars, model_avg.values)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "overall_pass_rate_by_model.png", dpi=300, bbox_inches='tight')
    plt.close()

    
    # 2. Heatmap: Pass rate matrix (Models × Configurations)
    plt.figure(figsize=(12, 8))
    pivot = df.pivot_table(values="pass_rate", index="model", columns="config_short", aggfunc='mean')
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': 'Pass Rate (%)'})
    plt.title("Pass Rate Heatmap: Models × Configurations")
    plt.xlabel("Configuration")
    plt.ylabel("Model")
    plt.tight_layout()
    plt.savefig(output_dir / "overall_pass_rate_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()


    # 3. Grouped bar chart: Pass rates by configuration, grouped by model
    plt.figure(figsize=(12, 8))
    pivot_grouped = df.pivot_table(values="pass_rate", index="model", columns="config_short", aggfunc='mean')
    pivot_grouped.plot(kind='bar', width=0.8, figsize=(12, 8))
    plt.ylabel("Pass Rate (%)")
    plt.title("Pass Rate by Configuration (Grouped by Model)")
    plt.xlabel("Model")
    plt.legend(title="Configuration", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "overall_pass_rate_by_config.png", dpi=300, bbox_inches='tight')
    plt.close()

    
    # 4. Box plot: Pass rate distribution by model
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=df, x="model", y="pass_rate")
    plt.ylabel("Pass Rate (%)")
    plt.title("Pass Rate Distribution by Model")
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "overall_pass_rate_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()



def plot_ablation_repair(df: pd.DataFrame, output_dir: Path):
    """Create ablation study for repair mechanism."""
    
    # Only compare few-shot configurations
    with_repair_fs = df[df["config_id"].isin([2, 4])].copy()
    without_repair_fs = df[df["config_id"].isin([3, 5])].copy()
    
    # 1. Grouped bar chart: With/Without repair per model
    plt.figure(figsize=(12, 8))
    repair_comparison = []
    for model in df["model"].unique():
        # Handle missing data gracefully
        wr_data = with_repair_fs[with_repair_fs["model"] == model]
        wor_data = without_repair_fs[without_repair_fs["model"] == model]
        
        if not wr_data.empty and not wor_data.empty:
            with_repair_avg = wr_data["pass_rate"].mean()
            without_repair_avg = wor_data["pass_rate"].mean()
            repair_comparison.append({
                "model": model,
                "With Repair": with_repair_avg,
                "Without Repair": without_repair_avg
            })
    
    repair_df = pd.DataFrame(repair_comparison)
    if not repair_df.empty:
        x = np.arange(len(repair_df))
        width = 0.35
        plt.bar(x - width/2, repair_df["With Repair"], width, label="With Repair", color='#2ecc71')
        plt.bar(x + width/2, repair_df["Without Repair"], width, label="Without Repair", color='#e74c3c')
        plt.xticks(x, repair_df["model"], rotation=45, ha='right')
        plt.ylabel("Pass Rate (%)")
        plt.title("Effect of Repair Mechanism (Few-shot Configurations)")
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "ablation_repair_effect.png", dpi=300, bbox_inches='tight')
        plt.close()

    
    # 2. Improvement from repair
    plt.figure(figsize=(12, 8))
    improvements = []
    for model in df["model"].unique():
        wr_data = with_repair_fs[with_repair_fs["model"] == model]
        wor_data = without_repair_fs[without_repair_fs["model"] == model]
        
        if not wr_data.empty and not wor_data.empty:
            with_repair_avg = wr_data["pass_rate"].mean()
            without_repair_avg = wor_data["pass_rate"].mean()
            improvement = with_repair_avg - without_repair_avg
            improvements.append({"model": model, "improvement": improvement})
    
    imp_df = pd.DataFrame(improvements)
    if not imp_df.empty:
        bars = plt.bar(range(len(imp_df)), imp_df["improvement"].values, 
                       color=['#3498db' if x > 0 else '#e74c3c' for x in imp_df["improvement"].values])
        plt.xticks(range(len(imp_df)), imp_df["model"], rotation=45, ha='right')
        plt.ylabel("Improvement in Pass Rate (%)")
        plt.title("Improvement from Repair Mechanism")
        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        plt.grid(axis='y', alpha=0.3)
        for i, (bar, val) in enumerate(zip(bars, imp_df["improvement"].values)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.5 if val > 0 else -1.5),
                    f'{val:+.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)
        plt.tight_layout()
        plt.savefig(output_dir / "ablation_repair_improvement.png", dpi=300, bbox_inches='tight')
        plt.close()

    
    # 3. Repair success rate by model
    plt.figure(figsize=(12, 8))
    repair_success = df[df["config_id"].isin([1, 2, 4])].groupby("model")["repair_success_rate"].mean()
    bars = plt.bar(range(len(repair_success)), repair_success.values * 100, color='#9b59b6')
    plt.xticks(range(len(repair_success)), repair_success.index, rotation=45, ha='right')
    plt.ylabel("Repair Success Rate (%)")
    plt.title("Repair Success Rate by Model")
    plt.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars, repair_success.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val*100:.1f}%', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_repair_success_rate.png", dpi=300, bbox_inches='tight')
    plt.close()

    
    # 4. Box plot: Pass rate with/without repair
    plt.figure(figsize=(12, 8))
    comparison_data = []
    for _, row in with_repair_fs.iterrows():
        comparison_data.append({"model": row["model"], "condition": "With Repair", "pass_rate": row["pass_rate"]})
    for _, row in without_repair_fs.iterrows():
        comparison_data.append({"model": row["model"], "condition": "Without Repair", "pass_rate": row["pass_rate"]})
    comp_df = pd.DataFrame(comparison_data)
    if not comp_df.empty:
        sns.boxplot(data=comp_df, x="condition", y="pass_rate")
        plt.ylabel("Pass Rate (%)")
        plt.title("Pass Rate Distribution: With vs Without Repair")
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "ablation_repair_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()



def plot_ablation_docstrings(df: pd.DataFrame, output_dir: Path):
    """Create ablation study for docstrings."""
    
    # Only compare few-shot configurations
    with_docstring_fs = df[df["config_id"].isin([2, 3])].copy()
    without_docstring_fs = df[df["config_id"].isin([4, 5])].copy()
    
    # 1. Grouped bar chart: With/Without docstring per model
    plt.figure(figsize=(12, 8))
    docstring_comparison = []
    for model in df["model"].unique():
        wd_data = with_docstring_fs[with_docstring_fs["model"] == model]
        wod_data = without_docstring_fs[without_docstring_fs["model"] == model]
        
        if not wd_data.empty and not wod_data.empty:
            with_doc_avg = wd_data["pass_rate"].mean()
            without_doc_avg = wod_data["pass_rate"].mean()
            docstring_comparison.append({
                "model": model,
                "With Docstring": with_doc_avg,
                "Without Docstring": without_doc_avg
            })
    
    docstring_df = pd.DataFrame(docstring_comparison)
    if not docstring_df.empty:
        x = np.arange(len(docstring_df))
        width = 0.35
        plt.bar(x - width/2, docstring_df["With Docstring"], width, label="With Docstring", color='#3498db')
        plt.bar(x + width/2, docstring_df["Without Docstring"], width, label="Without Docstring", color='#f39c12')
        plt.xticks(x, docstring_df["model"], rotation=45, ha='right')
        plt.ylabel("Pass Rate (%)")
        plt.title("Effect of Docstrings (Few-shot Configurations)")
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "ablation_docstrings_effect.png", dpi=300, bbox_inches='tight')
        plt.close()

    
    # 2. Improvement from docstrings
    plt.figure(figsize=(12, 8))
    improvements = []
    for model in df["model"].unique():
        wd_data = with_docstring_fs[with_docstring_fs["model"] == model]
        wod_data = without_docstring_fs[without_docstring_fs["model"] == model]
        
        if not wd_data.empty and not wod_data.empty:
            with_doc_avg = wd_data["pass_rate"].mean()
            without_doc_avg = wod_data["pass_rate"].mean()
            improvement = with_doc_avg - without_doc_avg
            improvements.append({"model": model, "improvement": improvement})
    
    imp_df = pd.DataFrame(improvements)
    if not imp_df.empty:
        bars = plt.bar(range(len(imp_df)), imp_df["improvement"].values,
                       color=['#3498db' if x > 0 else '#e74c3c' for x in imp_df["improvement"].values])
        plt.xticks(range(len(imp_df)), imp_df["model"], rotation=45, ha='right')
        plt.ylabel("Improvement in Pass Rate (%)")
        plt.title("Improvement from Docstrings")
        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        plt.grid(axis='y', alpha=0.3)
        for i, (bar, val) in enumerate(zip(bars, imp_df["improvement"].values)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.5 if val > 0 else -1.5),
                    f'{val:+.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)
        plt.tight_layout()
        plt.savefig(output_dir / "ablation_docstrings_improvement.png", dpi=300, bbox_inches='tight')
        plt.close()

    
    # 3. Comparison across all models
    plt.figure(figsize=(12, 8))
    comparison_data = []
    for _, row in with_docstring_fs.iterrows():
        comparison_data.append({"model": row["model"], "condition": "With Docstring", "pass_rate": row["pass_rate"]})
    for _, row in without_docstring_fs.iterrows():
        comparison_data.append({"model": row["model"], "condition": "Without Docstring", "pass_rate": row["pass_rate"]})
    comp_df = pd.DataFrame(comparison_data)
    if not comp_df.empty:
        sns.boxplot(data=comp_df, x="condition", y="pass_rate")
        plt.ylabel("Pass Rate (%)")
        plt.title("Pass Rate Distribution: With vs Without Docstrings")
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "ablation_docstrings_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()

    
    # 4. Line chart: Docstring impact across models
    plt.figure(figsize=(12, 8))
    for model in df["model"].unique():
        with_doc = with_docstring_fs[with_docstring_fs["model"] == model]["pass_rate"].values
        without_doc = without_docstring_fs[without_docstring_fs["model"] == model]["pass_rate"].values
        if len(with_doc) > 0 and len(without_doc) > 0:
            plt.plot([0, 1], [without_doc.mean(), with_doc.mean()], 
                    marker='o', label=model, linewidth=2, markersize=8)
    plt.xticks([0, 1], ["Without Docstring", "With Docstring"])
    plt.ylabel("Pass Rate (%)")
    plt.title("Docstring Impact Across Models")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_docstrings_impact_line.png", dpi=300, bbox_inches='tight')
    plt.close()



def plot_zero_vs_few_shot(df: pd.DataFrame, output_dir: Path):
    """Compare zero-shot vs few-shot performance."""
    
    # Compare config 1 (zero-shot) vs config 2 (few-shot with same settings)
    zero_shot = df[df["config_id"] == 1].copy()
    few_shot = df[df["config_id"] == 2].copy()
    
    # 1. Grouped bar chart
    plt.figure(figsize=(10, 6))
    comparison = []
    for model in df["model"].unique():
        zs_rate = zero_shot[zero_shot["model"] == model]["pass_rate"].values
        fs_rate = few_shot[few_shot["model"] == model]["pass_rate"].values
        if len(zs_rate) > 0 and len(fs_rate) > 0:
            comparison.append({
                "model": model,
                "Zero-shot": zs_rate[0],
                "Few-shot": fs_rate[0]
            })
    
    comp_df = pd.DataFrame(comparison)
    if not comp_df.empty:
        x = np.arange(len(comp_df))
        width = 0.35
        plt.bar(x - width/2, comp_df["Zero-shot"], width, label="Zero-shot", color='#e67e22')
        plt.bar(x + width/2, comp_df["Few-shot"], width, label="Few-shot", color='#16a085')
        plt.xticks(x, comp_df["model"], rotation=45, ha='right')
        plt.ylabel("Pass Rate (%)")
        plt.title("Zero-shot vs Few-shot (Both with Repair + Docstring)")
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "zero_vs_few_shot_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()

    
    # 2. Improvement from few-shot
    plt.figure(figsize=(10, 6))
    improvements = []
    for model in df["model"].unique():
        zs_rate = zero_shot[zero_shot["model"] == model]["pass_rate"].values
        fs_rate = few_shot[few_shot["model"] == model]["pass_rate"].values
        if len(zs_rate) > 0 and len(fs_rate) > 0:
            improvement = fs_rate[0] - zs_rate[0]
            improvements.append({"model": model, "improvement": improvement})
    
    imp_df = pd.DataFrame(improvements)
    if not imp_df.empty:
        bars = plt.bar(range(len(imp_df)), imp_df["improvement"].values,
                       color=['#16a085' if x > 0 else '#e74c3c' for x in imp_df["improvement"].values])
        plt.xticks(range(len(imp_df)), imp_df["model"], rotation=45, ha='right')
        plt.ylabel("Improvement in Pass Rate (%)")
        plt.title("Improvement from Few-shot Learning")
        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        plt.grid(axis='y', alpha=0.3)
        for i, (bar, val) in enumerate(zip(bars, imp_df["improvement"].values)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.5 if val > 0 else -1.5),
                    f'{val:+.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)
        plt.tight_layout()
        plt.savefig(output_dir / "zero_vs_few_shot_improvement.png", dpi=300, bbox_inches='tight')
        plt.close()




def generate_statistical_summary(df: pd.DataFrame, output_dir: Path):
    """Generate statistical summary tables and JSON."""
    tables_dir = output_dir.parent / "tables"
    tables_dir.mkdir(exist_ok=True)
    stats_dir = output_dir.parent / "statistics"
    stats_dir.mkdir(exist_ok=True)
    
    # Table 1: Overall Performance
    perf_table = df.sort_values(["model", "config_id"])[["model", "config_short", "total_modules", "passed", "failed", "pass_rate"]].copy()
    perf_table.to_csv(tables_dir / "performance_summary.csv", index=False)
    
    # Table 2: Ablation Results
    ablation_data = []
    for model in df["model"].unique():
        # Repair ablation
        with_repair = df[(df["model"] == model) & (df["config_id"].isin([2, 4]))]["pass_rate"].mean()
        without_repair = df[(df["model"] == model) & (df["config_id"].isin([3, 5]))]["pass_rate"].mean()
        repair_improvement = with_repair - without_repair
        
        # Docstring ablation
        with_doc = df[(df["model"] == model) & (df["config_id"].isin([2, 3]))]["pass_rate"].mean()
        without_doc = df[(df["model"] == model) & (df["config_id"].isin([4, 5]))]["pass_rate"].mean()
        doc_improvement = with_doc - without_doc
        
        # Few-shot vs Zero-shot
        zs = df[(df["model"] == model) & (df["config_id"] == 1)]["pass_rate"].values
        fs = df[(df["model"] == model) & (df["config_id"] == 2)]["pass_rate"].values
        fs_improvement = (fs[0] - zs[0]) if len(zs) > 0 and len(fs) > 0 else 0
        
        ablation_data.append({
            "model": model,
            "repair_baseline": without_repair,
            "repair_with": with_repair,
            "repair_improvement": repair_improvement,
            "repair_improvement_pct": (repair_improvement / without_repair * 100) if without_repair > 0 else 0,
            "docstring_baseline": without_doc,
            "docstring_with": with_doc,
            "docstring_improvement": doc_improvement,
            "docstring_improvement_pct": (doc_improvement / without_doc * 100) if without_doc > 0 else 0,
            "zero_shot": zs[0] if len(zs) > 0 else 0,
            "few_shot": fs[0] if len(fs) > 0 else 0,
            "few_shot_improvement": fs_improvement,
            "few_shot_improvement_pct": (fs_improvement / zs[0] * 100) if len(zs) > 0 and zs[0] > 0 else 0
        })
    
    ablation_df = pd.DataFrame(ablation_data)
    ablation_df.to_csv(tables_dir / "ablation_results.csv", index=False)
    
    # Table 3: Efficiency Metrics
    eff_table = df.sort_values(["model", "config_id"])[["model", "config_short", "avg_tokens_per_module", 
                    "tokens_per_passed_module", "avg_time_per_module"]].copy()
    eff_table.to_csv(tables_dir / "efficiency_metrics.csv", index=False)
    
    # Statistical summary JSON
    summary = {
        "overall_statistics": {
            "mean_pass_rate": float(df["pass_rate"].mean()),
            "std_pass_rate": float(df["pass_rate"].std()),
            "min_pass_rate": float(df["pass_rate"].min()),
            "max_pass_rate": float(df["pass_rate"].max())
        },
        "by_model": {},
        "by_configuration": {},
        "ablation_summary": {
            "repair_avg_improvement": float(ablation_df["repair_improvement"].mean()),
            "docstring_avg_improvement": float(ablation_df["docstring_improvement"].mean()),
            "few_shot_avg_improvement": float(ablation_df["few_shot_improvement"].mean())
        }
    }
    
    for model in df["model"].unique():
        model_data = df[df["model"] == model]
        summary["by_model"][model] = {
            "mean_pass_rate": float(model_data["pass_rate"].mean()),
            "std_pass_rate": float(model_data["pass_rate"].std()),
            "best_config": model_data.loc[model_data["pass_rate"].idxmax(), "config_short"],
            "best_pass_rate": float(model_data["pass_rate"].max())
        }
    
    for config in df["config_short"].unique():
        config_data = df[df["config_short"] == config]
        summary["by_configuration"][config] = {
            "mean_pass_rate": float(config_data["pass_rate"].mean()),
            "std_pass_rate": float(config_data["pass_rate"].std())
        }
    
    with open(stats_dir / "summary_statistics.json", 'w') as f:
        json.dump(summary, f, indent=2)
    



def main():
    results_dir = Path("results_summary")
    output_dir = Path("plots")
    output_dir.mkdir(exist_ok=True)
    
    df = load_all_results(results_dir)
    
    if df.empty:
        return
    
    plot_overall_performance(df, output_dir)
    plot_ablation_repair(df, output_dir)
    plot_ablation_docstrings(df, output_dir)
    plot_zero_vs_few_shot(df, output_dir)
    
    # print("\nGenerating statistical summaries...")
    generate_statistical_summary(df, output_dir)
    

if __name__ == "__main__":
    main()

