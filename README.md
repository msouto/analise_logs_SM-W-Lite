# Analisador de Logs – SM-W Lite+ (IE Tecnologia)

Este repositório contém um script em Python para **análise de logs** gerados pelo equipamento **SM-W Lite+**, da **IE Tecnologia**, focado no monitoramento de:

- Tensão RMS da fase A (`uarms`)
- Corrente RMS da fase A (`iarms`)
- Potência ativa da fase A (`pa`)
- Consumo acumulado (`epa_c`)

O sistema gera:

- 📈 Gráficos de **tensão**, **corrente** e **potência** ao longo do tempo  
- ⚡ Estimativa de **kWh por dia**, a partir do acumulado `epa_c`  
- 🚨 Detecção automática de **outliers** (via IQR)  
- 📝 **Relatório automático** com estatísticas, kWh/dia e lista de outliers (opcional, exibido no terminal, salvo em arquivo `.txt` ou ambos)

---

## 🧩 Formato dos arquivos de log

Os arquivos de log são esperados no formato:

```text
hora:minuto:segundo:pa:epa_c:epa_g:iarms:uarms
