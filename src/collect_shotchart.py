import time
import pandas as pd
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import teams, players
import sqlite3
import os
import random

# --- CONFIGURAÇÃO ---
# Defina as temporadas que você quer coletar
SEASONS = ["2024-25", "2023-24", "2022-23"]
DB_NAME = "nba_shots.sqlite"
# Arquivo para marcar que o setup inicial foi feito e evitar recriação
SETUP_DONE_FILE = "db_setup.done"

def clear_tables(conn):
    """Limpa as tabelas antes de inserir novos dados para garantir dados apenas da rodagem atual."""
    print("\n=== LIMPANDO TABELAS PARA NOVA RODAGEM ===")
    
    tables_to_clear = ['game_shot_charts', 'players', 'games', 'teams']
    
    for table in tables_to_clear:
        try:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table}")
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"  -> Tabela '{table}' limpa: {deleted_count} registros removidos")
        except Exception as e:
            print(f"  -> Erro ao limpar tabela '{table}': {e}")
    
    print("=== LIMPEZA CONCLUÍDA ===\n")

def setup_database():
    """Cria o banco de dados e as tabelas se ainda não foram criados."""
    if not os.path.exists(SETUP_DONE_FILE):
        print("Executando o setup inicial do banco de dados...")
        # Apaga o banco de dados antigo para garantir um estado limpo
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
            print(f"Banco de dados '{DB_NAME}' antigo removido.")
            
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Criação das tabelas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY, team_name TEXT NOT NULL, team_abbreviation TEXT NOT NULL
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY, player_name TEXT
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY, game_date TEXT NOT NULL
        );''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_shot_charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, game_id TEXT NOT NULL, game_event_id INTEGER,
            player_id INTEGER NOT NULL, team_id INTEGER NOT NULL, period INTEGER,
            minutes_remaining INTEGER, seconds_remaining INTEGER, shot_made_flag INTEGER NOT NULL,
            loc_x INTEGER, loc_y INTEGER, shot_distance INTEGER, action_type TEXT, shot_type TEXT,
            shot_zone_basic TEXT, shot_zone_area TEXT, shot_zone_range TEXT, season TEXT NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games (id),
            FOREIGN KEY (player_id) REFERENCES players (id),
            FOREIGN KEY (team_id) REFERENCES teams (id)
        );''')
        
        conn.commit()
        conn.close()
        # Cria o arquivo marcador para não executar esta função novamente
        with open(SETUP_DONE_FILE, 'w') as f:
            f.write('done')
        print(f"Banco de dados '{DB_NAME}' criado com sucesso.")
    else:
        print("Setup do banco de dados já foi realizado.")

def get_all_team_ids():
    """Busca os IDs de todos os times da NBA."""
    nba_teams = teams.get_teams()
    return {team['full_name']: team['id'] for team in nba_teams}

def fetch_shot_data_for_team(team_id, season, max_retries=3):
    """Busca os dados de arremessos para um time em uma temporada."""
    for attempt in range(max_retries):
        try:
            print(f"  -> Buscando dados de arremessos para o time {team_id}... (tentativa {attempt + 1}/{max_retries})")
            
            # Delay aleatório entre 1.5 e 3 segundos para evitar rate limiting
            delay = random.uniform(1.5, 3.0)
            time.sleep(delay)
            
            # O parâmetro season_nullable é a chave para filtrar por temporada [1]
            shot_chart = shotchartdetail.ShotChartDetail(
                team_id=team_id,
                player_id=0,
                context_measure_simple='FGA',
                season_nullable=season,
                season_type_all_star='Regular Season'
            )
            
            df_list = shot_chart.get_data_frames()
            if df_list and len(df_list) > 0:
                print(f"  -> Dados obtidos com sucesso para o time {team_id}")
                return df_list
            else:
                print(f"  -> Nenhum dado encontrado para o time {team_id}")
                return None
                
        except Exception as e:
            error_msg = str(e)
            print(f"  -> Erro ao buscar dados para o time {team_id} (tentativa {attempt + 1}): {error_msg}")
            
            # Se for timeout, esperar mais tempo antes da próxima tentativa
            if "timeout" in error_msg.lower() or "read timed out" in error_msg.lower():
                wait_time = (attempt + 1) * 5  # Espera progressiva: 5s, 10s, 15s
                print(f"  -> Timeout detectado. Aguardando {wait_time} segundos antes da próxima tentativa...")
                time.sleep(wait_time)
            else:
                # Para outros erros, esperar um pouco menos
                time.sleep(2)
            
            # Se for a última tentativa, retornar None
            if attempt == max_retries - 1:
                print(f"  -> Falha após {max_retries} tentativas para o time {team_id}")
                return None
    
    return None

def fix_missing_data(conn):
    """Corrige dados faltantes nas tabelas players e games extraindo dados únicos de game_shot_charts."""
    
    print("\n=== VERIFICANDO E CORRIGINDO DADOS FALTANTES ===")
    
    # 1. Corrigir tabela players
    print("\n1. Verificando tabela players...")
    
    # Buscar todos os player_ids únicos dos shot charts
    unique_player_ids = pd.read_sql_query('''
        SELECT DISTINCT player_id 
        FROM game_shot_charts 
        ORDER BY player_id
    ''', conn)
    
    print(f"Total de player_ids únicos nos shot charts: {len(unique_player_ids)}")
    
    # Verificar quais já existem na tabela players
    existing_players = pd.read_sql_query('SELECT id FROM players', conn)
    existing_player_ids = set(existing_players['id'].tolist())
    
    # Encontrar player_ids que não estão na tabela players
    missing_player_ids = unique_player_ids[~unique_player_ids['player_id'].isin(existing_player_ids)]
    
    print(f"Player_ids faltando na tabela players: {len(missing_player_ids)}")
    
    if not missing_player_ids.empty:
        # Buscar nomes dos jogadores da API
        nba_players = players.get_players()
        player_names = {p['id']: p['full_name'] for p in nba_players}
        
        # Criar DataFrame com os jogadores faltantes
        missing_players_df = pd.DataFrame({
            'id': missing_player_ids['player_id'],
            'player_name': missing_player_ids['player_id'].map(player_names)
        })
        
        # Remover jogadores sem nome (não encontrados na API)
        missing_players_df = missing_players_df.dropna(subset=['player_name'])
        
        if not missing_players_df.empty:
            # Inserir jogadores faltantes
            missing_players_df.to_sql('players', conn, if_exists='append', index=False)
            print(f"Inseridos {len(missing_players_df)} jogadores na tabela players")
        else:
            print("Nenhum jogador válido encontrado para inserir")
    
    # 2. Corrigir tabela games
    print("\n2. Verificando tabela games...")
    
    # Buscar todos os game_ids únicos dos shot charts
    unique_game_ids = pd.read_sql_query('''
        SELECT DISTINCT game_id, MIN(game_event_id) as first_event
        FROM game_shot_charts 
        GROUP BY game_id
        ORDER BY game_id
    ''', conn)
    
    print(f"Total de game_ids únicos nos shot charts: {len(unique_game_ids)}")
    
    # Verificar quais já existem na tabela games
    existing_games = pd.read_sql_query('SELECT id FROM games', conn)
    existing_game_ids = set(existing_games['id'].tolist())
    
    # Encontrar game_ids que não estão na tabela games
    missing_game_ids = unique_game_ids[~unique_game_ids['game_id'].isin(existing_game_ids)]
    
    print(f"Game_ids faltando na tabela games: {len(missing_game_ids)}")
    
    if not missing_game_ids.empty:
        # Para games, vamos usar uma data padrão já que não temos a data real
        # Você pode ajustar isso conforme necessário
        missing_games_df = pd.DataFrame({
            'id': missing_game_ids['game_id'],
            'game_date': '20241101'  # Data padrão - você pode ajustar
        })
        
        # Inserir games faltantes
        missing_games_df.to_sql('games', conn, if_exists='append', index=False)
        print(f"Inseridos {len(missing_games_df)} jogos na tabela games")
    
    # 3. Verificar resultados finais
    print("\n3. Resultados finais...")
    
    final_counts = {}
    for table in ['teams', 'players', 'games', 'game_shot_charts']:
        count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', conn)
        final_counts[table] = count.iloc[0,0]
        print(f"{table}: {final_counts[table]} linhas")
    
    # Verificar se ainda há dados faltantes
    missing_players_final = pd.read_sql_query('''
        SELECT COUNT(DISTINCT gsc.player_id) as missing_players
        FROM game_shot_charts gsc
        LEFT JOIN players p ON gsc.player_id = p.id
        WHERE p.id IS NULL
    ''', conn)
    
    missing_games_final = pd.read_sql_query('''
        SELECT COUNT(DISTINCT gsc.game_id) as missing_games
        FROM game_shot_charts gsc
        LEFT JOIN games g ON gsc.game_id = g.id
        WHERE g.id IS NULL
    ''', conn)
    
    print(f"\nDados ainda faltando:")
    print(f"Players: {missing_players_final.iloc[0,0]}")
    print(f"Games: {missing_games_final.iloc[0,0]}")
    
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")

def run_etl_pipeline(seasons_list):
    """Executa o pipeline completo de ETL para uma lista de temporadas."""
    setup_database()
    conn = sqlite3.connect(DB_NAME)
    
    # Limpar tabelas antes de inserir novos dados
    clear_tables(conn)
    
    all_teams = get_all_team_ids()
    print(f"Iniciando coleta de dados para {len(all_teams)} times em {len(seasons_list)} temporadas...")

    # Contadores para estatísticas
    successful_teams = 0
    failed_teams = 0

    for season in seasons_list:
        print(f"\n================ PROCESSANDO TEMPORADA: {season} ================")
        for i, (team_name, team_id) in enumerate(all_teams.items(), 1):
            print(f"Processando time {i}/{len(all_teams)}: {team_name} (ID: {team_id})")
            
            df_shots = fetch_shot_data_for_team(team_id, season)
            
            # Check if df_shots is a list and extract the first DataFrame
            if isinstance(df_shots, list) and len(df_shots) > 0:
                df_shots = df_shots[0]
            elif not isinstance(df_shots, pd.DataFrame):
                print(f"  -> Nenhum dado de arremesso encontrado para {team_name} na temporada {season}.")
                failed_teams += 1
                continue
            
            if df_shots.empty:
                print(f"  -> Nenhum dado de arremesso encontrado para {team_name} na temporada {season}.")
                failed_teams += 1
                continue

            # --- Transform and Load ---
            
            try:
                # Ensure df_shots is a DataFrame
                if not isinstance(df_shots, pd.DataFrame):
                    print(f"  -> Dados inválidos para {team_name}")
                    failed_teams += 1
                    continue
                
                # 1. Popular tabela 'teams'
                df_teams = df_shots.loc[:, ['TEAM_ID']].drop_duplicates()
                df_teams.columns = ['id']
                team_info = [t for t in teams.get_teams() if t['id'] == team_id]
                if team_info:
                    df_teams['team_name'] = team_info[0]['full_name']
                    df_teams['team_abbreviation'] = team_info[0]['abbreviation']
                    try:
                        df_teams.to_sql('teams', conn, if_exists='append', index=False)
                        print(f"  -> Time {team_name} inserido na tabela teams")
                    except sqlite3.IntegrityError:
                        # Skip duplicate teams
                        print(f"  -> Time {team_name} já existe na tabela teams")

                # 2. Popular tabela 'players'
                df_players = df_shots.loc[:, ['PLAYER_ID']].drop_duplicates()
                df_players.columns = ['id']
                
                # Buscar nomes dos jogadores da API
                nba_players = players.get_players()
                player_names = {p['id']: p['full_name'] for p in nba_players}
                
                # Adicionar nomes dos jogadores
                df_players['player_name'] = df_players['id'].map(player_names)
                
                # Remover linhas onde player_name é NaN (jogadores não encontrados)
                df_players = df_players.dropna(subset=['player_name'])
                
                if not df_players.empty:
                    try:
                        df_players.to_sql('players', conn, if_exists='append', index=False)
                        print(f"  -> {len(df_players)} jogadores inseridos na tabela players")
                    except sqlite3.IntegrityError:
                        # Skip duplicate players
                        print(f"  -> Jogadores já existem na tabela players")
                else:
                    print(f"  -> Nenhum jogador válido encontrado para {team_name}")

                # 3. Popular tabela 'games'
                df_games = df_shots.loc[:, ['GAME_ID', 'GAME_DATE']].drop_duplicates()
                df_games.columns = ['id', 'game_date']
                
                if not df_games.empty:
                    try:
                        df_games.to_sql('games', conn, if_exists='append', index=False)
                        print(f"  -> {len(df_games)} jogos inseridos na tabela games")
                    except sqlite3.IntegrityError:
                        # Skip duplicate games
                        print(f"  -> Jogos já existem na tabela games")
                else:
                    print(f"  -> Nenhum jogo encontrado para {team_name}")

                # 4. Popular tabela 'game_shot_charts'
                column_mapping = {
                    'GAME_ID': 'game_id', 'GAME_EVENT_ID': 'game_event_id', 'PLAYER_ID': 'player_id',
                    'TEAM_ID': 'team_id', 'PERIOD': 'period', 'MINUTES_REMAINING': 'minutes_remaining',
                    'SECONDS_REMAINING': 'seconds_remaining', 'SHOT_MADE_FLAG': 'shot_made_flag',
                    'LOC_X': 'loc_x', 'LOC_Y': 'loc_y', 'SHOT_DISTANCE': 'shot_distance',
                    'ACTION_TYPE': 'action_type', 'SHOT_TYPE': 'shot_type',
                    'SHOT_ZONE_BASIC': 'shot_zone_basic', 'SHOT_ZONE_AREA': 'shot_zone_area',
                    'SHOT_ZONE_RANGE': 'shot_zone_range'
                }
                
                # Use a more compatible approach for column selection
                df_shots_renamed = pd.DataFrame(df_shots).copy()
                df_shots_renamed = df_shots_renamed.rename(columns=column_mapping)
                
                # Select only the columns that exist in the DataFrame
                available_columns = [col for col in column_mapping.values() if col in df_shots_renamed.columns]
                df_final_shots = df_shots_renamed.loc[:, available_columns]
                
                # Adicionar a coluna 'season'
                df_final_shots['season'] = season
                
                df_final_shots.to_sql('game_shot_charts', conn, if_exists='append', index=False)
                
                print(f"  -> {len(df_shots)} arremessos de {team_name} processados e salvos.")
                successful_teams += 1
                
            except Exception as e:
                print(f"  -> Erro ao processar dados para {team_name}: {e}")
                failed_teams += 1
            
            # Pausa a cada 5 times para dar um respiro na API
            if i % 5 == 0:
                print(f"  -> Pausa de 10 segundos após processar {i} times...")
                time.sleep(10)

    # Corrigir dados faltantes automaticamente
    fix_missing_data(conn)
    
    print(f"\nPipeline de ETL concluído!")
    print(f"Times processados com sucesso: {successful_teams}")
    print(f"Times com falha: {failed_teams}")
    print(f"Taxa de sucesso: {successful_teams/(successful_teams+failed_teams)*100:.1f}%")
    conn.close()

if __name__ == "__main__":
    run_etl_pipeline(SEASONS)