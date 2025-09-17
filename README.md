# 🏀 NBA Shot Prediction ML Model

Um projeto completo de Machine Learning para previsão de arremessos na NBA, desenvolvido como parte da Fase 3 do curso MLET da FIAP. O projeto inclui coleta de dados, engenharia de features, modelagem e uma interface web interativa para análise.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Coleta de Dados](#-coleta-de-dados)
- [Modelagem](#-modelagem)
- [Dashboard](#-dashboard)
- [Estrutura dos Dados](#-estrutura-dos-dados)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🎯 Visão Geral

Este projeto implementa um modelo de Machine Learning para prever a probabilidade de sucesso de arremessos na NBA. Utilizando dados históricos de arremessos coletados da NBA API, o modelo analisa diversos fatores como:

- Posição do arremesso (coordenadas x, y)
- Distância da cesta
- Zona de arremesso
- Tipo de arremesso

O modelo final utiliza XGBoost e alcança alta precisão na previsão de arremessos, sendo apresentado através de um dashboard interativo desenvolvido em Streamlit.

## ✨ Funcionalidades

### 🔍 Análise Exploratória de Dados (EDA)
- Visualização de distribuições de arremessos
- Análise de performance por zona de arremesso
- Estatísticas descritivas dos dados

### 🛠️ Engenharia de Features
- Criação de features derivadas
- Encoding de variáveis categóricas
- Normalização e padronização de dados
- Feature selection e otimização

### 🤖 Modelagem de Machine Learning
- Múltiplos algoritmos testados (XGBoost, Random Forest, etc.)
- **Separação temporal realista**: Treino com temporadas 2022-23 e 2023-24, teste com 2024-25
- Validação cruzada e otimização de hiperparâmetros
- Métricas de avaliação detalhadas
- Análise de importância das features

### 📊 Dashboard Interativo
- Visualização de shot charts
- Análise de performance por time e jogador
- Métricas de POE (Points Over Expected)
- Análise de erros do modelo

## 📁 Estrutura do Projeto

```
MLET_FIAP_FASE3_NBA_ML_MODEL/
├── 📁 configs/                    # Configurações do projeto
│   ├── database_setup.py         # Setup do banco de dados
│   └── seasons_config.py         # Configuração das temporadas
├── 📁 data/                      # Dados processados (gerados pelos notebooks)
│   └── (arquivos CSV gerados automaticamente)
├── 📁 frontend/                   # Interface web
│   └── app.py                    # Dashboard Streamlit
├── 📁 models/                     # Modelos treinados
│   └── xgb_best_model.joblib     # Melhor modelo XGBoost
├── 📁 notebooks/                  # Jupyter notebooks
│   ├── 01_EDA.ipynb              # Análise exploratória
│   ├── 02_engenharia_features.ipynb
│   ├── 03_modeling_ml.ipynb
│   └── 04_analyzing_ml.ipynb
├── 📁 src/                        # Scripts de coleta de dados
│   ├── collect_roster.py         # Coleta de elencos
│   └── collect_shotchart.py      # Coleta de dados de arremessos
├── nba_shots.sqlite              # Banco de dados SQLite
├── requirements.txt              # Dependências Python
└── README.md                     # Este arquivo
```

## 🔧 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git
- Jupyter Notebook ou JupyterLab
- Dados coletados no banco SQLite (execute os scripts de coleta primeiro)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/MLET_FIAP_FASE3_NBA_ML_MODEL.git
cd MLET_FIAP_FASE3_NBA_ML_MODEL
```

### 2. Crie um ambiente virtual (recomendado)

```bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

```bash
python configs/database_setup.py
```

### 5. Gere os dados processados

**Importante:** Os arquivos de dados CSV são gerados automaticamente pelos notebooks. Execute os notebooks na ordem correta para gerar os dados necessários:

```bash
# Execute os notebooks em ordem para gerar os dados:
# 1. 01_EDA.ipynb (carrega dados do banco)
# 2. 02_engenharia_features.ipynb (gera features)
# 3. 03_modeling_ml.ipynb (treina modelo e salva)
# 4. 04_analyzing_ml.ipynb (análise final)
```

## 💻 Uso

### Executar o Dashboard

**Pré-requisito:** Execute todos os notebooks primeiro para gerar os dados necessários.

```bash
cd frontend
streamlit run app.py
```

O dashboard estará disponível em `http://localhost:8501`

**Troubleshooting:** Se o dashboard não carregar, verifique se:
- Os notebooks foram executados na ordem correta
- Os arquivos CSV existem na pasta `data/`
- O modelo `xgb_best_model.joblib` existe na pasta `models/`

### Executar Análises nos Notebooks

```bash
jupyter notebook notebooks/
```

## 📊 Coleta de Dados

### Coletar Dados de Arremessos

```bash
python src/collect_shotchart.py
```

### Coletar Dados de Elencos

```bash
python src/collect_roster.py
```

**Nota:** A coleta de dados pode demorar várias horas dependendo das temporadas selecionadas. Os scripts incluem delays para respeitar os limites da NBA API.

### Configurar Temporadas

Edite o arquivo `configs/seasons_config.py` para selecionar as temporadas desejadas:

```python
DEFAULT_SEASONS = ["2024-25", "2023-24", "2022-23"]
```

## 🤖 Modelagem

O projeto inclui um pipeline completo de modelagem:

1. **Pré-processamento**: Limpeza e transformação dos dados
2. **Feature Engineering**: Criação de features derivadas
3. **Separação Temporal**: Dados divididos por temporada (mais realista que split aleatório)
4. **Modelagem**: Treinamento de múltiplos algoritmos
5. **Otimização**: Tuning de hiperparâmetros
6. **Avaliação**: Métricas de performance detalhadas

### Executar o Pipeline de Modelagem

**Ordem obrigatória dos notebooks:**

1. **01_EDA.ipynb** - Análise exploratória e carregamento dos dados do banco SQLite
2. **02_engenharia_features.ipynb** - Criação de features e preparação dos dados (inclui coluna season)
3. **03_modeling_ml.ipynb** - Separação temporal e treinamento do modelo
4. **04_analyzing_ml.ipynb** - Análise de performance e métricas do modelo

```bash
# Execute no Jupyter Notebook ou JupyterLab:
jupyter notebook notebooks/
```

**Nota:** O dashboard só funcionará após executar todos os notebooks, pois ele depende dos arquivos CSV gerados pelo notebook 03.

### Estratégia de Separação Temporal

O projeto utiliza uma abordagem mais realista para separação dos dados:

- **Dados de Treino**: Temporadas 2022-23 e 2023-24
- **Dados de Teste**: Temporada 2024-25

Esta estratégia simula melhor o cenário real de produção, onde o modelo é treinado com dados históricos e testado com dados futuros, evitando vazamento de informação temporal.

## 📈 Dashboard

O dashboard interativo oferece:

### 🏀 Shot Charts
- Visualização de arremessos em quadra
- Código de cores para diferentes resultados
- Análise por jogador e time

### 📊 Métricas de Performance
- **POE (Points Over Expected)**: Pontos acima da expectativa
- **FG% Real vs Esperado**: Comparação de aproveitamento
- **Análise por Zona**: Performance em diferentes áreas da quadra

### 🔍 Análise de Erros
- Falsos Positivos e Falsos Negativos
- Identificação de padrões de erro
- Insights para melhoria do modelo

## 🗄️ Estrutura dos Dados

### Fluxo de Dados

1. **Coleta**: Scripts em `src/` coletam dados da NBA API
2. **Armazenamento**: Dados salvos no banco SQLite `nba_shots.sqlite`
3. **Processamento**: Notebooks processam e geram arquivos CSV em `data/`
4. **Modelagem**: Modelo treinado e salvo em `models/`
5. **Visualização**: Dashboard consome dados processados

### Tabelas do Banco de Dados

- **teams**: Informações dos times
- **players**: Dados dos jogadores
- **games**: Informações dos jogos
- **game_shot_charts**: Dados de arremessos (tabela principal)
- **game_events**: Eventos dos jogos
- **player_positions**: Posições dos jogadores

### Arquivos CSV Gerados

Os notebooks geram automaticamente os seguintes arquivos na pasta `data/`:
- `X_train_encoded.csv`: Features de treino
- `X_test_encoded.csv`: Features de teste
- `y_train.csv`: Labels de treino
- `y_test.csv`: Labels de teste
- `df.csv`: Dataset original processado

### Features Principais

- `loc_x`, `loc_y`: Coordenadas do arremesso
- `shot_distance`: Distância da cesta
- `shot_zone_basic`: Zona básica de arremesso
- `action_type`: Tipo de ação
- `period`: Período do jogo
- `minutes_remaining`, `seconds_remaining`: Tempo restante
- `season`: Temporada (usada para separação temporal)
- `time_remaining_in_game`: Tempo total restante no jogo
- `shot_angle`: Ângulo do arremesso em relação à cesta

## 🛠️ Desenvolvimento

### Adicionando Novas Features

1. Modifique o notebook de engenharia de features
2. Re-treine o modelo
3. Atualize o dashboard se necessário

### Melhorando o Modelo

1. Experimente novos algoritmos
2. Ajuste hiperparâmetros
3. Adicione mais features
4. Use técnicas de ensemble

## 🔧 Troubleshooting

### Problemas Comuns

**Dashboard não carrega:**
- Verifique se executou todos os notebooks na ordem correta
- Confirme se os arquivos CSV existem na pasta `data/`
- Verifique se o modelo `xgb_best_model.joblib` existe

**Erro ao executar notebooks:**
- Certifique-se de que o banco SQLite tem dados coletados
- Execute primeiro os scripts de coleta de dados
- Verifique se todas as dependências estão instaladas

**Erro de memória:**
- O dataset é grande, considere usar uma máquina com mais RAM
- Processe os dados em chunks menores se necessário

**Erro na NBA API:**
- Os scripts incluem delays para respeitar limites da API
- Se houver muitos erros, aumente os delays nos scripts

## 📝 Dependências Principais

- **FastAPI**: API backend
- **Streamlit**: Interface web
- **Pandas**: Manipulação de dados
- **Scikit-learn**: Machine Learning
- **XGBoost**: Algoritmo principal
- **Plotly**: Visualizações interativas
- **SQLite**: Banco de dados

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- **Leonardo Martini** - *Desenvolvimento Principal* - [GitHub](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- FIAP - Faculdade de Informática e Administração Paulista
- NBA API - Dados oficiais da NBA
- Comunidade Python e Machine Learning

## 📞 Contato

Para dúvidas ou sugestões, entre em contato:

- Email: seu-email@exemplo.com
- LinkedIn: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela!** ⭐
