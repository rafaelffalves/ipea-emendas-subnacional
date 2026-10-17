import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

print("Carregando o painel de dados...")
df = pd.read_csv("painel_regressao_ipea.csv")

# 1. Configuração do Índice do Painel
# O linearmodels exige que o DataFrame tenha um MultiIndex: (entidade, tempo)
df = df.set_index(['id_municipio', 'ano'])

# 2. Definição das Variáveis
# Y = Variável Dependente (Esforço Fiscal / Arrecadação Própria)
Y = df['arrecadacao_propria']

# X = Variáveis Independentes
# Adicionamos a constante para que o modelo estime o intercepto corretamente
exog_vars = ['emendas_recebidas']
X = sm.add_constant(df[exog_vars])

# 3. Estimação do Modelo
# entity_effects=True controla as características fixas do município (ex: tamanho da costa, clima)
# time_effects=True controla choques macroeconômicos que afetam todos num dado ano (ex: pandemia, PIB nacional)
print("\nRodando Regressão de Efeitos Fixos (Município e Ano)...")
modelo = PanelOLS(Y, X, entity_effects=True, time_effects=True)

# Erros padrão clusterizados por entidade são mandatórios aqui, 
# pois os erros do mesmo município ao longo dos anos são correlacionados (autocorrelação serial)
resultados = modelo.fit(cov_type='clustered', cluster_entity=True)# 4. Exibição do Relatório
print("\n" + "="*80)
print(resultados.summary)
print("="*80)