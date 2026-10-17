import pandas as pd
import numpy as np

# 1. Carrega o arquivo extraído
df = pd.read_csv("emendas_tratadas.csv")

# 2. Função para converter string financeira brasileira ('10.000,00') para float (10000.00)
def limpar_moeda(valor_str):
    if pd.isna(valor_str):
        return 0.0
    valor_limpo = str(valor_str).replace('.', '').replace(',', '.')
    return float(valor_limpo)

colunas_valor = ['valorEmpenhado', 'valorLiquidado', 'valorPago', 'valorRestoPago']
for col in colunas_valor:
    df[col] = df[col].apply(limpar_moeda)

# 3. Tratamento Espacial: Separar Município e UF (ignorando casos nacionais genéricos)
# Espera o formato "MUNICIPIO - UF"
df[['municipio', 'uf']] = df['localidadeDoGasto'].str.extract(r'^(.*?)\s*-\s*([A-Z]{2})$')

# Removemos linhas que não são municípios específicos (ex: Nacional, Múltiplo)
df_subnacional = df.dropna(subset=['uf']).copy()

# 4. Agregação: Total pago por Estado e Função (Visão Macro)
painel_uf = df_subnacional.groupby(['uf', 'funcao'])['valorPago'].sum().reset_index()
painel_uf = painel_uf.sort_values(by=['uf', 'valorPago'], ascending=[True, False])

print("--- AMOSTRA DO PAINEL TRATADO ---")
print(painel_uf.head(10))

# Salva a base final pronta para merge com IBGE/Finbra
painel_uf.to_csv("painel_emendas_limpo.csv", index=False)