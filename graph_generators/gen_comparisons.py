import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def genera_grafico_confronto_ide(csv_path, output_path, use_case_title):
    """
    Genera un grafico di confronto tra IDE a partire da un file CSV.
    
    Parametri:
    - csv_path: percorso del file CSV con i dati
    - output_path: percorso dove salvare il grafico generato
    - use_case_title: titolo del caso d'uso da mostrare nel grafico
    """
    
    # Verifica che il file esista
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File non trovato: {csv_path}")
    
    # Carica i dati
    df = pd.read_csv(csv_path)
    
    # Estrai il nome dell'IDE dal nome del progetto (rimuove i numeri finali)
    df['IDE'] = df['Project'].str.replace(r'\d+$', '', regex=True)
    
    # Calcola le medie per IDE
    ide_stats = df.groupby('IDE').agg({
        'ExecutionTime': 'mean',
        'CorrectionTime': 'mean',
        'Corrections': 'mean'
    }).reset_index()
    
    # Rinomina per chiarezza
    ide_stats.columns = ['IDE', 'Tempo_agente', 'Tempo_interazioni', 'N_medio_correzioni']
    
    # Ordina alfabeticamente (o mantieni l'ordine di apparizione se preferisci)
    ide_stats = ide_stats.sort_values('IDE')
    
    # Capitalizza i nomi degli IDE per la visualizzazione
    ide_labels = [ide.capitalize() for ide in ide_stats['IDE']]
    
    # Crea il grafico
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Posizioni delle barre
    x = np.arange(len(ide_stats))
    width = 0.35
    
    # Barre - Tempo agente (blu)
    bars1 = ax1.bar(x - width/2, ide_stats['Tempo_agente'], width, 
                    label='Tempo agente', color='#4472C4', alpha=0.9)
    
    # Barre - Tempo interazioni (verde)
    bars2 = ax1.bar(x + width/2, ide_stats['Tempo_interazioni'], width,
                    label='Tempo interazioni', color='#70AD47', alpha=0.9)
    
    # Configura l'asse Y sinistro (tempi)
    ax1.set_xlabel('')
    ax1.set_ylabel('Tempo medio (minuti)')

    # Calcola automaticamente i limiti dell'asse Y per i tempi
    max_tempo = max(ide_stats['Tempo_agente'].max(), ide_stats['Tempo_interazioni'].max())
    y_max = np.ceil(max_tempo / 2.5) * 2.5  # Arrotonda al multiplo di 2.5 superiore
    ax1.set_ylim(0, y_max + 0.5)
    ax1.set_yticks(np.arange(0, y_max + 1, 2.5))

    ax1.grid(axis='y', alpha=0.5, linestyle='--', linewidth=0.8, color='gray')
    ax1.set_axisbelow(True)

    # Configura l'asse X
    ax1.set_xticks(x)
    ax1.set_xticklabels(ide_labels)

    # Crea il secondo asse Y per le correzioni
    ax2 = ax1.twinx()
    line = ax2.plot(x, ide_stats['N_medio_correzioni'], 
                    color='#C55A5A', marker='o', linewidth=2, 
                    markersize=6, label='N. medio correzioni')

    # --- Allineamento tick asse destro con asse sinistro ---
    # Scegli un fattore di scala: ad esempio 10 minuti = 2 correzioni
    # Quindi: fattore = 10/2 = 5
    # L'asse destro avrà tick in corrispondenza di quelli sinistri
    left_ticks = ax1.get_yticks()
    # Scegli il valore di correzioni che vuoi allineare (es: 2 correzioni per 10 minuti)
    correzioni_per_tempo = 2 / 10  # 2 correzioni ogni 10 minuti
    right_ticks = left_ticks * correzioni_per_tempo
    ax2.set_yticks(right_ticks)
    ax2.set_ylim(ax1.get_ylim()[0] * correzioni_per_tempo, ax1.get_ylim()[1] * correzioni_per_tempo)
    ax2.set_ylabel('Numero medio correzioni')
    
    # Titolo con il caso d'uso
    ax1.set_title(f'Use Case {use_case_title}: tempi medi e numero medio di correzioni', 
                  fontsize=12, pad=20)
    
    # Legenda combinata
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, 
               loc='upper center', bbox_to_anchor=(0.5, -0.08), 
               ncol=3, frameon=False)
    
    # Layout tight
    plt.tight_layout()
    
    # Salva il grafico
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Grafico salvato in: {output_path}")
    
    # Mostra statistiche
    print(f"\nStatistiche per {use_case_title}:")
    print(ide_stats.to_string(index=False))
    print("-" * 80)
    
    plt.close()


def genera_tutti_i_grafici():
    """
    Genera automaticamente tutti i grafici per i diversi use case.
    """
    
    # Mapping cartelle -> nomi use case
    use_cases = {
        'CRUD_TEST': 'CRUD',
        'AUTH_TEST': 'Autenticazione',
        'CHAT_TEST': 'Chat',
        'FILE_UPLOAD_TEST': 'File Hosting',
        'TASKS_QUEUE_TEST': 'Tasks Queue',
        'CRUD_2_TEST': 'CRUD (re-iterazione)'
    }
    
    # Ottieni la directory root (parent della cartella graph_generators)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 80)
    print("Generazione grafici in corso...")
    print(f"Directory root: {root_dir}")
    print("=" * 80)
    
    grafici_generati = 0
    
    # Scorri tutte le cartelle
    for folder, use_case_name in use_cases.items():
        folder_path = os.path.join(root_dir, folder)
        csv_path = os.path.join(folder_path, 'generation_stats.csv')
        
        # Verifica se il file CSV esiste
        if not os.path.exists(csv_path):
            print(f"⚠ Saltato {folder}: file {csv_path} non trovato")
            continue
        
        # Crea la cartella graphs dentro la cartella del test
        graphs_dir = os.path.join(folder_path, 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        
        output_path = os.path.join(graphs_dir, 'generation_stats_graph.png')
        
        try:
            print(f"\n📊 Generazione grafico per {use_case_name}...")
            genera_grafico_confronto_ide(csv_path, output_path, use_case_name)
            grafici_generati += 1
        except Exception as e:
            print(f"✗ Errore nella generazione del grafico per {folder}: {e}")
    
    print("\n" + "=" * 80)
    print(f"Completato! {grafici_generati}/{len(use_cases)} grafici generati con successo.")
    print("=" * 80)


if __name__ == "__main__":
    genera_tutti_i_grafici()