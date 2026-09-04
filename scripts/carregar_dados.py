# Passo 2 do projeto de padrões suspeitos em Pix
# Lê pix_transacoes.csv e carrega numa base SQLite (pix.db), na tabela
# transacoes_pix, já com índices pensados pras consultas de detecção
# (por CPF origem + data/hora)

import sqlite3
import csv

db_path = "../db/pix.db"
csv_path = "../dados/pix_transacoes.csv"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS transacoes_pix")
cur.execute("""
    CREATE TABLE transacoes_pix (
        id_transacao   INTEGER PRIMARY KEY,
        cpf_origem     TEXT NOT NULL,
        cpf_destino    TEXT NOT NULL,
        tipo_transacao TEXT NOT NULL,
        valor          REAL NOT NULL,
        data           TEXT NOT NULL,   -- YYYY-MM-DD
        hora           TEXT NOT NULL,   -- HH:MM:SS
        minuto         TEXT NOT NULL    -- YYYY-MM-DD HH:MM, ajuda no GROUP BY por minuto
    )
""")

with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    linhas = [
        (
            int(r["id_transacao"]),
            r["cpf_origem"],
            r["cpf_destino"],
            r["tipo_transacao"],
            float(r["valor"]),
            r["data"],
            r["hora"],
            f'{r["data"]} {r["hora"][:5]}',  # minuto = data + HH:MM
        )
        for r in reader
    ]

cur.executemany(
    """INSERT INTO transacoes_pix
       (id_transacao, cpf_origem, cpf_destino, tipo_transacao, valor, data, hora, minuto)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    linhas,
)

# índices para as consultas de detecção (velocity por CPF/minuto, valor repetido)
cur.execute("CREATE INDEX idx_origem_minuto ON transacoes_pix (cpf_origem, minuto)")
cur.execute("CREATE INDEX idx_origem_valor ON transacoes_pix (cpf_origem, valor)")
cur.execute("CREATE INDEX idx_hora ON transacoes_pix (hora)")

conn.commit()

total = cur.execute("SELECT COUNT(*) FROM transacoes_pix").fetchone()[0]
print(f"Carregado {total} transações em {db_path} (tabela transacoes_pix).")

conn.close()