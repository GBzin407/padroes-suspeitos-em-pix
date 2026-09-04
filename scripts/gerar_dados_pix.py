# Passo 1 do projeto de padrões suspeitos em Pix
# Gera uma base simulada de transações, já com alguns padrões
# suspeitos injetados de propósito (pra depois serem achados pelo SQL):
#   - Smurfing: várias transferências pequenas, mesma origem, mesmo minuto
#   - Valor repetido: mesmo CPF origem repete o mesmo valor várias vezes
#   - Horário atípico: transação de valor alto entre 1h e 5h da manhã
# Saída: pix_transacoes.csv
 
import random
from datetime import datetime, timedelta
from faker import Faker
 
fake = Faker("pt_BR")
random.seed(42)
 
n_normais = 5000
tipos_transacao = ["Pix Enviado", "Pix Recebido", "Pagamento", "Transferência", "Saque Pix"]
 
data_inicio = datetime(2026, 1, 1)
data_fim = datetime(2026, 1, 31, 23, 59, 59)
 
def cpf_fake():
    return fake.cpf()
 
def timestamp_normal():
    delta = data_fim - data_inicio
    segundos = random.randint(0, int(delta.total_seconds()))
    ts = data_inicio + timedelta(seconds=segundos)
    # concentra a maior parte das transações no horário comercial (6h-23h)
    if random.random() < 0.85:
        ts = ts.replace(hour=random.randint(6, 23))
    return ts
 
def valor_normal():
    # maioria de valores baixos/médios, poucos altos (distribuição realista)
    return round(random.lognormvariate(3.5, 1.2), 2)
 
linhas = []
 
# transações normais
cpfs = [cpf_fake() for _ in range(500)]
 
for i in range(n_normais):
    ts = timestamp_normal()
    linhas.append({
        "id_transacao": i + 1,
        "cpf_origem": random.choice(cpfs),
        "cpf_destino": random.choice(cpfs),
        "tipo_transacao": random.choice(tipos_transacao),
        "valor": valor_normal(),
        "data": ts.date().isoformat(),
        "hora": ts.strftime("%H:%M:%S"),
    })
 
next_id = n_normais + 1
 
# padrão suspeito: smurfing (várias transferências pequenas, mesmo minuto)
for _ in range(15):  # 15 "surtos" de smurfing
    origem = cpf_fake()
    ts_base = timestamp_normal().replace(second=0, microsecond=0)
    for _ in range(random.randint(6, 12)):
        linhas.append({
            "id_transacao": next_id,
            "cpf_origem": origem,
            "cpf_destino": cpf_fake(),
            "tipo_transacao": "Pix Enviado",
            "valor": round(random.uniform(50, 300), 2),
            "data": ts_base.date().isoformat(),
            "hora": ts_base.strftime("%H:%M:%S"),
        })
        next_id += 1
 
# padrão suspeito: valor repetido
for _ in range(10):
    origem = cpf_fake()
    valor_fixo = round(random.choice([100, 250, 500, 1000, 1500]), 2)
    for _ in range(random.randint(4, 8)):
        ts = timestamp_normal()
        linhas.append({
            "id_transacao": next_id,
            "cpf_origem": origem,
            "cpf_destino": cpf_fake(),
            "tipo_transacao": "Pix Enviado",
            "valor": valor_fixo,
            "data": ts.date().isoformat(),
            "hora": ts.strftime("%H:%M:%S"),
        })
        next_id += 1
 
# padrão suspeito: horário atípico + valor alto
for _ in range(20):
    ts = timestamp_normal().replace(hour=random.randint(1, 5))
    linhas.append({
        "id_transacao": next_id,
        "cpf_origem": cpf_fake(),
        "cpf_destino": cpf_fake(),
        "tipo_transacao": "Pix Enviado",
        "valor": round(random.uniform(5000, 20000), 2),
        "data": ts.date().isoformat(),
        "hora": ts.strftime("%H:%M:%S"),
    })
    next_id += 1
 
random.shuffle(linhas)
 
import csv
with open("../dados/pix_transacoes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=linhas[0].keys())
    writer.writeheader()
    writer.writerows(linhas)
 
print(f"Gerado pix_transacoes.csv com {len(linhas)} transações.")