# 📊 Analisador de Logs – SM-W lite+ (IE Tecnologia)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

Este repositório contém um sistema em Python para análise automática de logs gerados pelo equipamento **SM-W lite+**, da **IE Tecnologia**, utilizado para monitoramento elétrico de fase A.

A ferramenta realiza:

- 📈 **Geração de gráficos** de Tensão RMS (V), Corrente RMS (A) e Potência Ativa (W)  
- ⚡ **Cálculo de kWh/dia**, usando o acumulado `epa_c`  
- 🚨 **Detecção de outliers** via método IQR (tensão, corrente, potência)  
- 📝 **Relatório automático** contendo estatísticas, kWh/dia e outliers  
- 💾 Menu interativo para escolher **pasta padrão (`./logs`)** ou qualquer pasta do sistema  
- 📑 Relatório exibido no terminal, salvo em arquivo `.txt` ou ambos  

O sistema funciona em macOS, Linux e Windows.

---

## 📂 Organização do Repositório

```text
.
├── analise.py          # Script principal da análise
├── README.md           # Documentação em Português
├── README_EN.md        # Documentação em Inglês
└── logs/               # (opcional) Pasta padrão com arquivos .txt de log
```

---

## 📄 Formato dos Arquivos de Log

Os arquivos devem estar no formato:

```text
hora : minuto : segundo : pa : epa_c : epa_g : iarms : uarms
```

### 🧾 Legenda dos Campos

| Campo         | Descrição                                   | Unidade |
|---------------|---------------------------------------------|---------|
| **hora**      | Hora da medição (0–23)                      | h       |
| **minuto**    | Minuto da medição (0–59)                    | min     |
| **segundo**   | Segundo da medição (0–59)                   | s       |
| **pa**        | Potência ativa na Fase A                    | W       |
| **epa_c**     | Energia consumida acumulada na Fase A       | kWh     |
| **epa_g**     | Energia gerada acumulada na Fase A          | kWh     |
| **iarms**     | Corrente RMS da Fase A                      | A       |
| **uarms**     | Tensão RMS da Fase A                        | V       |

### 🔧 Observação sobre escala dos valores

Os campos exportados pelo SM-W Lite+ são **escalados ×100**:

- `pa`
- `iarms`
- `uarms`

O script converte automaticamente:

- `pa_W` → W  
- `iarms_A` → A  
- `uarms_V` → V  

---

## 🛠️ Instalação

### ✔️ Requisito: Python 3.10+

Recomenda-se usar ambiente virtual.

### 1. Criar ambiente virtual

```bash
python3.10 -m venv .venv
source .venv/bin/activate   # macOS / Linux
.\.venv\Scriptsctivate    # Windows
```

### 2. Instalar dependências

```bash
pip install "numpy<2.0" "pandas<2.2" matplotlib
```

---

## ▶️ Como Usar

### 1. Coloque os arquivos `.txt` de log na pasta desejada  

Exemplo:

```text
logs/
 ├── 15112025.txt
 ├── 16112025.txt
 ├── 17112025.txt
 ├── 18112025.txt
 └── 19112025.txt
```

### 2. Execute o script

```bash
python analise.py
```

### 3. Escolha a origem dos logs

```text
1 - Usar a pasta padrão './logs/'
2 - Informar manualmente o caminho dos arquivos
```

### 4. Escolha como quer gerar o relatório

```text
1 - Exibir somente no terminal
2 - Salvar somente em arquivo .txt
3 - Exibir no terminal E salvar em arquivo
4 - Não gerar relatório
```

O relatório (se salvo) fica na mesma pasta dos logs.

---

## 📈 Gráficos Gerados

O script cria automaticamente:

| Arquivo gerado       | Conteúdo                                       |
|----------------------|-----------------------------------------------|
| `tensao.png`         | Tensão RMS (fase A) ao longo do tempo         |
| `corrente.png`       | Corrente RMS (fase A) ao longo do tempo       |
| `potencia.png`       | Potência ativa (fase A) ao longo do tempo     |

Todos os gráficos são salvos na **pasta onde estão os logs**.

---

## ⚡ Cálculo de kWh/dia

O consumo diário é estimado por:

```text
kWh_dia = max(epa_c) - min(epa_c), por dia
```

Um exemplo de saída:

```text
            kWh_dia
2025-11-15    3.10
2025-11-16    3.05
2025-11-17    3.20
2025-11-18    3.08
```

Caso o SM-W lite+ esteja configurado com escala alternativa, basta ajustar o fator na função `calcular_kwh_por_dia()`.

---

## 🚨 Detecção de Outliers (IQR)

Para cada grandeza:

- `uarms_V`  
- `iarms_A`  
- `pa_W`

o script usa o método IQR:

```text
outlier < Q1 − 1.5·IQR
outlier > Q3 + 1.5·IQR
```

O relatório inclui:

- limites superior e inferior  
- Q1, Q3  
- quantidade total de outliers  
- até 10 exemplos por grandeza  

---

## 📝 Relatório Automático

O relatório reúne:

- estatísticas (`describe()` do pandas)  
- consumo diário em kWh  
- limites de outliers  
- amostras de valores fora da faixa  

Ele é salvo como:

```text
relatorio_analise_logs.txt
```

---

## 🔧 Customização

O sistema pode ser facilmente expandido para:

- cálculo de custo (R$/dia, R$/mês)  
- exportação para PDF  
- comparação entre períodos (ex.: antes/depois de correção elétrica)  
- suporte a múltiplas fases (A/B/C)  

---

## 📜 Licença

MIT License

---

## 💡 Documentação em Inglês

Para a versão em inglês da documentação, consulte o arquivo [`README_EN.md`](README_EN.md).
