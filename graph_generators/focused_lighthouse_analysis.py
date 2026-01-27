#!/usr/bin/env python3
"""
Focused Lighthouse Analysis for IDE Comparison
Generates key visualizations for thesis analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def load_and_prepare_data(csv_path):
    df = pd.read_csv(csv_path)
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Overall_Score'] = df[score_columns].mean(axis=1)
    return df

def create_key_visualizations(df, output_dir):
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    plt.style.use('default')
    sns.set_palette("Set2")

    # 1. Overall Performance Comparison (Bar Chart)
    plt.figure(figsize=(12, 8))
    ide_performance = df.groupby('IDE')['Overall_Score'].mean().sort_values(ascending=False)
    bars = plt.bar(range(len(ide_performance)), ide_performance.values, 
                   color=['#2E8B57', '#4169E1', '#DC143C', '#FF8C00', '#9932CC'])
    for i, (ide, value) in enumerate(ide_performance.items()):
        plt.text(i, value + 0.5, f'{value:.1f}', ha='center', va='bottom', 
                fontweight='bold', fontsize=12)
    plt.title('Overall IDE Performance Comparison\n(Average Lighthouse Score)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Average Score', fontsize=12)
    plt.xlabel('IDE', fontsize=12)
    plt.xticks(range(len(ide_performance)), ide_performance.index.str.upper())
    plt.ylim(85, 100)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'overall_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Metric-wise Comparison (Grouped Bar Chart)
    fig, ax = plt.subplots(figsize=(14, 8))
    metrics = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    metric_names = ['Performance', 'Accessibility', 'Best Practices', 'SEO']
    ide_means = df.groupby('IDE')[metrics].mean()
    x = np.arange(len(metric_names))
    width = 0.15
    multiplier = 0
    colors = ['#2E8B57', '#4169E1', '#DC143C', '#FF8C00', '#9932CC']
    for i, (ide, color) in enumerate(zip(ide_means.index, colors)):
        offset = width * multiplier
        values = ide_means.loc[ide].values
        bars = ax.bar(x + offset, values, width, label=ide.upper(), color=color, alpha=0.8)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        multiplier += 1
    ax.set_xlabel('Lighthouse Metrics', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('IDE Performance by Lighthouse Metric', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(metric_names)
    ax.legend(title='IDE', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_ylim(70, 105)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'metric_wise_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Score Distribution Box Plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Score Distribution by IDE', fontsize=16, fontweight='bold')
    for i, (metric, name) in enumerate(zip(metrics, metric_names)):
        ax = axes[i//2, i%2]
        sns.boxplot(data=df, x='IDE', y=metric, ax=ax, palette='Set2')
        ax.set_title(f'{name}', fontweight='bold')
        ax.set_ylabel('Score')
        ax.set_xlabel('IDE')
        ax.set_ylim(70, 105)
        ax.tick_params(axis='x', rotation=45)
        for j, ide in enumerate(df['IDE'].unique()):
            ide_data = df[df['IDE'] == ide][metric]
            mean_val = ide_data.mean()
            ax.scatter(j, mean_val, color='red', s=80, marker='D', zorder=5)
    plt.tight_layout()
    plt.savefig(output_dir / 'score_distribution_boxplots.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Heatmap of Average Scores
    plt.figure(figsize=(10, 6))
    heatmap_data = df.groupby('IDE')[metrics].mean()
    heatmap_data.columns = metric_names
    sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', center=90, 
                vmin=80, vmax=100, fmt='.1f', 
                cbar_kws={'label': 'Score'}, square=True)
    plt.title('IDE Performance Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('IDE')
    plt.xlabel('Lighthouse Metric')
    plt.tight_layout()
    plt.savefig(output_dir / 'performance_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Generate Summary Table
    summary_stats = df.groupby('IDE')[metrics + ['Overall_Score']].agg(['mean', 'std']).round(2)
    summary_stats.to_csv(output_dir / 'ide_performance_summary.csv')
    print(f"All visualizations saved to: {output_dir}")
    print(f"Summary statistics saved to: {output_dir}/ide_performance_summary.csv")



def run_all_lighthouse_analyses():
    use_cases = [
        'AUTH_TEST',
        'CHAT_TEST',
        'FILE_UPLOAD_TEST',
        'TASKS_QUEUE_TEST',
        'CRUD_2_TEST'
    ]
    import os
    from pathlib import Path
    for folder in use_cases:
        root_dir = Path(__file__).resolve().parent.parent
        folder_path = root_dir / folder
        csv_path = folder_path / 'lighthouse_stats.csv'
        output_dir = folder_path / 'graphs' / 'lighthouse_analysis'
        if not csv_path.exists():
            print(f"⚠ Saltato {folder}: file {csv_path} non trovato")
            continue
        print(f"\n📊 Analisi Lighthouse per {folder}...")
        df = load_and_prepare_data(csv_path)
        create_key_visualizations(df, output_dir)
        # Warnings count barplots (per messaggio, split su virgola)
        plot_lighthouse_warnings(csv_path, output_dir / 'warnings_messages_summary.png')

def plot_lighthouse_warnings(lighthouse_csv, output_path):
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.read_csv(lighthouse_csv)
    note_cols = [
        ("Performance_Notes", "Performance Warnings", "lightcoral"),
        ("Accessibility_Notes", "Accessibility Warnings", "skyblue"),
        ("Best Practices_Notes", "Best Practices Warnings", "lightgreen"),
        ("SEO_Notes", "SEO Warnings", "#E2CE5EFD"),  # oro, più visibile
    ]
    fig, ax = plt.subplots(2, 2, figsize=(16, 10), facecolor="#f2f2f2")
    for i, (col, title, color) in enumerate(note_cols):
        # Conta i warning per IDE (split su virgola)
        warning_counts = df.groupby('IDE')[col].apply(
            lambda notes: notes.dropna().apply(lambda x: len([w for w in str(x).split(',') if w.strip() != ''])).sum()
        )
        ax_ = ax[i // 2, i % 2]
        bars = ax_.bar(warning_counts.index, warning_counts.values, color=color, alpha=0.8)
        for bar, value in zip(bars, warning_counts.values):
            ax_.text(bar.get_x() + bar.get_width()/2, value + 0.1, f'{int(value)}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        ax_.set_title(title)
        ax_.set_xlabel("IDE")
        ax_.set_ylabel("Number of Warnings")
        ax_.set_ylim(0, max(warning_counts.values.max() + 1, 3))
        # Tick solo interi
        ax_.set_yticks(range(0, int(max(warning_counts.values.max() + 1, 3)) + 1, 1))
        ax_.grid(axis='y', alpha=0.15)
        ax_.set_facecolor("#f2f2f2")
        for spine in ["top", "right"]:
            ax_.spines[spine].set_visible(False)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

def plot_warnings_count_by_ide(df, output_dir):
    """Crea 4 barplot (uno per metrica) con il conteggio dei warnings per IDE, con numeri sopra le barre e colori diversi."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Lighthouse Warnings Overview by IDE and Category', fontsize=16, fontweight='bold')
    metrics = [
        ('Performance_Warnings', 'Performance', '#f08080'),
        ('Accessibility_Warnings', 'Accessibility', '#87ceeb'),
        ('Best_Practices_Warnings', 'Best Practices', '#90ee90'),
        ('SEO_Warnings', 'SEO', '#ffffcc')
    ]
    # Calcola il numero di warning per riga (split su virgola, ignora vuoti)
    for col, _, _ in metrics:
        if col in df.columns:
            df[col + '_count'] = df[col].fillna('').apply(lambda x: len([w for w in str(x).split(',') if w.strip() != '']))
    for i, (col, name, color) in enumerate(metrics):
        ax = axes[i//2, i%2]
        count_col = col + '_count'
        if count_col not in df.columns:
            ax.axis('off')
            continue
        counts = df.groupby('IDE')[count_col].sum()
        bars = ax.bar(counts.index, counts.values, color=color, alpha=0.7)
        for bar, value in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, value + 0.1, f'{int(value)}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        ax.set_title(f'{name} Warnings Count by IDE', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Warnings')
        ax.set_xlabel('IDE')
        ax.set_ylim(0, max(counts.values.max() + 1, 3))
        ax.grid(axis='y', alpha=0.15)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(Path(output_dir) / 'warnings_count_by_ide.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Lighthouse IDE Performance Analysis")
    print("=" * 40)
    try:
        run_all_lighthouse_analyses()
        print("\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
