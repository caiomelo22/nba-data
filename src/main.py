import pandas as pd
from services import ScrapperService, MySQLService, NBAService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General info
start_season = 2023
end_season = 2023

nba_service = NBAService(start_season=start_season, end_season=end_season)

season_games, player_season_games = nba_service.run_nba_pipeline()

scrapper_service = ScrapperService(
    start_season=start_season,
    end_season=end_season,
    nba_seasons=season_games
)

scrapper_service.start_driver()

scrapper_service.bet_explorer_scrapper()

scrapper_service.close_driver()

scrapper_service.match_seasons_data()

mysql_service = MySQLService()

mysql_service.insert_from_df("teams", nba_service.teams)
mysql_service.insert_from_df("players", nba_service.players)
mysql_service.insert_from_df("games", scrapper_service.nba_seasons)
mysql_service.insert_from_df("player_games", nba_service.player_season_games)
    
mysql_service.close()