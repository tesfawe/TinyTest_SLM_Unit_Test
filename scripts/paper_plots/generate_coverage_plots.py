"""
generate_coverage_plots.py

Generate comprehensive code coverage visualizations and statistics for research paper.
Analyzes coverage data across models and configurations.
"""

import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 12)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

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


def parse_coverage_file(filepath: str) -> Optional[Dict[str, float]]:
    """
    Parses a coverage summary file to extract detailed coverage information.
    Expected format last line: "TOTAL 1187 108 91%"
    
    Returns:
        Dictionary with 'coverage', 'total_statements', 'missed_statements' or None
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        # Look for the TOTAL line
        for line in reversed(lines):
            if line.strip().startswith('TOTAL'):
                parts = line.split()
                # Expected parts: ['TOTAL', '1187', '108', '91%']
                if len(parts) >= 4:
                    total_statements = int(parts[1])
                    missed_statements = int(parts[2])
                    percent_str = parts[-1].replace('%', '')
                    coverage = float(percent_str)
                    return {
                        'coverage': coverage,
                        'total_statements': total_statements,
                        'missed_statements': missed_statements
                    }
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def extract_model_config(run_id: int) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract model_id and config_id from run_id.
    run_id format: XY where X is model_id (1-7) and Y is config_id (1-5)
    """
    run_str = str(run_id)
    if len(run_str) >= 2:
        model_id = int(run_str[0])
        config_id = int(run_str[1])
        if model_id in MODEL_MAP and config_id in CONFIG_MAP:
            return model_id, config_id
    return None, None


