import os
import glob
import shutil

def process_pH_folders(root_folder, output_folder):
    # Criar pasta de saída se não existir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Encontrar todos os valores de pH únicos
    folders = glob.glob(os.path.join(root_folder, "Sim-repet*"))
    pH_values = set()
    
    for folder in folders:
        parts = os.path.basename(folder).split('-')
        for part in parts:
            if part.startswith('pH_'):
                pH_values.add(part)
    
    # Tipos de arquivos a serem processados (type_1 e type_2)
    file_types = {
        "type_1": "HIST_RES_distribution_modulus_ions_type_1_particle_1.txt_normalized.txt",
        "type_2": "HIST_RES_distribution_modulus_ions_type_2_particle_1.txt_normalized.txt"
    }
    
    # Processar cada valor de pH e cada tipo de arquivo
    for pH in sorted(pH_values):
        for file_type, file_name in file_types.items():
            print(f"Processando {pH} - {file_type}...")
            
            # Encontrar as 3 pastas para este pH
            pH_folders = glob.glob(os.path.join(root_folder, f"Sim-repet*-{pH}-*"))
            if len(pH_folders) != 3:
                print(f"Aviso: Encontradas {len(pH_folders)} pastas para {pH}, esperava 3")
                continue
            
            # Lista para armazenar os dados de cada repetição
            all_data = []
            
            # Ler os arquivos de cada pasta
            for folder in sorted(pH_folders):
                file_path = os.path.join(folder, file_name)
                
                if not os.path.exists(file_path):
                    print(f"Arquivo {file_name} não encontrado em {folder}")
                    continue
                    
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    # Filtrar linhas onde x (coluna 1) < 21.75
                    data = [line.strip().split() for line in lines if line.strip() and float(line.split()[0]) < 21.75]
                    all_data.append(data)
            
            # Pular se nenhum dado válido foi encontrado
            if not all_data:
                print(f"Nenhum dado válido encontrado para {pH} - {file_type}")
                continue
                
            # Verificar se todos os arquivos têm o mesmo número de linhas
            lengths = [len(data) for data in all_data]
            if len(set(lengths)) != 1:
                print(f"Aviso: Arquivos para {pH} - {file_type} têm números diferentes de linhas. Usando o menor comprimento.")
                min_length = min(lengths)
                all_data = [data[:min_length] for data in all_data]
            
            # Combinar os dados
            combined_data = []
            for i in range(len(all_data[0])):
                row = []
                for data in all_data:
                    row.extend(data[i])
                combined_data.append(row)
            
            # Nome do arquivo de saída (agora inclui o tipo)
            output_file = os.path.join(output_folder, f"combined_data_{pH}_{file_type}_filtered.txt")
            
            # Escrever os dados combinados
            with open(output_file, 'w') as f:
                for row in combined_data:
                    f.write('\t'.join(row) + '\n')
            
            print(f"Dados filtrados para {pH} - {file_type} salvos em {output_file}")

# Exemplo de uso
if __name__ == "__main__":
    root_folder = "."  # Pasta onde estão as subpastas (pode alterar)
    output_folder = "filtered_results"
    
    process_pH_folders(root_folder, output_folder)
    print("Processamento concluído!")
