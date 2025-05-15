import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def normalize_data():
    # Configurações
    input_conc_file = 'input_conc.txt'
    data_dir = Path('filtered_results')
    output_prefix = 'normalized'
    
    # Ler arquivo de concentrações
    try:
        conc_df = pd.read_csv(input_conc_file, sep='\\s+', header=None, 
                            names=['conc1', 'conc2', 'pH'], engine='python')
    except Exception as e:
        print(f"Erro ao ler arquivo de concentrações: {e}")
        return

    # Processar cada combinação de pH e tipo de íon
    for pH in range(2, 11, 2):  # pH 2,4,6,8,10
        # Obter concentrações para este pH
        pH_data = conc_df[conc_df['pH'] == pH]
        if pH_data.empty:
            print(f"Aviso: Não encontrou concentrações para pH {pH}")
            continue

        conc1 = pH_data['conc1'].values[0]
        conc2 = pH_data['conc2'].values[0]

        for ion_type in [1, 2]:
            # Construir caminhos dos arquivos
            input_filename = data_dir / f"combined_data_pH_{pH}_type_{ion_type}_filtered.txt"
            output_filename = data_dir / f"{output_prefix}_pH_{pH}_type_{ion_type}.txt"

            if not input_filename.exists():
                print(f"Aviso: Arquivo não encontrado - {input_filename}")
                continue

            try:
                # Ler dados (6 colunas)
                data = pd.read_csv(input_filename, sep='\\s+', header=None)

                # Verificar estrutura (deve ter 6 colunas)
                if data.shape[1] != 6:
                    print(f"Erro: Arquivo {input_filename} não tem 6 colunas")
                    continue

                # Selecionar concentração correta
                current_conc = conc1 if ion_type == 1 else conc2

                # Calcular média das colunas Y (2,4,6)
                y_columns = [1, 3, 5]  # Colunas 2,4,6 (0-indexed)
                y_means = data[y_columns].mean()
                overall_mean = y_means.mean()

                # Evitar divisão por zero
                if overall_mean == 0:
                    print(f"Erro: Média zero em {input_filename} - não é possível normalizar")
                    continue

                # Normalizar dados
                norm_factor = current_conc / overall_mean
                normalized_data = data.copy()
                for col in y_columns:
                    normalized_data[col] = data[col] * norm_factor

                # Salvar dados normalizados (mesmo formato 6 colunas)
                normalized_data.to_csv(output_filename, sep='\t', 
                                     header=False, index=False, 
                                     float_format='%.15g')
                
                print(f"Arquivo criado: {output_filename}")

            except Exception as e:
                print(f"Erro ao processar {input_filename}: {e}")

if __name__ == "__main__":
    normalize_data()
    print("Processamento concluído!")
    
    # Configurações de estilo profissional
plt.style.use('seaborn-v0_8-poster')
sns.set_context("notebook", font_scale=1.1)
plt.rcParams['font.family'] = 'DejaVu Sans'  # Fonte melhor para símbolos químicos

def create_plots():
    # Diretórios
    data_dir = Path('filtered_results')
    output_dir = Path('plots')
    output_dir.mkdir(exist_ok=True)
    
    # Configurações visuais
    ion_config = {
        1: {'color': '#274001', 'label': 'CrO₄²⁻', 'marker': 'o', 'linestyle': '-'},
        2: {'color': '#a62f03', 'label': 'HCrO₄⁻', 'marker': 's', 'linestyle': '--'}
    }

    # Encontrar todos arquivos normalizados
    all_files = glob.glob(str(data_dir / 'normalized_pH_*_type_*.txt'))
    
    if not all_files:
        print("Nenhum arquivo normalizado encontrado!")
        return

    # ================================================
    # 1. Gráficos combinados (um por pH)
    # ================================================
    files_by_ph = {}
    for file in all_files:
        parts = Path(file).stem.split('_')
        ph = int(parts[2])
        ion_type = int(parts[4])
        files_by_ph.setdefault(ph, {})[ion_type] = file

    for ph, ion_files in files_by_ph.items():
        plt.figure(figsize=(10, 6), dpi=300)
        plt.title(f"Distribuição de Íons - pH {ph}", pad=15)
        
        for ion_type, file_path in ion_files.items():
            data = pd.read_csv(file_path, sep='\\s+', header=None)
            
            # Plotar as 3 réplicas
            for rep in [0, 2, 4]:  # Colunas x: 0,2,4
                x = data[rep]
                y = data[rep+1]    # Colunas y correspondentes
                
                # Linha suave
                plt.plot(x, y, 
                        color=ion_config[ion_type]['color'],
                        linestyle=ion_config[ion_type]['linestyle'],
                        linewidth=2,
                        alpha=0.6,
                        label=f"{ion_config[ion_type]['label']} (Rep {rep//2+1})" if rep == 0 else "")
                
                # Pontos originais
                plt.scatter(x, y,
                          color=ion_config[ion_type]['color'],
                          marker=ion_config[ion_type]['marker'],
                          s=40,
                          alpha=0.5)

        plt.xlabel("Distância à superfície (nm)", labelpad=10)
        plt.ylabel("Concentração (M)", labelpad=10)
        plt.xlim(0, 20)
        plt.ylim(bottom=0)
        plt.grid(True, alpha=0.2)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_dir / f"combined_pH_{ph}.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Gráfico combinado salvo: combined_pH_{ph}.png")

    # ================================================
    # 2. Gráficos individuais (um por arquivo)
    # ================================================
    for file_path in all_files:
        parts = Path(file_path).stem.split('_')
        ph = parts[2]
        ion_type = int(parts[4])
        
        data = pd.read_csv(file_path, sep='\\s+', header=None)
        
        plt.figure(figsize=(8, 5), dpi=300)
        plt.title(f"{ion_config[ion_type]['label']} - pH {ph}", pad=15)
        
        # Plotar as 3 réplicas
        for rep in [0, 2, 4]:
            x = data[rep]
            y = data[rep+1]
            
            # Linha + pontos
            plt.plot(x, y,
                    color=ion_config[ion_type]['color'],
                    linestyle=ion_config[ion_type]['linestyle'],
                    linewidth=2,
                    alpha=0.7)
            
            plt.scatter(x, y,
                      color=ion_config[ion_type]['color'],
                      marker=ion_config[ion_type]['marker'],
                      s=35,
                      alpha=0.6,
                      label=f"Réplica {rep//2+1}")

        plt.xlabel("Distância à superfície (nm)", labelpad=10)
        plt.ylabel("Concentração (M)", labelpad=10)
        plt.xlim(0, 20)
        plt.ylim(bottom=0)
        plt.grid(True, alpha=0.2)
        plt.legend()
        
        ion_name = "CrO4" if ion_type == 1 else "HCrO4"
        plt.tight_layout()
        plt.savefig(output_dir / f"individual_{ion_name}_pH_{ph}.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Gráfico individual salvo: individual_{ion_name}_pH_{ph}.png")

if __name__ == "__main__":
    create_plots()
    print("✅ Todos os gráficos foram gerados com sucesso!")
