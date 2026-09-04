# Detecção de Padrões Suspeitos em Pix
 
Projeto que analisa transações Pix pra encontrar padrões que podem indicar fraude. Usa Python, SQLite, SQL, DAX e Power BI.
 
Todos os dados são simulados, criados só pra fins de estudo.
 
## Objetivo
 
O projeto simula um cenário de prevenção a fraudes em transações Pix.
 
A partir de uma base de transações, três padrões suspeitos são identificados:
 
- várias transferências feitas pelo mesmo CPF no mesmo minuto
- o mesmo CPF repetindo várias vezes o mesmo valor
- transações de valor alto em horário incomum, como de madrugada
Depois de encontrar esses padrões, os alertas são exportados pra um CSV e analisados num painel do Power BI.
 
## Resultado
 
A base de alertas encontrou 45 casos suspeitos, sendo 38 de alto risco. O tipo mais comum foi horário atípico (20 alertas), seguido por smurfing (15) e valor repetido (10). O valor total envolvido nesses alertas passa de R$ 27 milhões.
 
## Tecnologias usadas
 
- Python
- SQLite
- SQL
- DAX
- Power BI
- CSV
- GitHub
## Estrutura do projeto
 
- `gerar_dados_pix.py` cria a base de transações
- `carregar_dados.py` carrega os dados no banco
- `consultas_deteccao.sql` tem as consultas que encontram os padrões suspeitos
- `exportar_alertas.py` gera o arquivo final de alertas
- `pix_transacoes.csv` é a base de transações gerada
- `alertas_pix.csv` é o resultado com os alertas
- `pix.db` é o banco de dados
- `Projeto_Pix_Deteccao_Padroes_Suspeitos.pbix` é o painel do Power BI
## Como o processo funciona
 
O `gerar_dados_pix.py` cria a base de transações e salva em `pix_transacoes.csv`. O `carregar_dados.py` lê esse CSV e carrega no banco `pix.db`. As consultas em `consultas_deteccao.sql` procuram os padrões suspeitos nesse banco. O `exportar_alertas.py` roda essas consultas e gera o `alertas_pix.csv`. Por fim, o Power BI se conecta nesse CSV e monta o dashboard de alertas.
 
## Sobre os dados
 
O arquivo `gerar_dados_pix.py` cria uma base simulada de transações Pix, com:
 
- ID da transação
- CPF de origem
- CPF de destino
- tipo de transação
- valor
- data
- hora
Os tipos de transação são: Pix Enviado, Pix Recebido, Pagamento, Transferência e Saque Pix.
 
A base tem 5.000 transações normais, além das transações que simulam os padrões suspeitos de propósito, pra testar as regras de detecção.
 
## Banco de dados
 
O `carregar_dados.py` lê o CSV e cria o banco `pix.db`, com a tabela `transacoes_pix`:
 
- `id_transacao` – identificador da transação
- `cpf_origem` – CPF que iniciou a transação
- `cpf_destino` – CPF que recebeu a transação
- `tipo_transacao` – tipo da operação
- `valor` – valor da transação
- `data` – data da operação
- `hora` – horário da operação
- `minuto` – data, hora e minuto juntos
 
Também são criados índices pra facilitar as buscas por CPF, minuto, valor e horário.
 
## Regras de detecção
 
As regras usam SQL, com `GROUP BY`, `HAVING` e `CASE`.
 
### Smurfing
 
Identifica quando o mesmo CPF faz 5 ou mais transferências Pix no mesmo minuto.
 
- Menos de 5 transações – Normal
- 5 a 7 transações – Médio
- 8 ou mais transações – Alto
 
O objetivo é achar uma concentração incomum de transferências num intervalo muito curto.
 
### Valor repetido
 
Identifica quando o mesmo CPF faz 4 ou mais transações com exatamente o mesmo valor.
 
- Menos de 4 repetições – Normal
- 4 a 5 repetições – Médio
- 6 ou mais repetições – Alto
 