def load_coverage_data(coverage_dir: str) -> pd.DataFrame:
    """Load all coverage files and create a unified dataframe."""
    pattern = os.path.join(coverage_dir, "coverage_summary_run_id_*.txt")
    files = glob.glob(pattern)
    
    data = []
    data = []
    data = []
    
    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        # Extract run_id from filename
        match = re.search(r'run_id_(\d+)', filename)
        if match:
            run_id = int(match.group(1))
            coverage_data = parse_coverage_file(filepath)
            
            if coverage_data is not None:
                model_id, config_id = extract_model_config(run_id)
                
                row = {
                    'run_id': run_id,
                    'coverage': coverage_data['coverage'],
                    'total_statements': coverage_data['total_statements'],
                    'missed_statements': coverage_data['missed_statements']
                }
                
                if model_id and config_id:
                    row['model_id'] = model_id
                    row['config_id'] = config_id
                    row['model'] = MODEL_MAP[model_id]
                    row['config'] = CONFIG_MAP[config_id]
                    row['config_short'] = CONFIG_SHORT[config_id]
                else:
                    row['model_id'] = None
                    row['config_id'] = None
                    row['model'] = f"Unknown (run_id_{run_id})"
                    row['config'] = "Unknown"
                    row['config_short'] = "Unknown"
                
                data.append(row)
            else:
                print(f"Could not extract coverage from {filename}")
    
    if not data:
        print("No valid data found.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df = df.sort_values('run_id')
    
    return df


def plot_coverage_distribution(df: pd.DataFrame, output_dir: Path):
    """Create distribution plot with enhanced statistics."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Histogram with KDE
    sns.histplot(df['coverage'], kde=True, bins=15, color='#3498db', alpha=0.7, edgecolor='black', ax=ax)
    
    # Add statistical lines
    mean_coverage = df['coverage'].mean()
    median_coverage = df['coverage'].median()
    std_coverage = df['coverage'].std()
    
    ax.axvline(mean_coverage, color='red', linestyle='--', linewidth=2, 
               label=f"Mean: {mean_coverage:.2f}%")
    ax.axvline(median_coverage, color='green', linestyle='-', linewidth=2, 
               label=f"Median: {median_coverage:.2f}%")
    ax.axvline(mean_coverage + std_coverage, color='orange', linestyle=':', linewidth=1.5, 
               alpha=0.7, label=f"±1σ: {mean_coverage + std_coverage:.2f}%")
    ax.axvline(mean_coverage - std_coverage, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
    
    ax.set_title('Distribution of Code Coverage across All Experiments', fontweight='bold', pad=15)
    ax.set_xlabel('Coverage (%)', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax.grid(axis='y', alpha=0.3)
    
    # Ensure everything fits
    ax.set_xlim(left=0)
    plt.tight_layout(pad=2.0)
    plt.savefig(output_dir / "coverage_distribution.png", dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close()



def plot_coverage_by_model(df: pd.DataFrame, output_dir: Path):
    """Create coverage analysis by model using bar plots with labels."""
    if 'model' not in df.columns or df['model'].isna().all():
        return
    
    # Filter out unknown models
    df_known = df[df['model_id'].notna()].copy()
    if df_known.empty:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate means
    model_avg = df_known.groupby('model')['coverage'].mean().sort_values(ascending=False)
    
    # Create bar plot
    bars = ax.bar(range(len(model_avg)), model_avg.values, color=sns.color_palette("husl", len(model_avg)))
    
    # Customize axis
    ax.set_xticks(range(len(model_avg)))
    ax.set_xticklabels(model_avg.index, rotation=45, ha='right')
    ax.set_title('Average Code Coverage by Model', fontweight='bold', pad=15)
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_ylabel('Coverage (%)', fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Set Y-axis to standard 0-110 range (to fit labels)
    ax.set_ylim(0, 110)
    
    plt.tight_layout(pad=2.0)
    plt.savefig(output_dir / "coverage_by_model.png", dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close()



def plot_coverage_by_config(df: pd.DataFrame, output_dir: Path):
    """Create coverage analysis by configuration using bar plots with labels."""
    if 'config_short' not in df.columns or df['config_short'].isna().all():
        return
    
    df_known = df[df['config_id'].notna()].copy()
    if df_known.empty:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate means
    config_avg = df_known.groupby('config_short')['coverage'].mean().sort_values(ascending=False)
    
    # Create bar plot
    bars = ax.bar(range(len(config_avg)), config_avg.values, color=sns.color_palette("Set2", len(config_avg)))
    
    # Customize axis
    ax.set_xticks(range(len(config_avg)))
    ax.set_xticklabels(config_avg.index, rotation=0)
    ax.set_title('Average Code Coverage by Configuration', fontweight='bold', pad=15)
    ax.set_xlabel('Configuration', fontweight='bold')
    ax.set_ylabel('Coverage (%)', fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Set Y-axis
    ax.set_ylim(0, 110)
    
    plt.tight_layout(pad=2.0)
    plt.savefig(output_dir / "coverage_by_config.png", dpi=600, bbox_inches='tight', pad_inches=0.2)
    plt.close()



def plot_coverage_heatmap(df: pd.DataFrame, output_dir: Path):
    """Create heatmap: Coverage by Model × Configuration."""
    if 'model' not in df.columns or 'config_short' not in df.columns:
        print("⚠ Skipping heatmap: model/config information not available")
        return
    
    df_known = df[(df['model_id'].notna()) & (df['config_id'].notna())].copy()
    if df_known.empty:
        print("⚠ Skipping heatmap: no known model/config combinations")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    pivot = df_known.pivot_table(values='coverage', index='model', columns='config_short', aggfunc='mean')
    
    # Create heatmap
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', 
                cbar_kws={'label': 'Coverage (%)', 'shrink': 0.8},
                linewidths=0.5, linecolor='gray', square=False, ax=ax)
    
    ax.set_title('Code Coverage Heatmap: Models × Configurations', fontweight='bold', pad=15)
    ax.set_xlabel('Configuration', fontweight='bold')
    ax.set_ylabel('Model', fontweight='bold')
    
    plt.tight_layout(pad=2.0)
    plt.savefig(output_dir / "coverage_heatmap.png", dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close()



def generate_statistical_summary(df: pd.DataFrame, output_dir: Path):
    """Generate comprehensive statistical summary tables."""
    tables_dir = output_dir.parent / "tables"
    tables_dir.mkdir(exist_ok=True)
    
    # 1. Overall statistics
    overall_stats = df['coverage'].describe()
    overall_stats['median'] = df['coverage'].median()
    overall_stats['std'] = df['coverage'].std()
    overall_stats.to_csv(tables_dir / "coverage_statistics.csv")
    
    # 2. Detailed coverage data
    df.to_csv(output_dir / "coverage_data.csv", index=False)
    
    # 3. Coverage by model (if available)
    if 'model' in df.columns and df['model_id'].notna().any():
        df_known = df[df['model_id'].notna()].copy()
        model_stats = df_known.groupby('model')['coverage'].agg([
            'count', 'mean', 'std', 'min', 'max', 'median'
        ]).round(2)
        model_stats.columns = ['N', 'Mean', 'Std', 'Min', 'Max', 'Median']
        model_stats.to_csv(tables_dir / "coverage_by_model.csv")
        
        # LaTeX table
        latex_table = model_stats.to_latex(float_format="%.2f", caption="Code Coverage Statistics by Model")
        with open(tables_dir / "coverage_by_model.tex", 'w') as f:
            f.write(latex_table)
    
    # 4. Coverage by configuration (if available)
    if 'config_short' in df.columns and df['config_id'].notna().any():
        df_known = df[df['config_id'].notna()].copy()
        config_stats = df_known.groupby('config_short')['coverage'].agg([
            'count', 'mean', 'std', 'min', 'max', 'median'
        ]).round(2)
        config_stats.columns = ['N', 'Mean', 'Std', 'Min', 'Max', 'Median']
        config_stats.to_csv(tables_dir / "coverage_by_config.csv")
        
        # LaTeX table
        latex_table = config_stats.to_latex(float_format="%.2f", caption="Code Coverage Statistics by Configuration")
        with open(tables_dir / "coverage_by_config.tex", 'w') as f:
            f.write(latex_table)
    
    # 5. Combined model × config table
    if 'model' in df.columns and 'config_short' in df.columns:
        df_known = df[(df['model_id'].notna()) & (df['config_id'].notna())].copy()
        if not df_known.empty:
            combined = df_known.groupby(['model', 'config_short'])['coverage'].agg(['mean', 'std']).round(2)
            combined.columns = ['Mean Coverage', 'Std Coverage']
            combined.to_csv(tables_dir / "coverage_by_model_config.csv")
    



def perform_statistical_tests(df: pd.DataFrame, output_dir: Path):
    """Perform statistical significance tests for ablation studies."""
    if 'model_id' not in df.columns or 'config_id' not in df.columns:
        print("⚠ Skipping statistical tests: model/config information not available")
        return
    
    df_known = df[(df['model_id'].notna()) & (df['config_id'].notna())].copy()
    if df_known.empty:
        print("⚠ Skipping statistical tests: no known model/config combinations")
        return
    
    results = []
    
    # Test 1: Repair effect
    with_repair = df_known[df_known['config_id'].isin([2, 4])]['coverage'].values
    without_repair = df_known[df_known['config_id'].isin([3, 5])]['coverage'].values
    if len(with_repair) > 0 and len(without_repair) > 0:
        t_stat, p_value = stats.ttest_ind(with_repair, without_repair)
        results.append({
            'Test': 'Repair Effect',
            'Group1': 'With Repair (FS+R+D, FS+R+ND)',
            'Group2': 'Without Repair (FS+NR+D, FS+NR+ND)',
            'Mean1': with_repair.mean(),
            'Mean2': without_repair.mean(),
            'T-statistic': t_stat,
            'P-value': p_value,
            'Significant': 'Yes' if p_value < 0.05 else 'No'
        })
    
    # Test 2: Docstring effect
    with_doc = df_known[df_known['config_id'].isin([2, 3])]['coverage'].values
    without_doc = df_known[df_known['config_id'].isin([4, 5])]['coverage'].values
    if len(with_doc) > 0 and len(without_doc) > 0:
        t_stat, p_value = stats.ttest_ind(with_doc, without_doc)
        results.append({
            'Test': 'Docstring Effect',
            'Group1': 'With Docstring (FS+R+D, FS+NR+D)',
            'Group2': 'Without Docstring (FS+R+ND, FS+NR+ND)',
            'Mean1': with_doc.mean(),
            'Mean2': without_doc.mean(),
            'T-statistic': t_stat,
            'P-value': p_value,
            'Significant': 'Yes' if p_value < 0.05 else 'No'
        })
    
    if results:
        stats_df = pd.DataFrame(results)
        stats_df.to_csv(output_dir / "coverage_statistical_tests.csv", index=False)



def main():
    coverage_dir = "coverage_summary"
    output_dir = Path("coverage_stats")
    output_dir.mkdir(exist_ok=True)
    

    
    # Load data
    df = load_coverage_data(coverage_dir)
    
    if df.empty:
        print("Error: No valid data found.")
        return
    
    # Statistics summary

    
    # Generate plots
    plot_coverage_distribution(df, output_dir)
    plot_coverage_by_model(df, output_dir)
    plot_coverage_by_config(df, output_dir)
    plot_coverage_heatmap(df, output_dir)
    
    # Generate statistics
    generate_statistical_summary(df, output_dir)
    perform_statistical_tests(df, output_dir)
    



if __name__ == "__main__":
    main()
