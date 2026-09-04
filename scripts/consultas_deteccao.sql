-- ==========================================================
-- consultas_deteccao.sql
-- Consultas de detecção de padrões suspeitos em transações Pix
-- Base: pix.db / tabela transacoes_pix
-- ==========================================================

-- ------------------------------------------------------------
-- 1) SMURFING (fracionamento)
-- Regra: mesmo CPF de origem faz várias transações "Pix Enviado"
-- no mesmo minuto. É o padrão clássico de quem fraciona um valor
-- grande em várias transferências pequenas pra não chamar atenção.
-- Sinalização: >=5 transações no minuto = risco MÉDIO; >=8 = ALTO.
-- ------------------------------------------------------------
SELECT
    cpf_origem,
    minuto,
    COUNT(*)   AS qtd_transacoes,
    SUM(valor) AS valor_total,
    ROUND(AVG(valor), 2) AS valor_medio,
    CASE
        WHEN COUNT(*) >= 8 THEN 'ALTO'
        WHEN COUNT(*) >= 5 THEN 'MEDIO'
        ELSE 'NORMAL'
    END AS risco_smurfing
FROM transacoes_pix
WHERE tipo_transacao = 'Pix Enviado'
GROUP BY cpf_origem, minuto
HAVING COUNT(*) >= 5
ORDER BY qtd_transacoes DESC;


-- ------------------------------------------------------------
-- 2) VALOR REPETIDO
-- Regra: mesmo CPF de origem envia o mesmo valor exato várias vezes.
-- Valor "redondo" repetido é indício de teste de conta laranja
-- ou de golpe estruturado (mesmo script/automação por trás).
-- Sinalização: >=6 repetições = risco ALTO; >=4 = MÉDIO.
-- ------------------------------------------------------------
SELECT
    cpf_origem,
    valor,
    COUNT(*) AS qtd_repeticoes,
    MIN(data) AS primeira_data,
    MAX(data) AS ultima_data,
    CASE
        WHEN COUNT(*) >= 6 THEN 'ALTO'
        WHEN COUNT(*) >= 4 THEN 'MEDIO'
        ELSE 'NORMAL'
    END AS risco_valor_repetido
FROM transacoes_pix
WHERE tipo_transacao = 'Pix Enviado'
GROUP BY cpf_origem, valor
HAVING COUNT(*) >= 4
ORDER BY qtd_repeticoes DESC;


-- ------------------------------------------------------------
-- 3) HORÁRIO ATÍPICO + VALOR ALTO
-- Regra: transação de valor alto realizada de madrugada (00h-05h59),
-- fora do horário normal de uso da maioria das contas. Combinação
-- "valor alto + madrugada" é clássica em golpes (ex: sequestro
-- relâmpago, conta invadida, engenharia social).
-- Sinalização: valor >= 5000 = risco ALTO; valor >= 1000 = MÉDIO.
-- ------------------------------------------------------------
SELECT
    id_transacao,
    cpf_origem,
    cpf_destino,
    data,
    hora,
    valor,
    CASE
        WHEN valor >= 5000 THEN 'ALTO'
        WHEN valor >= 1000 THEN 'MEDIO'
        ELSE 'NORMAL'
    END AS risco_horario_atipico
FROM transacoes_pix
WHERE tipo_transacao = 'Pix Enviado'
  AND CAST(SUBSTR(hora, 1, 2) AS INTEGER) BETWEEN 0 AND 5
  AND valor >= 1000
ORDER BY valor DESC;
