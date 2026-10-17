import requests
import pandas as pd
import warnings
import time
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

CHAVE = "SUA_CHAVE_AQUI"
url = "https://api.portaldatransparencia.gov.br/api-de-dados/emendas"
cabecalho = {"chave-api-dados": CHAVE, "accept": "application/json"}

registros = []
anos_analise = [2021, 2022, 2023, 2024]

print("Iniciando extração do painel longitudinal...")

for ano in anos_analise:
    print(f"Coletando emendas de {ano}...")
    # Coletando as 5 primeiras páginas de cada ano para construir a amostra
    for pagina in range(1, 6):
        parametros = {"ano": ano, "pagina": pagina}
        resposta = requests.get(url, headers=cabecalho, params=parametros, verify=False)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            if not dados:
                break
            registros.extend(dados)
        else:
            print(f"Erro no ano {ano}, pág {pagina}: {resposta.status_code}")
            break
        time.sleep(0.5) # Pausa para evitar bloqueio da API

df = pd.DataFrame(registros)

# Filtra apenas transferências e garante que a coluna 'ano' seja inteira
df_filtrado = df[df['tipoEmenda'].str.contains("Transferência", case=False, na=False)].copy()
df_filtrado['ano'] = df_filtrado['ano'].astype(int)

df_filtrado.to_csv("emendas_tratadas_painel.csv", index=False, encoding="utf-8-sig")
print(f"Sucesso! {len(df_filtrado)} registros salvos em 'emendas_tratadas_painel.csv'.")