O objetivo é achar repetição sistemática de operações com o mesmo valor.
 
### Horário atípico
 
Identifica transações de Pix enviado feitas entre 00h e 05h59, com valor de R$ 1.000 ou mais.
 
- De R$ 1.000 até R$ 4.999,99 – Médio
- R$ 5.000 ou mais – Alto
 
O objetivo é achar transações de valor alto feitas num horário considerado incomum.
 
## Alertas exportados
 
O `exportar_alertas.py` roda as regras e gera o `alertas_pix.csv`, com os campos:
 
- `tipo_alerta` – tipo do padrão identificado
- `cpf_origem` – CPF relacionado ao alerta
- `data_hora_referencia` – data e hora do alerta
- `quantidade` – quantidade de transações relacionadas
- `valor_total` – valor total associado ao alerta
- `risco` – classificação do risco
 
Os tipos de alerta são: `SMURFING`, `VALOR_REPETIDO` e `HORARIO_ATIPICO`.
 
## Painel Power BI
 
O arquivo `Projeto_Pix_Deteccao_Padroes_Suspeitos.pbix` tem o dashboard com os indicadores e gráficos pra analisar os alertas.
 
Indicadores calculados em DAX:
 
```DAX
Total Alertas =
COUNTROWS('alertas_pix')
```
 
```DAX
Alertas Alto Risco =
CALCULATE(
    COUNTROWS('alertas_pix'),
    'alertas_pix'[risco] = "ALTO"
)
```
 
```DAX
Alertas Médio Risco =
CALCULATE(
    COUNTROWS('alertas_pix'),
    'alertas_pix'[risco] = "MEDIO"
)
```
 
```DAX
Valor Total Suspeito =
SUM('alertas_pix'[valor_total])
```
 
```DAX
CPFs Envolvidos =
DISTINCTCOUNT('alertas_pix'[cpf_origem])
```
 
## Dashboard
 
O painel mostra:
 
- total de alertas
- alertas de alto risco
- alertas de médio risco
- valor total suspeito
- quantidade de CPFs envolvidos
- gráfico de alertas por tipo
- gráfico de distribuição por risco
- tabela detalhada dos alertas
- filtro por tipo de alerta, por risco e por CPF de origem
## Como rodar
 
Requisitos: Python 3, SQLite e Power BI Desktop.
 
1. Gere os dados: `python gerar_dados_pix.py` (cria `pix_transacoes.csv`)
2. Crie o banco: `python carregar_dados.py` (cria `pix.db`)
3. Gere os alertas: `python exportar_alertas.py` (cria `alertas_pix.csv`)
4. Abra o `Projeto_Pix_Deteccao_Padroes_Suspeitos.pbix` no Power BI
## Exemplo de análise
 
Um alerta de `SMURFING` acontece quando um CPF faz pelo menos 5 transações de Pix enviado no mesmo minuto.
 
Um alerta de `VALOR_REPETIDO` acontece quando um CPF faz pelo menos 4 transações de Pix enviado com o mesmo valor.
 
Um alerta de `HORARIO_ATIPICO` acontece quando um Pix enviado de pelo menos R$ 1.000 é feito entre 00h e 05h.
 
## Sobre o projeto
 
O projeto mostra um fluxo completo de análise de dados: geração dos dados em Python, armazenamento no SQLite, detecção de padrões em SQL, exportação dos alertas em CSV e visualização em DAX e Power BI.
 
A ideia é mostrar, de forma prática, como dados de transações podem ser usados pra identificar comportamentos fora do padrão.
 
Este projeto tem finalidade só educacional. Os CPFs, valores e transações usados são fictícios e não representam dados reais de clientes ou operações bancárias.
 
## Autor
 
Gabriel de Oliveira Irineu
 
[LinkedIn](https://www.linkedin.com/in/gabriel-irineu/) · [GitHub](https://github.com/GBzin407)