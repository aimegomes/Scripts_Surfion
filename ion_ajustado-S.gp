# Colocar o script em uma pasta que contem somente os dados a serem ajustados
# Configurações de encoding e terminal
set encoding iso_8859_1
set terminal pdfcairo font "Gill Sans,8" linewidth 2 rounded fontscale 1.0

# Proporção do gráfico
set size ratio 0.61

# Estilos de linha para eixos e grade
set style line 80 lt rgb "#000000" lw 1.0
set style line 81 lt 0  # dashed
set style line 81 lt rgb "#808080"  # grey

# Borda
set border 3 back linestyle 80

# Definição de estilos de linha para os gráficos
set style line 1 lt rgb "#000000" lw 2.0 pt 7 ps 0.5  #   (pontos)
set style line 2 lt rgb "#f29f05" lw 2.0              # Laranja (linha)
set style line 3 lt rgb "#000000" lw 2.0 pt 7 ps 0.5  # Laranja escuro (pontos)
set style line 4 lt rgb "#a62f03" lw 2.0              #  S (linha)

# Rótulos dos eixos
set xlabel "Distância radial (nm)"
set ylabel "Concentração (M)"

# Intervalos dos eixos
set xrange [0:20]
set yrange [0:*]

# Configuração da legenda
set ytics nomirror
set xtics nomirror
set key font ",7"
set key top right vertical  # Legenda em coluna vertical
set key spacing 1.5         # Aumenta o espaço entre os itens da legenda
#set key box                 # Adiciona uma caixa ao redor da legenda

# Função de ajuste
f(x) = b * x * exp(-d * x) + a

# Valor fixo para o parâmetro d
c=3.6
# Loop through each directory
dir_list = system("ls -d */")

# Loop through each directory
do for [dir in dir_list] {
    # Remover a barra final do diretório, se existir
    dir = substr(dir, 1, strlen(dir)-1)

    # Caminho para o arquivo surfion_simulationParameters.f90
    surfion_file = dir."/surfion_simulationParameters.f90"

    # Ler os valores de conc1 e conc2, considerando que o número está antes de qualquer comentário (!)
    conc1 = system(sprintf("sed -n '29p' %s | awk '{print $1}' | cut -d'!' -f1", surfion_file))
    conc2 = system(sprintf("sed -n '34p' %s | awk '{print $1}' | cut -d'!' -f1", surfion_file))

    # Converter os valores lidos para números
    conc1 = real(conc1)
    conc2 = real(conc2)

    # Construir os caminhos dos arquivos
    file1 = dir."/HIST_RES_distribution_modulus_ions_type_1_particle_1.txt_normalized.txt"
    file2 = dir."/HIST_RES_distribution_modulus_ions_type_2_particle_1.txt_normalized.txt"
    
    # Verificar se os arquivos existem corretamente
    exists1 = system(sprintf("[ -f '%s' ] && echo 1 || echo 0", file1)) + 0
    exists2 = system(sprintf("[ -f '%s' ] && echo 1 || echo 0", file2)) + 0

    if (exists1 && exists2) {
        # Coletar estatísticas dos arquivos
        stats file1 using 1:2 name "A1"
        stats file2 using 1:2 name "A2"

        # Definir valores iniciais para os parâmetros
        b = 0.01  # Valor inicial para b
        d = 0.5  # Valor inicial para d
        a = 0.0001 


        # Ajustar a função aos dados normalizados
        fit f(x) file1 using 1:($2*conc1/A1_mean_y) via b, d, a
        fit f(x) file2 using 1:($2*conc2/A2_mean_y) via b, d, a

        # Criar strings para a legenda com a fórmula e os parâmetros
        label_CrO4 = sprintf("Ajuste CrO4: a+bxe^{-cx}\na=%.3f, b = %.3f, c = %.3f", a, b, d)
        label_HCrO4 = sprintf("Ajuste HCrO4: b(x)e^{-d(x)}\na=%.3f, nb = %.3f, d = %.3f", a, b, d)

        # Gráfico para CrO4 (pontos e ajuste)
        set output dir."/concentration_CrO4.pdf"
        plot \
            file1 using 1:($2*conc1/A1_mean_y) with points linestyle 1 title "CrO4 (dados)", \
            f(x) with lines linestyle 2 title label_CrO4
        set output

        # Gráfico para HCrO4 (pontos e ajuste)
        set output dir."/concentration_HCrO4.pdf"
        plot \
            file2 using 1:($2*conc2/A2_mean_y) with points linestyle 3 title "HCrO4 (dados)", \
            f(x) with lines linestyle 4 title label_HCrO4
        set output

        print sprintf("Gráficos gerados para o diretório: %s", dir)
    } else {
        print sprintf("Ignorando diretório %s: Arquivos necessários não encontrados.", dir)
    }
}
