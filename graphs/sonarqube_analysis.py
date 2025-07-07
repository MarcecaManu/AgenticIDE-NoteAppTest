import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# === CONFIG ===
INPUT_CSV = "project_stats.csv"
OUTPUT_DIR = "charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Load data ===
df = pd.read_csv(INPUT_CSV)
df['IDE'] = df['Project'].str.extract(r'([a-zA-Z]+)')

# === Setup plot style ===
sns.set(style="whitegrid", palette="Set2")

# === 1. Boxplot: Coverage per IDE ===
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="IDE", y="Coverage (%)")
plt.title("Coverage (%) per IDE")
plt.ylabel("Coverage (%)")
plt.xlabel("IDE")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/coverage_per_ide_boxplot.png")
plt.clf()

# === 2. Barplot: Maintainability per Project ===
plt.figure(figsize=(12, 6))
df_sorted = df.sort_values("Maintainability", ascending=False)
sns.barplot(data=df_sorted, x="Project", y="Maintainability", hue="IDE", dodge=False)
plt.title("Maintainability Issues per Project")
plt.ylabel("Maintainability Issues")
plt.xlabel("Project")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/maintainability_barplot.png")
plt.clf()

# === 3. Heatmap: Metriche di qualità per progetto (con formattazione personalizzata) ===
import numpy as np

plt.figure(figsize=(12, 6))
metrics = ["Security", "Reliability", "Maintainability", "Coverage (%)", "Duplications (%)", "Security Hotspots"]
heat_df = df.set_index("Project")[metrics]

# Crea una matrice di annotazioni con formato corretto
annot_matrix = heat_df.copy()
for col in annot_matrix.columns:
    if col in ["Coverage (%)", "Duplications (%)"]:
        annot_matrix[col] = annot_matrix[col].map("{:.1f}".format)
    else:
        annot_matrix[col] = annot_matrix[col].map("{:.0f}".format)

sns.heatmap(heat_df, annot=annot_matrix, fmt="", cmap="coolwarm", linewidths=0.5, linecolor="gray")
plt.title("Heatmap Qualità Codice per Progetto")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/quality_heatmap_per_project.png")
plt.clf()


# === 4. Media Coverage per IDE (con deviazione standard) ===
plt.figure(figsize=(8, 6))
sns.barplot(data=df, x="IDE", y="Coverage (%)", ci="sd", estimator="mean")
plt.title("Coverage Media per IDE (± Deviazione Standard)")
plt.ylabel("Coverage (%)")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/coverage_mean_per_ide.png")
plt.clf()

# === 5. Scatterplot: Coverage vs Maintainability ===
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x="Coverage (%)", y="Maintainability", hue="IDE", style="IDE", s=100)
plt.title("Coverage vs Maintainability")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/coverage_vs_maintainability.png")
plt.clf()

# === 6. Distribuzione Coverage (%) ===
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x="Coverage (%)", hue="IDE", kde=True, multiple="stack")
plt.title("Distribuzione della Coverage (%)")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/coverage_distribution.png")
plt.clf()

# === 7. Heatmap delle correlazioni tra metriche ===
plt.figure(figsize=(10, 6))
correlation = df.drop(columns=["Project", "IDE"]).corr()
sns.heatmap(correlation, annot=True, cmap="vlag")
plt.title("Correlazioni tra Metriche di Qualità")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/correlation_heatmap.png")
plt.clf()

print("✅ Grafici salvati nella cartella 'charts/'")
