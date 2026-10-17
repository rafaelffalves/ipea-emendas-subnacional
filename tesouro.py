import basedosdados as bd
import pandas as pd

PROJECT_ID = "SEU_PROJECT_ID_AQUI" # Mantenha sua chave do Google Cloud

# ==========================================
# 1. TRATAMENTO DAS EMENDAS (AGORA EM PAINEL) E IBGE
# ==========================================
print("1. Processando emendas temporais e buscando códigos IBGE...")

# Lendo o novo arquivo com os anos de 2021 a 2024
df_emendas = pd.read_csv("emendas_tratadas_painel.csv")

# Extrai a cidade e UF da string bruta
df_emendas[['municipio', 'uf']] = df_emendas['localidadeDoGasto'].str.extract(r'^(.*?)\s*-\s*([A-Z]{2})$')
df_emendas = df_emendas.dropna(subset=['uf']).copy()

def padronizar_string(serie):
    return serie.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper().str.strip()

df_emendas['municipio_padrao'] = padronizar_string(df_emendas['municipio'])

# Puxa o dicionário oficial do IBGE via SQL
df_ibge = bd.read_sql("SELECT id_municipio, sigla_uf, nome FROM `basedosdados.br_bd_diretorios_brasil.municipio`", billing_project_id=PROJECT_ID)
df_ibge['municipio_padrao'] = padronizar_string(df_ibge['nome'])

# PROCV / Merge (Cruza pelo Nome Padronizado + UF)
df_emendas_ibge = pd.merge(
    df_emendas, 
    df_ibge[['id_municipio', 'sigla_uf', 'municipio_padrao']], 
    left_on=['municipio_padrao', 'uf'], 
    right_on=['municipio_padrao', 'sigla_uf'], 
    how='inner'
)

# Limpa strings financeiras para float
df_emendas_ibge['valorPago'] = df_emendas_ibge['valorPago'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.')) if pd.notna(x) else 0.0)

# AQUI ESTÁ A GRANDE MUDANÇA: O ANO ENTROU NO GROUPBY
painel_emendas = df_emendas_ibge.groupby(['ano', 'id_municipio', 'uf', 'municipio'])['valorPago'].sum().reset_index()
painel_emendas.rename(columns={'valorPago': 'emendas_recebidas'}, inplace=True)

# ==========================================
# 2. EXTRAÇÃO DO ESFORÇO FISCAL (SICONFI)
# ==========================================
print("\n2. Baixando esforço fiscal nacional (Isso leva 1 a 2 minutos)...")
query_siconfi = """
SELECT ano, id_municipio, valor
FROM `basedosdados.br_me_siconfi.municipio_receitas_orcamentarias`
WHERE ano >= 2021
    AND estagio = 'Receitas Brutas Realizadas'
    AND (LOWER(conta) LIKE '%predial e territorial urbana%' 
         OR LOWER(conta) LIKE '%serviços de qualquer natureza%')
"""
df_siconfi = bd.read_sql(query=query_siconfi, billing_project_id=PROJECT_ID)

# Consolida a arrecadação própria (IPTU + ISS)
df_esforco = df_siconfi.groupby(['ano', 'id_municipio'])['valor'].sum().reset_index()
df_esforco.rename(columns={'valor': 'arrecadacao_propria'}, inplace=True)

# ==========================================
# 3. MERGE FINAL (DUPLA CHAVE: ANO E MUNICÍPIO)
# ==========================================
print("\n3. Montando o painel da regressão temporal...")

df_esforco['id_municipio'] = df_esforco['id_municipio'].astype(str)
painel_emendas['id_municipio'] = painel_emendas['id_municipio'].astype(str)

# MERGE COM DUPLA CHAVE (ano e id_municipio)
painel_final = pd.merge(df_esforco, painel_emendas[['ano', 'id_municipio', 'emendas_recebidas']], on=['ano', 'id_municipio'], how='left')

# Quem não recebeu emenda ganha 0 no respectivo ano
painel_final['emendas_recebidas'] = painel_final['emendas_recebidas'].fillna(0)

print("\n--- AMOSTRA DO PAINEL FINAL ---")
print(painel_final.sort_values(by='emendas_recebidas', ascending=False).head(10))

painel_final.to_csv("painel_regressao_ipea.csv", index=False)
print("\nSucesso! Arquivo 'painel_regressao_ipea.csv' gerado e pronto para efeitos fixos.")