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

def load_and_prepare_data():
    """Load and prepare the lighthouse data."""
    df = pd.read_csv("frontend_results.csv")
    
    # Ensure numeric columns are properly typed
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate overall score
    df['Overall_Score'] = df[score_columns].mean(axis=1)
    
    return df

def create_key_visualizations():
    """Create the most important visualizations for IDE comparison."""
    
    df = load_and_prepare_data()
    
    # Create output directory
    output_dir = Path("lighthouse_analysis")
    output_dir.mkdir(exist_ok=True)
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("Set2")
    
    # 1. Overall Performance Comparison (Bar Chart)
    plt.figure(figsize=(12, 8))
    ide_performance = df.groupby('IDE')['Overall_Score'].mean().sort_values(ascending=False)
    
    bars = plt.bar(range(len(ide_performance)), ide_performance.values, 
                   color=['#2E8B57', '#4169E1', '#DC143C', '#FF8C00', '#9932CC'])
    
    # Add value labels on bars
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
    plt.show()
    
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
        
        # Add value labels on bars
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
    plt.show()
    
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
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', rotation=45)
        
        # Add mean points
        for j, ide in enumerate(df['IDE'].unique()):
            ide_data = df[df['IDE'] == ide][metric]
            mean_val = ide_data.mean()
            ax.scatter(j, mean_val, color='red', s=80, marker='D', zorder=5)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'score_distribution_boxplots.png', dpi=300, bbox_inches='tight')
    plt.show()
    
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
    plt.show()
    
    # 5. Generate Summary Table
    summary_stats = df.groupby('IDE')[metrics + ['Overall_Score']].agg(['mean', 'std']).round(2)
    summary_stats.to_csv(output_dir / 'ide_performance_summary.csv')
    
    # Print summary
    print("IDE Performance Summary:")
    print("=" * 60)
    print("\nOverall Performance Ranking:")
    for i, (ide, score) in enumerate(ide_performance.items(), 1):
        std = df[df['IDE'] == ide]['Overall_Score'].std()
        print(f"{i}. {ide.upper()}: {score:.2f} (±{std:.2f})")
    
    print(f"\nAll visualizations saved to: {output_dir}")
    print(f"Summary statistics saved to: {output_dir}/ide_performance_summary.csv")
    
    return df, output_dir

if __name__ == "__main__":
    print("Lighthouse IDE Performance Analysis")
    print("=" * 40)
    
    try:
        df, output_dir = create_key_visualizations()
        print("\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
