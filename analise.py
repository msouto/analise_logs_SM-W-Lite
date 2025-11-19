import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ======================================================
# FUNÇÃO PARA CARREGAR UM ARQUIVO DE LOG
# ======================================================

def load_log(filepath):
    filename = os.path.basename(filepath)
    date_str = filename.replace(".txt", "")
    dt = datetime.strptime(date_str, "%d%m%Y")

    df = pd.read_csv(filepath, header=None, sep=":")
    df.columns = ["h", "m", "s", "pa", "epa_c", "epa_g", "iarms", "uarms"]

    for col in ["h", "m", "s", "pa", "epa_c", "epa_g", "iarms", "uarms"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["h", "m", "s"])

    df["timestamp"] = [
        dt + timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        for h, m, s in zip(df["h"], df["m"], df["s"])
    ]

    # Conversão dos valores escalados ×100 → unidades reais
    df["pa_W"] = df["pa"] / 100.0
    df["iarms_A"] = df["iarms"] / 100.0
    df["uarms_V"] = df["uarms"] / 100.0

    return df

# ======================================================
# FUNÇÃO PARA GERAR E SALVAR UM GRÁFICO
# ======================================================

def plot_series(df, column, ylabel, title, filepath):
    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df[column], linewidth=1)
    plt.xlabel("Tempo")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"Gráfico salvo em: {filepath}")

# ======================================================
# CÁLCULO DE kWh/DIA A PARTIR DE epa_c
# ======================================================

def calcular_kwh_por_dia(df):
    """
    Usa epa_c (Consumo Fase A [kWh], acumulado) para estimar kWh/dia:
    kWh_dia = max(epa_c) - min(epa_c) por data.
    Se a escala do equipamento for outra (ex: Wh ou ×100),
    ajustar o fator aqui.
    """
    df = df.copy()
    df["date"] = df["timestamp"].dt.date

    # agrupar por dia e pegar diferença do acumulado
    daily = df.groupby("date")["epa_c"].agg(["min", "max"])
    daily["kWh_dia"] = daily["max"] - daily["min"]

    return daily[["kWh_dia"]]

# ======================================================
# DETECÇÃO DE OUTLIERS VIA IQR
# ======================================================

def detectar_outliers_iqr(df, column):
    """
    Usa método do IQR:
    outlier < Q1 - 1.5*IQR ou > Q3 + 1.5*IQR
    Retorna dataframe apenas com linhas outliers na coluna indicada.
    """
    series = df[column].dropna()
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr

    mask = (df[column] < lim_inf) | (df[column] > lim_sup)
    return df[mask], (lim_inf, lim_sup, q1, q3)

# ======================================================
# GERAÇÃO DE RELATÓRIO TEXTO
# ======================================================

