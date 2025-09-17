import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Arc
import os
import sqlite3
import joblib
import numpy as np

# --- Caminhos Absolutos para os Dados, DB e Modelo ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(BASE_DIR, '..', 'nba_shots.sqlite')
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'xgb_best_model.joblib')

X_TEST_PATH = os.path.join(DATA_DIR, 'X_test.csv')
DF_ORIGINAL_PATH = os.path.join(DATA_DIR, 'df.csv')

# --- Carregamento do Modelo (feito uma vez) ---
@st.cache_resource
def load_model():
    """Carrega o modelo de machine learning."""
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except FileNotFoundError:
        st.error(f"Arquivo do modelo não encontrado em {MODEL_PATH}.")
        return None

# --- Funções Auxiliares de Desenho ---
def draw_court(ax=None, color='gray', lw=2, zorder=0):
    if ax is None: ax = plt.gca()
    hoop = plt.Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False, zorder=zorder)
    backboard = plt.Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color, zorder=zorder)
    outer_box = plt.Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False, zorder=zorder)
    inner_box = plt.Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False, zorder=zorder)
    three_point_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color, fill=False, zorder=zorder)
    ax.plot([-220, -220], [-47.5, 92.5], linewidth=lw, color=color, zorder=zorder)
    ax.plot([220, 220], [-47.5, 92.5], linewidth=lw, color=color, zorder=zorder)
    for element in [hoop, backboard, outer_box, inner_box, three_point_arc]:
        ax.add_patch(element)
    return ax

# --- Carregamento e Preparação dos Dados ---
@st.cache_data
def load_data():
    """Carrega e prepara os dados para o dashboard."""
    try:
        df_features = pd.read_csv(X_TEST_PATH, engine='pyarrow')
        df_original = pd.read_csv(DF_ORIGINAL_PATH, engine='pyarrow')
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar arquivos CSV: {e}.")
        return None, None

    df_analysis = df_original.loc[df_features.index].copy()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT id as player_id, player_name FROM players"
        df_players = pd.read_sql_query(query, conn)
        conn.close()
        df_analysis = pd.merge(df_analysis, df_players, on='player_id', how='left')
        df_analysis['player_display'] = df_analysis['player_name'].fillna(df_analysis['player_id'].astype(str))
    except Exception as e:
        st.warning(f"Não foi possível ler os nomes do DB. Usando 'player_id'. Erro: {e}")
        df_analysis['player_display'] = df_analysis['player_id'].astype(str)
    
    team_id_map = { 1610612737: "Atlanta Hawks", 1610612738: "Boston Celtics", 1610612739: "Cleveland Cavaliers", 1610612740: "New Orleans Pelicans", 1610612741: "Chicago Bulls", 1610612742: "Dallas Mavericks", 1610612743: "Denver Nuggets", 1610612744: "Golden State Warriors", 1610612745: "Houston Rockets", 1610612746: "LA Clippers", 1610612747: "Los Angeles Lakers", 1610612748: "Miami Heat", 1610612749: "Milwaukee Bucks", 1610612750: "Minnesota Timberwolves", 1610612751: "Brooklyn Nets", 1610612752: "New York Knicks", 1610612753: "Orlando Magic", 1610612754: "Indiana Pacers", 1610612755: "Philadelphia 76ers", 1610612756: "Phoenix Suns", 1610612757: "Portland Trail Blazers", 1610612758: "Sacramento Kings", 1610612759: "San Antonio Spurs", 1610612760: "Oklahoma City Thunder", 1610612761: "Toronto Raptors", 1610612762: "Utah Jazz", 1610612763: "Memphis Grizzlies", 1610612764: "Washington Wizards", 1610612765: "Detroit Pistons", 1610612766: "Charlotte Hornets"}
    df_analysis['team_name'] = df_analysis['team_id'].map(team_id_map)

    df_analysis.dropna(subset=['team_name'], inplace=True)
    
    common_indices = df_features.index.intersection(df_analysis.index)
    df_features = df_features.loc[common_indices]
    df_analysis = df_analysis.loc[common_indices]

    return df_features, df_analysis

