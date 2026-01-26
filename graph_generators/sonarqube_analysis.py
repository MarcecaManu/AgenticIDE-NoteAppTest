
import numpy as np
import os
import pandas as pd

def run_sonarqube_analysis(input_csv, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_csv)
    df['IDE'] = df['Project'].str.extract(r'([a-zA-Z]+)')
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set(style="whitegrid", palette="Set2")

    # 1. Boxplot: Coverage per IDE
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="IDE", y="Coverage (%)")
    plt.title("Coverage (%) per IDE")
    plt.ylabel("Coverage (%)")
    plt.xlabel("IDE")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/coverage_per_ide_boxplot.png")
    plt.clf()

    # 2. Barplot: Maintainability per Project
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values("Maintainability", ascending=False)
    sns.barplot(data=df_sorted, x="Project", y="Maintainability", hue="IDE", dodge=False)
    plt.title("Maintainability Issues per Project")
    plt.ylabel("Maintainability Issues")
    plt.xlabel("Project")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/maintainability_barplot.png")
    plt.clf()

    # 3. Heatmap: Metriche di qualità per progetto (colori scalati per colonna)
    plt.figure(figsize=(12, 6))
    metrics = ["Security", "Reliability", "Maintainability", "Coverage (%)", "Duplications (%)", "Security Hotspots"]
    heat_df = df.set_index("Project")[metrics]
    # Normalizza ogni colonna tra 0 e 1
    norm_heat_df = heat_df.copy()
    for col in norm_heat_df.columns:
        if col == "Coverage (%)":
            # Coverage: 0 rosso, 100 blu (inverte la scala)
            min_val = 0
            max_val = 100
            if (heat_df[col] == 0).all():
                norm_heat_df[col] = 1.0  # Tutti zeri: rosso
            elif (heat_df[col] == 100).all():
                norm_heat_df[col] = 0.0  # Tutti 100: blu
            else:
                norm_heat_df[col] = 1 - (heat_df[col] - min_val) / (max_val - min_val)
        else:
            min_val = norm_heat_df[col].min()
            max_val = norm_heat_df[col].max()
            if max_val > min_val:
                norm_heat_df[col] = (norm_heat_df[col] - min_val) / (max_val - min_val)
            else:
                if min_val == 0 and max_val == 0:
                    norm_heat_df[col] = 0.0  # Tutti zeri: blu
                else:
                    norm_heat_df[col] = 0.5  # Tutti uguali ma non zero: colore neutro
    # Prepara annotazioni come prima
    annot_matrix = heat_df.copy()
    for col in annot_matrix.columns:
        if col in ["Coverage (%)", "Duplications (%)"]:
            annot_matrix[col] = annot_matrix[col].map("{:.1f}".format)
        else:
            annot_matrix[col] = annot_matrix[col].map("{:.0f}".format)
    # Heatmap senza colorbar, colori scalati per colonna
    sns.heatmap(norm_heat_df, annot=annot_matrix, fmt="", cmap="coolwarm", linewidths=0.5, linecolor="gray", cbar=False)
    plt.title("Heatmap Qualità Codice per Progetto (colori scalati per colonna)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/quality_heatmap_per_project.png")
    plt.clf()

    # 4. Media Coverage per IDE (con deviazione standard)
    plt.figure(figsize=(8, 6))
    sns.barplot(data=df, x="IDE", y="Coverage (%)", ci="sd", estimator="mean")
    plt.title("Coverage Media per IDE (± Deviazione Standard)")
    plt.ylabel("Coverage (%)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/coverage_mean_per_ide.png")
    plt.clf()

    # 5. Scatterplot: Coverage vs Maintainability
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x="Coverage (%)", y="Maintainability", hue="IDE", style="IDE", s=100)
    plt.title("Coverage vs Maintainability")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/coverage_vs_maintainability.png")
    plt.clf()

    # 6. Distribuzione Coverage (%)
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x="Coverage (%)", hue="IDE", kde=True, multiple="stack")
    plt.title("Distribuzione della Coverage (%)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/coverage_distribution.png")
    plt.clf()

    # 7. Heatmap delle correlazioni tra metriche
    plt.figure(figsize=(10, 6))
    correlation = df.drop(columns=["Project", "IDE"]).corr()
    sns.heatmap(correlation, annot=True, cmap="vlag")
    plt.title("Correlazioni tra Metriche di Qualità")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/correlation_heatmap.png")
    plt.clf()

    print(f"✅ Grafici salvati nella cartella '{output_dir}/'")


def run_all_sonarqube_analyses():
    use_cases = [
        'CRUD_TEST',
        'AUTH_TEST',
        'CHAT_TEST',
        'FILE_UPLOAD_TEST',
        'TASKS_QUEUE_TEST',
        'CRUD_2_TEST'
    ]
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder in use_cases:
        folder_path = os.path.join(root_dir, folder)
        csv_path = os.path.join(folder_path, 'project_stats.csv')
        output_dir = os.path.join(folder_path, 'graphs', 'SonarQube')
        if not os.path.exists(csv_path):
            print(f"⚠ Saltato {folder}: file {csv_path} non trovato")
            continue
        print(f"\n📊 Analisi SonarQube per {folder}...")
        run_sonarqube_analysis(csv_path, output_dir)

if __name__ == "__main__":
    run_all_sonarqube_analyses()
