#!/bin/bash

# Nome da pasta de destino
dest_dir="org"

# Cria a pasta de destino se ela não existir
if [ ! -d "$dest_dir" ]; then
    mkdir "$dest_dir"
fi

# Percorre todas as pastas no diretório atual
for dir in */; do
    # Remove a barra do final do nome da pasta
    dir_name=${dir%/}
    
    # Verifica se existem os arquivos desejados na pasta atual
    for file in "$dir"concentration_{CrO4,HCrO4}.pdf; do
        # Verifica se o arquivo existe (o glob pode retornar o padrão se não encontrar)
        if [ -f "$file" ]; then
            # Extrai o nome base do arquivo (sem o caminho)
            base_name=$(basename "$file")
            # Novo nome do arquivo
            new_name="${dir_name}_${base_name}"
            # Copia o arquivo para a pasta de destino com o novo nome
            cp "$file" "$dest_dir/$new_name"
        fi
    done
done

echo "Arquivos copiados para a pasta $dest_dir com sucesso!"