# --- Função de Predição e Análise ---
def get_analytical_data(model, df_team_features, df_team_analysis):
    df_predicted = df_team_analysis.copy()
    
    probabilities = model.predict_proba(df_team_features)[:, 1]
    df_predicted['shot_probability'] = probabilities
    df_predicted['predicted_outcome'] = (df_predicted['shot_probability'] >= 0.5).astype(int)
    
    mean_poe_bias = (df_predicted['shot_made_flag'] - df_predicted['shot_probability']).mean()
    df_predicted['poe'] = df_predicted['shot_made_flag'] - df_predicted['shot_probability']
    df_predicted['adjusted_poe'] = df_predicted['poe'] - mean_poe_bias

    return df_predicted

# --- Interface Principal ---
st.set_page_config(layout="wide")
st.title("Dashboard de Análise de Arremessos da NBA")

model = load_model()
df_features, df_analysis = load_data()

if all(df is not None for df in [model, df_features, df_analysis]):
    st.sidebar.header("Filtros")
    team_list = sorted(df_analysis['team_name'].unique())
    
    # Gerencia o estado da seleção para o filtro funcionar corretamente
    if 'selected_team' not in st.session_state:
        st.session_state['selected_team'] = team_list[0]

    selected_team = st.sidebar.selectbox("Selecione um Time:", team_list, index=team_list.index(st.session_state['selected_team']))

    if selected_team != st.session_state['selected_team']:
        st.session_state['selected_team'] = selected_team
        if 'df_team_predicted' in st.session_state:
            del st.session_state['df_team_predicted']

    st.header(f"Análises para: {selected_team}")

    if st.sidebar.button("Analisar Time"):
        with st.spinner("Analisando arremessos..."):
            team_indices = df_analysis[df_analysis['team_name'] == selected_team].index
            df_team_analysis = df_analysis.loc[team_indices].copy()
            df_team_features = df_features.loc[team_indices].copy()
            df_team_predicted = get_analytical_data(model, df_team_features, df_team_analysis)
            st.session_state['df_team_predicted'] = df_team_predicted
    
    if 'df_team_predicted' in st.session_state:
        df_team_predicted = st.session_state['df_team_predicted']

        tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Análise de POE", "Análise por Jogador", "Análise de Erros"])

        with tab1:
            st.subheader("Performance do Modelo por Zona de Arremesso")
            zone_perf = df_team_predicted.groupby('shot_zone_basic').agg(
                FG_Real=('shot_made_flag', 'mean'),
                FG_Esperado=('shot_probability', 'mean')
            ).rename(columns={'FG_Real': 'Aproveitamento Real', 'FG_Esperado': 'Aproveitamento Esperado (xFG)'})


            fig, ax = plt.subplots(figsize=(12, 6))
            zone_perf.plot(kind='bar', ax=ax, width=0.8)
            ax.set_title(f'Aproveitamento Real vs. Esperado por Zona - {selected_team}', fontsize=16)
            ax.set_ylabel('Taxa de Aproveitamento (FG%)')
            ax.set_xlabel('')
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            for container in ax.containers:
                ax.bar_label(container, fmt='%.2f')
            st.pyplot(fig)

        with tab2:
            st.subheader("Pontos Acima da Expectativa (POE)")
            player_poe = df_team_predicted.groupby('player_display').agg(
                total_adjusted_poe=('adjusted_poe', 'sum'),
                avg_adjusted_poe_per_shot=('adjusted_poe', 'mean'),
                total_shots=('game_id', 'count')
            ).sort_values(by='total_adjusted_poe', ascending=False).reset_index()

            st.write("#### Performance Geral (Total de POE Ajustado)")
            st.bar_chart(player_poe.set_index('player_display')['total_adjusted_poe'])

            col1, col2 = st.columns(2)
            with col1:
                st.write("✅ **Top 5 Performers**")
                st.dataframe(player_poe.head(5))
            with col2:
                st.write("❌ **Piores 5 Performers**")
                st.dataframe(player_poe.tail(5).sort_values(by='total_adjusted_poe', ascending=True))

        with tab3:
            st.subheader("Análise Individual por Jogador")
            player_list = sorted(df_team_predicted['player_display'].unique())
            selected_player = st.selectbox("Selecione um Jogador:", player_list)

            if selected_player:
                df_player = df_team_predicted[df_team_predicted['player_display'] == selected_player]
                
                # Layout em colunas para os gráficos
                col_shot, col_dist = st.columns([1, 1.2])

                with col_shot:
                    st.write(f"**Shot Chart de {selected_player}**")
                    conditions = [
                        (df_player['shot_made_flag'] == 1) & (df_player['predicted_outcome'] == 1),
                        (df_player['shot_made_flag'] == 0) & (df_player['predicted_outcome'] == 0),
                        (df_player['shot_made_flag'] == 0) & (df_player['predicted_outcome'] == 1),
                        (df_player['shot_made_flag'] == 1) & (df_player['predicted_outcome'] == 0)
                    ]
                    colors = ['green', 'red', 'orange', 'purple']
                    df_player['result_color'] = pd.Series(np.select(conditions, colors, default='black'), index=df_player.index)
                    
                    # --- CORREÇÃO NO TAMANHO DO GRÁFICO ---
                    fig, ax = plt.subplots(figsize=(6, 5.5)) # Reduzindo o tamanho da figura base
                    draw_court(ax)
                    ax.scatter(df_player['loc_x'], df_player['loc_y'], c=df_player['result_color'], alpha=0.8, s=40)
                    ax.set_title(f"Shot Chart de {selected_player}", fontsize=10)
                    plt.axis('off')
                    st.pyplot(fig) # Removido o use_container_width para usar o figsize
                    # --- FIM DA CORREÇÃO ---
                    st.markdown("- **Verde**: Acerto Correto\n- **Vermelho**: Erro Correto\n- **Laranja**: Falso Positivo\n- **Roxo**: Falso Negativo")

                with col_dist:
                    st.write(f"**Perfil de Arremessos vs. Média do Time**")
                    fig2, ax2 = plt.subplots(figsize=(8, 4.5))
                    sns.histplot(df_team_predicted['shot_distance'], bins=30, color='gray', stat='density', label=f'Média ({selected_team})', kde=True, ax=ax2)
                    sns.histplot(df_player['shot_distance'], bins=15, color='blue', stat='density', label=selected_player, kde=True, ax=ax2)
                    ax2.set_title(f"Distribuição da Distância dos Arremessos", fontsize=10)
                    ax2.set_xlabel('Distância (pés)')
                    ax2.legend()
                    st.pyplot(fig2)

        with tab4:
            st.subheader("Análise de Erros do Modelo para o Time")
            fp = df_team_predicted[(df_team_predicted['shot_made_flag'] == 0) & (df_team_predicted['predicted_outcome'] == 1)]
            fn = df_team_predicted[(df_team_predicted['shot_made_flag'] == 1) & (df_team_predicted['predicted_outcome'] == 0)]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Falsos Positivos (FP): {len(fp)} arremessos**")
                st.write("O modelo previu 'Cesta', mas o jogador errou.")
                if not fp.empty:
                    st.dataframe(fp['action_type'].value_counts().head())
            with col2:
                st.write(f"**Falsos Negativos (FN): {len(fn)} arremessos**")
                st.write("O modelo previu 'Erro', mas o jogador acertou.")
                if not fn.empty:
                    st.dataframe(fn['action_type'].value_counts().head())
    else:
        st.info("Clique em 'Analisar Time' na barra lateral para carregar as visualizações.")