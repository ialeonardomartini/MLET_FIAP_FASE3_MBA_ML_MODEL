# Configuração das temporadas da NBA para coleta de dados
# Formato: "YYYY-YY" (ex: "2024-25" para temporada 2024-2025)

# Temporadas disponíveis para coleta
AVAILABLE_SEASONS = [
    "2024-25",  # Temporada atual
    "2023-24",  # Temporada anterior
    "2022-23",  # Temporada 2022-2023
    "2021-22",  # Temporada 2021-2022
    "2020-21",  # Temporada 2020-2021
    "2019-20",  # Temporada 2019-2020
    "2018-19",  # Temporada 2018-2019
    "2017-18",  # Temporada 2017-2018
    "2016-17",  # Temporada 2016-2017
    "2015-16",  # Temporada 2015-2016
    "2014-15",  # Temporada 2014-2015
    "2013-14",  # Temporada 2013-2014
    "2012-13",  # Temporada 2012-2013
    "2011-12",  # Temporada 2011-2012
    "2010-11",  # Temporada 2010-2011
    "2009-10",  # Temporada 2009-2010
    "2008-09",  # Temporada 2008-2009
    "2007-08",  # Temporada 2007-2008
    "2006-07",  # Temporada 2006-2007
    "2005-06",  # Temporada 2005-2006
    "2004-05",  # Temporada 2004-2005
    "2003-04",  # Temporada 2003-2004
    "2002-03",  # Temporada 2002-2003
    "2001-02",  # Temporada 2001-2002
    "2000-01",  # Temporada 2000-2001
    "1999-00",  # Temporada 1999-2000
    "1998-99",  # Temporada 1998-1999
    "1997-98",  # Temporada 1997-1998
    "1996-97",  # Temporada 1996-1997
    "1995-96",  # Temporada 1995-1996
    "1994-95",  # Temporada 1994-1995
    "1993-94",  # Temporada 1993-1994
    "1992-93",  # Temporada 1992-1993
    "1991-92",  # Temporada 1991-1992
    "1990-91",  # Temporada 1990-1991
    "1989-90",  # Temporada 1989-1990
    "1988-89",  # Temporada 1988-1989
    "1987-88",  # Temporada 1987-1988
    "1986-87",  # Temporada 1986-1987
    "1985-86",  # Temporada 1985-1986
    "1984-85",  # Temporada 1984-1985
    "1983-84",  # Temporada 1983-1984
    "1982-83",  # Temporada 1982-1983
    "1981-82",  # Temporada 1981-1982
    "1980-81",  # Temporada 1980-1981
    "1979-80",  # Temporada 1979-1980
    "1978-79",  # Temporada 1978-1979
    "1977-78",  # Temporada 1977-1978
    "1976-77",  # Temporada 1976-1977
    "1975-76",  # Temporada 1975-1976
    "1974-75",  # Temporada 1974-1975
    "1973-74",  # Temporada 1973-1974
    "1972-73",  # Temporada 1972-1973
    "1971-72",  # Temporada 1971-1972
    "1970-71",  # Temporada 1970-1971
    "1969-70",  # Temporada 1969-1970
    "1968-69",  # Temporada 1968-1969
    "1967-68",  # Temporada 1967-1968
    "1966-67",  # Temporada 1966-1967
    "1965-66",  # Temporada 1965-1966
    "1964-65",  # Temporada 1964-1965
    "1963-64",  # Temporada 1963-1964
    "1962-63",  # Temporada 1962-1963
    "1961-62",  # Temporada 1961-1962
    "1960-61",  # Temporada 1960-1961
    "1959-60",  # Temporada 1959-1960
    "1958-59",  # Temporada 1958-1959
    "1957-58",  # Temporada 1957-1958
    "1956-57",  # Temporada 1956-1957
    "1955-56",  # Temporada 1955-1956
    "1954-55",  # Temporada 1954-1955
    "1953-54",  # Temporada 1953-1954
    "1952-53",  # Temporada 1952-1953
    "1951-52",  # Temporada 1951-1952
    "1950-51",  # Temporada 1950-1951
    "1949-50",  # Temporada 1949-1950
    "1948-49",  # Temporada 1948-1949
    "1947-48",  # Temporada 1947-1948
    "1946-47",  # Temporada 1946-1947
]

# Temporadas padrão para coleta (pode ser modificado conforme necessidade)
DEFAULT_SEASONS = ["2024-25", "2023-24", "2022-23"]

# Função para validar formato de temporada
def validate_season_format(season):
    """
    Valida se o formato da temporada está correto (YYYY-YY)
    
    Args:
        season (str): String da temporada no formato "YYYY-YY"
        
    Returns:
        bool: True se o formato estiver correto, False caso contrário
    """
    import re
    pattern = r'^\d{4}-\d{2}$'
    if not re.match(pattern, season):
        return False
    
    # Verificar se o segundo ano é o próximo ano do primeiro
    year1 = int(season[:4])
    year2 = int(season[5:])
    
    # Para anos como 2024-25, o segundo ano deve ser 25
    expected_year2 = year1 % 100 + 1
    if year2 != expected_year2:
        return False
    
    return True

# Função para obter temporadas válidas
def get_valid_seasons(seasons_list):
    """
    Filtra uma lista de temporadas, retornando apenas as válidas
    
    Args:
        seasons_list (list): Lista de strings de temporadas
        
    Returns:
        list: Lista de temporadas válidas
    """
    valid_seasons = []
    for season in seasons_list:
        if validate_season_format(season):
            valid_seasons.append(season)
        else:
            print(f"Aviso: Formato de temporada inválido ignorado: {season}")
    
    return valid_seasons

# Função para obter temporadas por década
def get_seasons_by_decade(start_year, end_year):
    """
    Gera uma lista de temporadas entre dois anos
    
    Args:
        start_year (int): Ano de início (ex: 2020)
        end_year (int): Ano de fim (ex: 2024)
        
    Returns:
        list: Lista de temporadas no formato "YYYY-YY"
    """
    seasons = []
    for year in range(start_year, end_year + 1):
        season = f"{year}-{str(year + 1)[-2:].zfill(2)}"
        seasons.append(season)
    
    return seasons
