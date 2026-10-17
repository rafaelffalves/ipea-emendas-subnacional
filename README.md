[readme_md.md](https://github.com/user-attachments/files/33613711/readme_md.md)

# Emendas Parlamentares e Esforço Fiscal Subnacional no Brasil (2021–2024)

Pipeline de dados e análise econométrica em dados em painel para testar a hipótese de substituição fiscal (*crowding-out*) decorrente do repasse de emendas orçamentárias federais sobre a arrecadação própria dos municípios brasileiros.

---

## Visão Geral do Projeto

O debate sobre federalismo fiscal e impositividade orçamentária no Brasil frequentemente levanta a hipótese de que transferências intergovernamentais discricionárias geram relaxamento no esforço tributário subnacional (*crowding-out*), levando prefeituras a desmobilizar a cobrança de impostos próprios (IPTU e ISS) diante do afluxo de recursos federais.

Este repositório implementa um pipeline reprodutível de ponta a ponta:
1. **Extração e Tratamento:** Coleta de microdados da execução orçamentária de emendas federais (API do Portal da Transparência / CGU) e dados fiscais municipais (Siconfi / Tesouro Nacional via BigQuery com `basedosdados`).
2. **Harmonização Cadastral:** Padronização fonética de municípios e cruzamento relacional através do identificador IBGE de 7 dígitos.
3. **Modelagem Econométrica:** Estimação por Efeitos Fixos bidirecionais (*Two-Way Fixed Effects - TWFE*) com erros padrão clusterizados ao nível municipal.

---

## Especificação Econométrica

O modelo empírico foi especificado como:

$$\text{ArrecadacaoPropria}_{it} = \beta_0 + \beta_1 \text{EmendasRecebidas}_{it} + \alpha_i + \delta_t + \varepsilon_{it}$$

Onde:

* **ArrecadacaoPropria**: Receita tributária própria realizada (ISSQN + IPTU) do município $i$ no ano $t$, obtida das declarações do DCA/FINBRA (Siconfi).
* **EmendasRecebidas**: Volume financeiro pago de emendas orçamentárias individuais e de transferências direcionadas ao município $i$ no ano $t$.
* **$\alpha_i$**: Efeito fixo municipal, que absorve todas as características municipais invariantes no tempo (geografia, histórico institucional, proximidade da capital, características costeiras, etc.).
* **$\delta_t$**: Efeito fixo de ano, que captura choques macroeconómicos e fiscais homogéneos que afetam todos os municípios conjuntamente.
* **$\varepsilon_{it}$**: Termo de erro idiossincrático, com variância clusterizada por município para mitigar autocorrelação serial e heterocedasticidade residual.
---

## 📊 Principais Resultados Empíricos

A estimação foi realizada sobre um painel com **5.569 municípios** observados entre **2021 e 2024** ($N \times T = 27.540$ observações):

```text
=================================================================================
                          PanelOLS Estimation Summary                            
=================================================================================
Dep. Variable:      arrecadacao_propria   R-squared:                    5.425e-05
Estimator:                     PanelOLS   R-squared (Between):            -0.0001
No. Observations:                 27540   R-squared (Within):           6.611e-05
Cov. Estimator:               Clustered   F-statistic:                     1.1917
Entities:                          5569   P-value:                         0.2750
Time periods:                         5   F-statistic (robust):            0.0518
                                          P-value (robust):                0.8199
=================================================================================
                    Parameter   Std. Err.     T-stat    P-value  Lower CI   Upper CI
---------------------------------------------------------------------------------
const               3.485e+07   1.625e+05     214.49     0.0000 3.453e+07  3.517e+07
emendas_recebidas     -226.49      994.76    -0.2277     0.8199   -2176.3     1723.3
=================================================================================
F-test for Poolability: 145.63  (P-value: 0.0000)
Included effects: Entity (Município), Time (Ano)
```

### Interpretação Econômica
* **Ausência de Efeito Significante:** O parâmetro pontual $\beta_1 = -226{,}49$ apresenta $p\text{-valor} = 0{,}8199$, sendo estatisticamente indistinguível de zero a qualquer nível de significância convencional (1%, 5% ou 10%).
* **Validação Metodológica:** O teste $F$ de *Poolability* rejeitou categoricamente a hipótese nula de ausência de efeitos individuais ($p < 0{,}0001$), confirmando que a estimação por Mínimos Quadrados Ordinários agrupados (*Pooled OLS*) produziria estimadores inconsistentes por viés de variável omitida.
* **Implicação Fiscal:** Os dados empíricos não sustentam a tese de desmobilização arrecadatória municipal induzida por emendas federais no período 2021–2024. A rigidez dos gastos públicos locais e as vinculações constitucionais mínimas em saúde e educação sobrepõem-se a eventuais incentivos de complacência tributária local.

---

##  Tecnologias e Bibliotecas

* **Linguagem:** Python 3.10+
* **Manipulação de Dados:** `pandas`, `numpy`
* **Conexão e Requisições:** `requests`, `urllib3`
* **Data Lakehouse:** `basedosdados` (Google Cloud BigQuery)
* **Modelagem Econométrica:** `linearmodels`, `statsmodels`

---

##  Estrutura do Repositório

```text
├── data/
│   ├── emendas_tratadas_painel.csv   # Base intermediária de emendas extraídas da API
│   └── painel_regressao_ipea.csv     # Painel balanceado consolidado (merge IBGE)
├── scripts/
│   ├── 01_extrator_emendas.py        # Extração da API do Portal da Transparência
│   ├── 02_pipeline_siconfi_merge.py  # Consulta BigQuery e consolidação municipal
│   └── 03_modelo_painel_ols.py       # Estimação Two-Way Fixed Effects com linearmodels
├── requirements.txt                  # Lista de dependências do ambiente
└── README.md                         # Documentação e resultados do projeto
```

---

##  Como Reproduzir o Estudo

### 1. Clonar o Repositório e Instalar Dependências

```bash
git clone https://github.com/SEU_USUARIO/ipea-emendas-subnacional.git
cd ipea-emendas-subnacional
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar Chaves de Acesso
1. **Portal da Transparência:** Gere sua chave de API gratuita no [Portal da Transparência do Governo Federal](https://portaldatransparencia.gov.br/api-de-dados).
2. **Google Cloud Platform:** Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/) para obter seu `PROJECT_ID` gratuito para executar queries no BigQuery via `basedosdados`.

Insira essas credenciais nos scripts correspondentes em `scripts/`.

### 3. Execução dos Módulos

```bash
# Passo 1: Extrair dados de emendas federais (2021-2024)
python scripts/01_extrator_emendas.py

# Passo 2: Extrair dados tributários no Siconfi e integrar painel
python scripts/02_pipeline_siconfi_merge.py

# Passo 3: Estimar o modelo de Efeitos Fixos
python scripts/03_modelo_painel_ols.py
```

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais detalhes.
