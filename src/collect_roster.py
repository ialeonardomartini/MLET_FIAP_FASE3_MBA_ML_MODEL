import time
import pandas as pd
from nba_api.stats.endpoints import commonteamroster
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
    
    tables_to_clear = ['player_positions']
    
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
    CREATE TABLE IF NOT EXISTS player_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        player_id INTEGER NOT NULL,
        position TEXT NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players (id)
    );
    ''')
        
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

def get_rosters_for_team(team_id, season, max_retries=3):
    """Busca os dados de jogadores para um time em uma temporada no endpoint commonteamroster."""
    for attempt in range(max_retries):
        try:
            print(f"  -> Buscando rosters para o time {team_id} na temporada {season}... (tentativa {attempt + 1}/{max_retries})")
            
            # Delay aleatório entre 1.5 e 3 segundos para evitar rate limiting
            delay = random.uniform(1.5, 3.0)
            time.sleep(delay)
            
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)

            df_roster = roster.get_data_frames()

            if df_roster and len(df_roster) > 0:
                print(f"  -> Dados obtidos com sucesso para o time {team_id}")
                return df_roster[0]  # Return the first DataFrame from the list
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

def verify_data_integrity(conn):
    """Verifica a integridade dos dados coletados."""
    
    print("\n=== VERIFICANDO INTEGRIDADE DOS DADOS ===")
    
    # Verificar estatísticas finais
    final_counts = {}
    for table in ['player_positions']:
        count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', conn)
        final_counts[table] = count.iloc[0,0]
        print(f"{table}: {final_counts[table]} linhas")
    
    # Verificar distribuição por posição
    position_distribution = pd.read_sql_query('''
        SELECT position, COUNT(*) as count 
        FROM player_positions 
        GROUP BY position 
        ORDER BY count DESC
    ''', conn)
    
    print(f"\nDistribuição por posição:")
    for _, row in position_distribution.iterrows():
        print(f"  {row['position']}: {row['count']} jogadores")
    
    # Verificar times únicos
    unique_teams = pd.read_sql_query('''
        SELECT COUNT(DISTINCT player_id) as unique_players
        FROM player_positions
    ''', conn)
    
    print(f"\nTotal de jogadores únicos: {unique_teams.iloc[0,0]}")
    
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
            
            df_player_positions = get_rosters_for_team(team_id, season)

            # Check if df_player_positions is a list and extract the first DataFrame
            if isinstance(df_player_positions, list) and len(df_player_positions) > 0:
                df_player_positions = df_player_positions[0]
            elif not isinstance(df_player_positions, pd.DataFrame):
                print(f"  -> Nenhum dado de roster encontrado para {team_name} na temporada {season}.")
                failed_teams += 1
                continue
            
            if df_player_positions.empty:
                print(f"  -> Nenhum dado de roster encontrado para {team_name} na temporada {season}.")
                failed_teams += 1
                continue

            # --- Transform and Load ---
            try:
                df_player_positions = df_player_positions[['PLAYER','PLAYER_ID', 'POSITION']].dropna(subset=['PLAYER', 'PLAYER_ID', 'POSITION'])
                df_player_positions = df_player_positions.drop_duplicates(subset=['PLAYER_ID'])
                df_player_positions.rename(columns={'PLAYER': 'player_name','PLAYER_ID': 'player_id','POSITION': 'position'}, inplace=True)

                df_player_positions.to_sql('player_positions', conn, if_exists='append', index=False)
                print(f"  -> {len(df_player_positions)} posições de jogadores processadas e salvas para {team_name}.")
                successful_teams += 1
                
            except sqlite3.IntegrityError:
                # Skip duplicate player positions
                print(f"  -> Jogadores do time {team_name} já existem no banco. Pulando...")
                pass
            except Exception as e:
                print(f"  -> Erro ao processar dados para {team_name}: {e}")
                failed_teams += 1
            
            # Pausa a cada 10 times para dar um respiro na API
            if i % 10 == 0:
                print(f"  -> Pausa de 5 segundos após processar {i} times...")
                time.sleep(5)

    # Verificar integridade dos dados coletados
    verify_data_integrity(conn)
    
    print(f"\nPipeline de ETL concluído!")
    print(f"Times processados com sucesso: {successful_teams}")
    print(f"Times com falha: {failed_teams}")
    print(f"Taxa de sucesso: {successful_teams/(successful_teams+failed_teams)*100:.1f}%")
    conn.close()

if __name__ == "__main__":
    run_etl_pipeline(SEASONS)