# Passo 6 do projeto de padrões suspeitos em Pix
# Roda as 3 regras de consultas_deteccao.sql e consolida o resultado
# numa única tabela (alertas_pix.csv), pronta pra importar no Power BI

import sqlite3
import csv

conn = sqlite3.connect("../db/pix.db")
cur = conn.cursor()

alertas = []

# smurfing
for cpf_origem, minuto, qtd, valor_total, valor_medio, risco in cur.execute("""
    SELECT cpf_origem, minuto, COUNT(*), SUM(valor), ROUND(AVG(valor), 2),
           CASE WHEN COUNT(*) >= 8 THEN 'ALTO' WHEN COUNT(*) >= 5 THEN 'MEDIO' ELSE 'NORMAL' END
    FROM transacoes_pix
    WHERE tipo_transacao = 'Pix Enviado'
    GROUP BY cpf_origem, minuto
    HAVING COUNT(*) >= 5
"""):
    alertas.append({
        "tipo_alerta": "SMURFING",
        "cpf_origem": cpf_origem,
        "data_hora_referencia": minuto,
        "quantidade": qtd,
        "valor_total": valor_total,
        "risco": risco,
    })

# valor repetido
for cpf_origem, valor, qtd, primeira, ultima, risco in cur.execute("""
    SELECT cpf_origem, valor, COUNT(*), MIN(data), MAX(data),
           CASE WHEN COUNT(*) >= 6 THEN 'ALTO' WHEN COUNT(*) >= 4 THEN 'MEDIO' ELSE 'NORMAL' END
    FROM transacoes_pix
    WHERE tipo_transacao = 'Pix Enviado'
    GROUP BY cpf_origem, valor
    HAVING COUNT(*) >= 4
"""):
    alertas.append({
        "tipo_alerta": "VALOR_REPETIDO",
        "cpf_origem": cpf_origem,
        "data_hora_referencia": ultima,
        "quantidade": qtd,
        "valor_total": round(valor * qtd, 2),
        "risco": risco,
    })

# horário atípico
for id_t, cpf_origem, data, hora, valor, risco in cur.execute("""
    SELECT id_transacao, cpf_origem, data, hora, valor,
           CASE WHEN valor >= 5000 THEN 'ALTO' WHEN valor >= 1000 THEN 'MEDIO' ELSE 'NORMAL' END
    FROM transacoes_pix
    WHERE tipo_transacao = 'Pix Enviado'
      AND CAST(SUBSTR(hora, 1, 2) AS INTEGER) BETWEEN 0 AND 5
      AND valor >= 1000
"""):
    alertas.append({
        "tipo_alerta": "HORARIO_ATIPICO",
        "cpf_origem": cpf_origem,
        "data_hora_referencia": f"{data} {hora}",
        "quantidade": 1,
        "valor_total": valor,
        "risco": risco,
    })

with open("../dados/alertas_pix.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=alertas[0].keys())
    writer.writeheader()
    writer.writerows(alertas)

print(f"Gerado alertas_pix.csv com {len(alertas)} alertas.")