import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict

def genera_grafico_requisiti_mancanti(csv_path, output_path, use_case_title, other_error_label):
    """
    Genera un grafico a barre impilate dei requisiti mancanti per IDE.
    
    Parametri:
    - csv_path: percorso del file CSV con i dati
    - output_path: percorso dove salvare il grafico generato
    - use_case_title: titolo del caso d'uso da mostrare nel grafico
    - other_error_label: etichetta personalizzata per la categoria "OtherErrors"
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File non trovato: {csv_path}")

    df = pd.read_csv(csv_path)

    # Estrai il nome dell'IDE dal nome del progetto (rimuove i numeri finali)
    df['IDE'] = df['Project'].str.replace(r'\d+$', '', regex=True)

    # Colonne da escludere
    exclude_cols = {'Project', 'ExecutionTime', 'CorrectionTime', 'Corrections', 'IDE', 'AutomaticAnalysisTime', 'regressions'}
    # Mappatura nomi colonne
    col_map = {
        'APIErrors': 'API',
        'PersistencyErrors': 'Persistenza dati',
        'FrontendErrors': 'Frontend',
        'TestsErrors': 'Tests',
        'ProjectStructureErrors': 'Organizzazione progetto',
        'OtherErrors': other_error_label
    }
    # Seleziona solo le colonne che ci interessano e che esistono
    req_cols = [col for col in col_map.keys() if col in df.columns]
    df = df.rename(columns=col_map)
    plot_cols = [col_map[c] for c in req_cols]

    # Calcola la somma delle mancanze per ogni requisito e IDE
    grouped = df.groupby('IDE')[plot_cols].sum().reset_index()

    # Ordina alfabeticamente per coerenza
    grouped = grouped.sort_values('IDE')
    ide_labels = [ide.capitalize() for ide in grouped['IDE']]

    # Colori personalizzati coerenti con lo screen
    color_map = {
        'API': '#1f77b4',  # blu
        'Frontend': '#7ec17e',  # verde chiaro
        'Organizzazione progetto': '#8c564b',  # marrone
        'Searchbar': '#bdbdbd',  # grigio chiaro (other)
        'Tests': '#9edae5',  # azzurrino
        'Persistenza dati': '#ffe066',  # giallo
    }
    colors = [color_map.get(col, '#cccccc') for col in plot_cols]

    # Grafico più basso
    fig, ax = plt.subplots(figsize=(10, 3.5))
    bottom = np.zeros(len(ide_labels))
    for idx, (col, color) in enumerate(zip(plot_cols, colors)):
        ax.bar(ide_labels, grouped[col], bottom=bottom, label=col, color=color, zorder=1)
        bottom += grouped[col].values

    # Aggiungi margine superiore all'asse y e imposta tick interi
    y_max = int(np.ceil(bottom.max() * 1.15))
    ax.set_ylim(0, y_max)
    if y_max <= 10:
        ax.set_yticks(np.arange(0, y_max + 1, 1))
    else:
        ax.set_yticks(np.arange(0, y_max + 2, 2))

    # Griglia tratteggiata SOPRA le barre
    ax.yaxis.grid(True, linestyle='--', linewidth=0.8, color='gray', alpha=0.5, zorder=10)
    ax.set_axisbelow(False)  # deve essere dopo le barre e dopo la grid

    ax.set_ylabel('Frequenza')
    ax.set_title(f'Distribuzione dei requisiti mancanti per IDE\n{use_case_title}')
    ax.legend(title='Requisito', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Grafico salvato in: {output_path}")
    plt.close()

def genera_tutti_i_grafici_requisiti():
    """
    Genera automaticamente tutti i grafici dei requisiti mancanti per i diversi use case.
    """
    use_cases = {
        'AUTH_TEST': ('Autenticazione', 'Sicurezza credenziali'),
        'CHAT_TEST': ('Chat', 'Gestione connessioni'),
        'FILE_UPLOAD_TEST': ('File Hosting', 'Validazione files'),
        'TASKS_QUEUE_TEST': ('Tasks Queue', 'Elaborazione asincrona'),
        'CRUD_2_TEST': ('CRUD (re-iterazione)', 'Searchbar')
    }
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 80)
    print("Generazione grafici requisiti mancanti in corso...")
    print(f"Directory root: {root_dir}")
    print("=" * 80)
    grafici_generati = 0
    for folder, (use_case_name, other_error_label) in use_cases.items():
        folder_path = os.path.join(root_dir, folder)
        csv_path = os.path.join(folder_path, 'generation_stats.csv')
        if not os.path.exists(csv_path):
            print(f"⚠ Saltato {folder}: file {csv_path} non trovato")
            continue
        graphs_dir = os.path.join(folder_path, 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        output_path = os.path.join(graphs_dir, 'missing_requirements_graph.png')
        try:
            print(f"\n📊 Generazione grafico requisiti mancanti per {use_case_name}...")
            genera_grafico_requisiti_mancanti(csv_path, output_path, use_case_name, other_error_label)
            grafici_generati += 1
        except Exception as e:
            print(f"✗ Errore nella generazione del grafico per {folder}: {e}")
    print("\n" + "=" * 80)
    print(f"Completato! {grafici_generati}/{len(use_cases)} grafici generati con successo.")
    print("=" * 80)

if __name__ == "__main__":
    genera_tutti_i_grafici_requisiti()
