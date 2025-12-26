"""
generate_mutmut_plots.py

Parses mutmut_run_score.txt and generates visualizations for the paper.
Now includes detailed breakdown of mutation outcomes and efficiency metrics.
"""

import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# Maps
MODEL_MAP = {
    1: "llama3.2",
    2: "gemma3:4b",
    3: "qwen2.5-coder",
    4: "phi3:3.8b",
    5: "mistral:7b",
    6: "gpt-4o-mini",
    7: "gemini-flash-2.5-lite"
}

CONFIG_SHORT = {
    1: "ZS+R+D",
    2: "FS+R+D",
    3: "FS+NR+D",
    4: "FS+R+ND",
    5: "FS+NR+ND"
}

def parse_line(line):
    """
    Parses a single line from mutmut_run_score.txt.
    Shape: '11: 2551/2551  🎉 2011 🫥 59  ⏰ 27  🤔 0  🙁 454  🔇 0 29.99 mutations/second'
    """
    # Regex to capture:
    # 1. Run ID
    # 2. Total
    # 3. 🎉 Killed
    # 4. 🫥 Survived
    # 5. ⏰ Timeout
    # 6. 🤔 Suspicious
    # 7. 🙁 Skipped/Error (often "skipped")
    # 8. Rate (float)
    
    # 11: 2551/2551  🎉 2011 🫥 59  ⏰ 27  🤔 0  🙁 454  🔇 0 29.99 mutations/second
    regex = r'^(\d+):\s+(\d+)/(\d+)\s+🎉\s+(\d+)\s+🫥\s+(\d+)\s+⏰\s+(\d+)\s+🤔\s+(\d+)\s+🙁\s+(\d+).*?([\d\.]+)\s+mutations/second'
    
    match = re.search(regex, line)
    if not match:
        return None
    
    run_id_str = match.group(1)
    total = int(match.group(3))
    killed = int(match.group(4))
    survived = int(match.group(5))
    timeout = int(match.group(6))
    suspicious = int(match.group(7))
    skipped = int(match.group(8))
    rate = float(match.group(9))
    
    if len(run_id_str) < 2:
        return None
        
    try:
        model_id = int(run_id_str[0])
        config_id = int(run_id_str[1])
    except ValueError:
        return None
        
    return {
        "model_id": model_id,
        "config_id": config_id,
        "total": total,
        "killed": killed,
        "survived": survived,
        "timeout": timeout,
        "suspicious": suspicious,
        "skipped": skipped,
        "rate_mut_sec": rate,
        "score": (killed / total) * 100 if total > 0 else 0
    }