def gerar_relatorio(full, out_dir):
    rel_lines = []
    rel_lines.append("RELATÓRIO DE ANÁLISE DOS LOGS DE CONSUMO ELÉTRICO\n")
    rel_lines.append("===============================================\n")

    # Estatísticas básicas
    rel_lines.append("\n[1] Estatísticas básicas (valores reais):\n")
    desc = full[["pa_W", "iarms_A", "uarms_V"]].describe()
    rel_lines.append(str(desc))
    rel_lines.append("\n")

    # kWh/dia
    rel_lines.append("\n[2] Estimativa de kWh por dia (via epa_c):\n")
    kwh_dia = calcular_kwh_por_dia(full)
    rel_lines.append(str(kwh_dia))
    rel_lines.append("\n")

    # Outliers
    rel_lines.append("\n[3] Detecção de outliers (IQR):\n")

    for col, label in [("uarms_V", "Tensão [V]"),
                       ("iarms_A", "Corrente [A]"),
                       ("pa_W", "Potência [W]")]:
        rel_lines.append(f"\n3.{['uarms_V','iarms_A','pa_W'].index(col)+1} - {label} ({col}):\n")
        out_df, (lim_inf, lim_sup, q1, q3) = detectar_outliers_iqr(full, col)
        rel_lines.append(f"  Limite inferior: {lim_inf:.3f}")
        rel_lines.append(f"  Limite superior: {lim_sup:.3f}")
        rel_lines.append(f"  Q1: {q1:.3f}")
        rel_lines.append(f"  Q3: {q3:.3f}")
        rel_lines.append(f"  Total de outliers: {len(out_df)}\n")

        if not out_df.empty:
            # mostrar só os 10 primeiros para não poluir demais
            preview = out_df[["timestamp", col]].head(10)
            rel_lines.append("  Exemplos:\n")
            rel_lines.append(str(preview))
            rel_lines.append("\n")
        else:
            rel_lines.append("  Nenhum outlier detectado.\n")

    rel_text = "\n".join(rel_lines)

    # Perguntar o que fazer com o relatório
    print("\nDeseja gerar/exibir o relatório (kWh/dia, outliers, estatísticas)?")
    print("1 - Exibir somente no terminal")
    print("2 - Salvar somente em arquivo .txt")
    print("3 - Exibir no terminal E salvar em arquivo")
    print("4 - Não gerar relatório")
    choice = input("\nDigite 1, 2, 3 ou 4: ").strip()

    report_path = os.path.join(out_dir, "relatorio_analise_logs.txt")

    if choice in ("1", "3"):
        print("\n" + "="*60)
        print(rel_text)
        print("="*60 + "\n")

    if choice in ("2", "3"):
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(rel_text)
        print(f"\nRelatório salvo em: {report_path}")

    if choice == "4":
        print("\nRelatório não gerado, conforme solicitado.")


# ======================================================
# MENU INTERATIVO (ESCOLHA DA PASTA)
# ======================================================

print("\n========================================")
print(" ANALISADOR DE LOGS DE CONSUMO ELÉTRICO ")
print("========================================\n")

print("Escolha a origem dos arquivos de log:\n")
print("1 - Usar a pasta padrão './logs/'")
print("2 - Informar manualmente o caminho dos arquivos")
choice = input("\nDigite 1 ou 2: ").strip()

if choice == "1":
    LOG_DIR = "logs"
    print("\n✔ Usando a pasta padrão './logs/'")
else:
    LOG_DIR = input("\nInforme o caminho completo da pasta onde estão os logs: ").strip()
    print(f"\n✔ Usando a pasta: {LOG_DIR}")

OUT_DIR = LOG_DIR  # salvar gráficos e relatório na mesma pasta
os.makedirs(OUT_DIR, exist_ok=True)

# ======================================================
# CARREGAR ARQUIVOS
# ======================================================

all_dfs = []
print("\nBuscando arquivos .txt...\n")

for file in os.listdir(LOG_DIR):
    if file.endswith(".txt"):
        path = os.path.join(LOG_DIR, file)
        print(f"Lendo: {path}")
        try:
            df = load_log(path)
            all_dfs.append(df)
        except Exception as e:
            print(f"Erro ao processar {file}: {e}")

if not all_dfs:
    print("\n❌ Nenhum arquivo .txt encontrado. Encerrando.")
    raise SystemExit

full = pd.concat(all_dfs, ignore_index=True)
full.sort_values("timestamp", inplace=True)

# ======================================================
# GERANDO GRÁFICOS
# ======================================================

print("\nGerando gráficos...\n")

plot_series(
    full, "uarms_V", "Tensão [V]",
    "Tensão RMS ao longo do tempo",
    os.path.join(OUT_DIR, "tensao.png")
)

plot_series(
    full, "iarms_A", "Corrente [A]",
    "Corrente RMS ao longo do tempo",
    os.path.join(OUT_DIR, "corrente.png")
)

plot_series(
    full, "pa_W", "Potência [W]",
    "Potência ativa ao longo do tempo",
    os.path.join(OUT_DIR, "potencia.png")
)

# ======================================================
# RELATÓRIO AUTOMÁTICO (kWh/dia + OUTLIERS)
# ======================================================

gerar_relatorio(full, OUT_DIR)

print("\n========================================")
print(" Análise concluída com sucesso! ")
print(" Gráficos e (opcionalmente) relatório gerados. ")
print("========================================\n")
