import sqlite3

def create_database(db_name="nba_shots.sqlite"):
    """Cria o banco de dados SQLite e as tabelas necessárias se não existirem."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Usamos 'TEXT' para maior flexibilidade e 'INTEGER PRIMARY KEY' para autoincremento
    # A sintaxe é ligeiramente ajustada para ser compatível com SQLite
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        team_name TEXT NOT NULL,
        team_abbreviation TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        player_name TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id TEXT PRIMARY KEY,
        game_date TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_shot_charts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT NOT NULL,
        game_event_id INTEGER,
        player_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        period INTEGER,
        minutes_remaining INTEGER,
        seconds_remaining INTEGER,
        shot_made_flag INTEGER NOT NULL, -- SQLite usa 0 para False, 1 para True
        loc_x INTEGER,
        loc_y INTEGER,
        shot_distance INTEGER,
        action_type TEXT,
        shot_type TEXT,
        shot_zone_basic TEXT,
        shot_zone_area TEXT,
        shot_zone_range TEXT,
        FOREIGN KEY (game_id) REFERENCES games (id),
        FOREIGN KEY (player_id) REFERENCES players (id),
        FOREIGN KEY (team_id) REFERENCES teams (id)
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT NOT NULL,
        event_number INTEGER NOT NULL,
        event_message_type INTEGER,
        home_description TEXT,
        visitor_description TEXT,
        score_margin INTEGER,
        UNIQUE(game_id, event_number)
    );
    ''')

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
    print(f"Banco de dados '{db_name}' e tabelas verificados/criados com sucesso.")

if __name__ == "__main__":
    create_database()