def load_data(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            parsed = parse_line(line.strip())
            if parsed:
                if parsed['model_id'] in MODEL_MAP and parsed['config_id'] in CONFIG_SHORT:
                    parsed['model_name'] = MODEL_MAP[parsed['model_id']]
                    parsed['config_name'] = CONFIG_SHORT[parsed['config_id']]
                    data.append(parsed)
    return pd.DataFrame(data)

def plot_heatmap(df, output_dir):
    plt.figure(figsize=(10, 6))
    pivot = df.pivot_table(index="model_name", columns="config_name", values="score")
    
    sorted_models = [MODEL_MAP[i] for i in sorted(MODEL_MAP.keys()) if MODEL_MAP[i] in pivot.index]
    sorted_configs = [CONFIG_SHORT[i] for i in sorted(CONFIG_SHORT.keys()) if CONFIG_SHORT[i] in pivot.columns]
    
    pivot = pivot.reindex(index=sorted_models, columns=sorted_configs)

    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", cbar_kws={'label': 'Mutation Score (%)'})
    plt.title("Mutation Score Heatmap (Killed / Total)")
    plt.tight_layout()
    plt.savefig(output_dir / "mutmut_heatmap.png", dpi=300)
    plt.close()

def plot_grouped_bar(df, output_dir):
    plt.figure(figsize=(18, 8))
    
    df['model_sort'] = df['model_id']
    df['config_sort'] = df['config_id']
    df = df.sort_values(['model_sort', 'config_sort'])
    
    # Create the text annotations manually
    ax = sns.barplot(data=df, x="model_name", y="score", hue="config_name", palette="viridis")
    
    # Add percentage labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', fontsize=9, padding=3)

    plt.ylabel("Mutation Score (%)")
    plt.xlabel("Model")
    plt.title("Mutation Score by Model and Configuration")
    plt.legend(title="Configuration", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(output_dir / "mutmut_grouped_bar.png", dpi=300)
    plt.close()

def plot_stacked_outcomes(df, output_dir):
    """
    Stacked bar chart showing % of Killed, Survived, Timeout, Skipped/Other
    """
    plt.figure(figsize=(14, 8))
    
    # Calculate percentages
    df['pct_killed'] = df['killed'] / df['total'] * 100
    df['pct_survived'] = df['survived'] / df['total'] * 100
    df['pct_timeout'] = df['timeout'] / df['total'] * 100
    df['pct_skipped'] = (df['skipped'] + df['suspicious']) / df['total'] * 100 # Group suspicious with skipped for simplicity or keep separate
    
    # We want one bar per (Model, Config) tuple, but that's too crowded.
    # Let's facet by Model or just plot everything on x-axis if there aren't too many.
    # There are 7 models * 5 configs = 35 bars. A bit crowded but doable.
    
    df['label'] = df['model_name'] + "\n" + df['config_name']
    
    # Sort
    df = df.sort_values(['model_id', 'config_id'])
    
    x = range(len(df))
    width = 0.85
    
    p1 = plt.bar(x, df['pct_killed'], width, label='Killed', color='#2ecc71')
    p2 = plt.bar(x, df['pct_survived'], width, bottom=df['pct_killed'], label='Survived', color='#e74c3c')
    p3 = plt.bar(x, df['pct_timeout'], width, bottom=df['pct_killed']+df['pct_survived'], label='Timeout', color='#f1c40f')
    p4 = plt.bar(x, df['pct_skipped'], width, bottom=df['pct_killed']+df['pct_survived']+df['pct_timeout'], label='Skipped/Suspicious', color='#95a5a6')
    
    plt.ylabel('Percentage (%)')
    plt.title('Distribution of Mutation Outcomes')
    plt.xticks(x, df['config_name'], rotation=90)
    
    # Add a second x-axis for Model grouping if possible, but for now simple labels
    # Let's simplify and just use Config as tick and group visually by separating models?
    # Or just X-axis = "Model - Config"
    plt.xticks(x, df['label'], rotation=90, fontsize=8)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(output_dir / "mutmut_outcomes_stacked.png", dpi=300)
    plt.close()

def plot_efficiency(df, output_dir):
    """
    Scatter plot: Mutation Score vs Mutation Rate
    """
    plt.figure(figsize=(10, 8))
    
    sns.scatterplot(
        data=df, 
        x="rate_mut_sec", 
        y="score", 
        hue="model_name", 
        style="config_name", 
        s=100,
        alpha=0.8
    )
    
    plt.xlabel("Mutation Rate (mutations/second)")
    plt.ylabel("Mutation Score (%)")
    plt.title("Efficiency Analysis: Effectiveness vs Speed")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(output_dir / "mutmut_efficiency_scatter.png", dpi=300)
    plt.close()

def main():
    input_file = Path("mutmut_run_score.txt")
    output_dir = Path("mutmut_plots")
    output_dir.mkdir(exist_ok=True)
    
    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        return

    df = load_data(input_file)
    if df.empty:
        print("No valid data found in file.")
        return
        
    print(f"Loaded {len(df)} records.")
    
    # Save detailed CSV
    # Reorder columns for readability
    cols = ['model_name', 'config_name', 'total', 'killed', 'survived', 'timeout', 'suspicious', 'skipped', 'score', 'rate_mut_sec']
    df[cols].to_csv(output_dir / "mutmut_detailed_stats.csv", index=False)
    print(f"Saved detailed stats to {output_dir}/mutmut_detailed_stats.csv")
    
    plot_heatmap(df, output_dir)
    plot_grouped_bar(df, output_dir)
    plot_stacked_outcomes(df, output_dir)
    plot_efficiency(df, output_dir)
    print(f"Plots saved to {output_dir}/")

if __name__ == "__main__":
    main()
