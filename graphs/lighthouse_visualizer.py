#!/usr/bin/env python3
"""
Lighthouse Data Visualizer
Generates comprehensive visualizations comparing IDE performance across Lighthouse metrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up the plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data(csv_path):
    """Load and prepare the lighthouse data."""
    df = pd.read_csv(csv_path)
    
    # Ensure numeric columns are properly typed
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def create_output_directory():
    """Create output directory for plots."""
    output_dir = Path("lighthouse_analysis")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def plot_score_distribution_by_ide(df, output_dir):
    """Create box plots showing score distribution for each IDE across all metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Lighthouse Score Distribution by IDE', fontsize=16, fontweight='bold')
    
    metrics = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    metric_names = ['Performance', 'Accessibility', 'Best Practices', 'SEO']
    
    for i, (metric, name) in enumerate(zip(metrics, metric_names)):
        ax = axes[i//2, i%2]
        
        # Create box plot
        sns.boxplot(data=df, x='IDE', y=metric, ax=ax)
        ax.set_title(f'{name} Scores by IDE', fontweight='bold')
        ax.set_ylabel('Score')
        ax.set_ylim(0, 105)
        
        # Add mean markers
        for j, ide in enumerate(df['IDE'].unique()):
            ide_data = df[df['IDE'] == ide][metric]
            mean_val = ide_data.mean()
            ax.scatter(j, mean_val, color='red', s=100, marker='D', zorder=5, label='Mean' if j == 0 else '')
        
        # Rotate x-axis labels for better readability
        ax.tick_params(axis='x', rotation=45)
        
        if i == 0:
            ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'score_distribution_by_ide.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_ide_comparison_heatmap(df, output_dir):
    """Create a heatmap showing average scores for each IDE across all metrics."""
    # Calculate mean scores for each IDE
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    heatmap_data = df.groupby('IDE')[score_columns].mean()
    
    # Rename columns for better display
    heatmap_data.columns = ['Performance', 'Accessibility', 'Best Practices', 'SEO']
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', center=85, 
                vmin=70, vmax=100, fmt='.1f', cbar_kws={'label': 'Score'})
    plt.title('Average Lighthouse Scores by IDE', fontsize=14, fontweight='bold')
    plt.ylabel('IDE')
    plt.xlabel('Lighthouse Metric')
    plt.tight_layout()
    plt.savefig(output_dir / 'ide_comparison_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_overall_performance_ranking(df, output_dir):
    """Create a bar chart showing overall performance ranking of IDEs."""
    # Calculate overall average score for each IDE
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    df['Overall_Score'] = df[score_columns].mean(axis=1)
    
    ide_rankings = df.groupby('IDE')['Overall_Score'].mean().sort_values(ascending=False)
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(ide_rankings.index, ide_rankings.values, 
                   color=['#2E8B57', '#4169E1', '#DC143C', '#FF8C00', '#9932CC'])
    
    # Add value labels on bars
    for bar, value in zip(bars, ide_rankings.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Overall IDE Performance Ranking\n(Average of All Lighthouse Metrics)', 
              fontsize=14, fontweight='bold')
    plt.ylabel('Average Score')
    plt.xlabel('IDE')
    plt.ylim(80, 100)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'overall_performance_ranking.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return ide_rankings

def plot_metric_comparison_radar(df, output_dir):
    """Create radar charts comparing IDEs across all metrics."""
    from math import pi
    
    # Calculate mean scores for each IDE
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    ide_means = df.groupby('IDE')[score_columns].mean()
    
    # Number of metrics
    num_metrics = len(score_columns)
    
    # Create angles for each metric
    angles = [n / float(num_metrics) * 2 * pi for n in range(num_metrics)]
    angles += angles[:1]  # Complete the circle
    
    # Create subplot for each IDE
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(projection='polar'))
    fig.suptitle('IDE Performance Radar Charts', fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    ides = ide_means.index.tolist()
    colors = ['#2E8B57', '#4169E1', '#DC143C', '#FF8C00', '#9932CC']
    
    for i, ide in enumerate(ides):
        ax = axes[i]
        
        # Get values for this IDE
        values = ide_means.loc[ide].values.tolist()
        values += values[:1]  # Complete the circle
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, label=ide, color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(['Performance', 'Accessibility', 'Best Practices', 'SEO'])
        ax.set_ylim(70, 100)
        ax.set_title(f'{ide.upper()}', fontweight='bold', pad=20)
        ax.grid(True)
    
    # Remove the extra subplot
    axes[-1].remove()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'radar_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_project_variability(df, output_dir):
    """Show variability of scores across projects for each IDE."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Score Variability Across Projects by IDE', fontsize=16, fontweight='bold')
    
    metrics = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    metric_names = ['Performance', 'Accessibility', 'Best Practices', 'SEO']
    
    for i, (metric, name) in enumerate(zip(metrics, metric_names)):
        ax = axes[i//2, i%2]
        
        # Calculate standard deviation for each IDE
        variability = df.groupby('IDE')[metric].agg(['mean', 'std']).reset_index()
        
        # Create bar plot with error bars
        bars = ax.bar(variability['IDE'], variability['mean'], 
                     yerr=variability['std'], capsize=5, alpha=0.7)
        
        ax.set_title(f'{name} Score Variability', fontweight='bold')
        ax.set_ylabel('Score (with std dev)')
        ax.set_ylim(70, 105)
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, mean_val, std_val in zip(bars, variability['mean'], variability['std']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + std_val + 1,
                   f'{mean_val:.1f}±{std_val:.1f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'project_variability.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_correlation_matrix(df, output_dir):
    """Create correlation matrix between different Lighthouse metrics."""
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    correlation_matrix = df[score_columns].corr()
    
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, cbar_kws={'label': 'Correlation Coefficient'})
    plt.title('Correlation Matrix: Lighthouse Metrics', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_summary_statistics(df, output_dir):
    """Generate and save summary statistics."""
    score_columns = ['Performance_Score', 'Accessibility_Score', 'Best Practices_Score', 'SEO_Score']
    
    # Overall statistics
    overall_stats = df[score_columns].describe()
    
    # Statistics by IDE
    ide_stats = df.groupby('IDE')[score_columns].agg(['mean', 'std', 'min', 'max'])
    
    # Calculate overall score
    df['Overall_Score'] = df[score_columns].mean(axis=1)
    overall_by_ide = df.groupby('IDE')['Overall_Score'].agg(['mean', 'std'])
    
    # Save to CSV
    overall_stats.to_csv(output_dir / 'summary_statistics.csv')
    ide_stats.to_csv(output_dir / 'detailed_comparison.csv')
    overall_by_ide.to_csv(output_dir / 'overall_scores_by_ide.csv')
    
    print("Summary Statistics:")
    print("=" * 50)
    print("\nOverall Statistics Across All IDEs:")
    print(overall_stats.round(2))
    
    print("\n\nIDE Rankings (by Overall Score):")
    rankings = df.groupby('IDE')['Overall_Score'].mean().sort_values(ascending=False)
    for i, (ide, score) in enumerate(rankings.items(), 1):
        print(f"{i}. {ide.upper()}: {score:.2f}")
    
    print(f"\n\nDetailed statistics saved to {output_dir}")

def main():
    """Main function to generate all visualizations."""
    print("Lighthouse Data Visualization Tool")
    print("=" * 40)
    
    # Load data
    csv_path = "frontend_results.csv"
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found!")
        return
    
    df = load_data(csv_path)
    print(f"Loaded data: {len(df)} records, {len(df['IDE'].unique())} IDEs")
    
    # Create output directory
    output_dir = create_output_directory()
    print(f"Saving plots to: {output_dir}")
    
    # Generate all visualizations
    print("\nGenerating visualizations...")
    
    plot_score_distribution_by_ide(df, output_dir)
    print("✓ Score distribution plots created")
    
    plot_ide_comparison_heatmap(df, output_dir)
    print("✓ IDE comparison heatmap created")
    
    rankings = plot_overall_performance_ranking(df, output_dir)
    print("✓ Overall performance ranking created")
    
    plot_metric_comparison_radar(df, output_dir)
    print("✓ Radar comparison charts created")
    
    plot_project_variability(df, output_dir)
    print("✓ Project variability analysis created")
    
    plot_correlation_matrix(df, output_dir)
    print("✓ Correlation matrix created")
    
    generate_summary_statistics(df, output_dir)
    print("✓ Summary statistics generated")
    
    print(f"\nAll visualizations completed! Check the '{output_dir}' folder for results.")

if __name__ == "__main__":
    main()
