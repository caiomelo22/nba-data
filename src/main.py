import pandas as pd
from services import ScrapperService, MySQLService, NBAService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General info
start_season = 2022
end_season = 2022

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

print(scrapper_service.nba_seasons.head())

# mysql_service = MySQLService()
# first_season = next(iter(scrapper_service.fbref_seasons))
# mysql_service.create_table_from_df("matches", scrapper_service.fbref_seasons[first_season])

# for season in scrapper_service.fbref_seasons:
#     data_list = scrapper_service.fbref_seasons[season].to_dict(orient="records")
#     mysql_service.insert_multiple_rows("matches", data_list)
    
# mysql_service.close()