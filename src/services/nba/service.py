from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.static import teams 
from functools import reduce
import pandas as pd

class NBAService():
    def __init__(self, start_season, end_season):
        self.start_season = start_season
        self.end_season = end_season

        self.season_games = []
        self.player_season_games = []

    def get_season_games(self, season):
        regular_season_games = leaguegamelog.LeagueGameLog(season = str(season), season_type_all_star='Regular Season').get_data_frames()[0]
        regular_season_games['IS_PLAYOFFS'] = False

        playoffs_games = leaguegamelog.LeagueGameLog(season = str(season), season_type_all_star='Regular Season').get_data_frames()[0]
        playoffs_games['IS_PLAYOFFS'] = True

        season_games = reduce(lambda left,right: pd.merge(left,right, how='outer'), [regular_season_games, playoffs_games])

        return season_games

    def get_player_season_games(self, season):
        regular_season_games = leaguegamelog.LeagueGameLog(season = str(season), player_or_team_abbreviation = 'P', season_type_all_star='Regular Season').get_data_frames()[0]
        regular_season_games['IS_PLAYOFFS'] = False

        playoffs_games = leaguegamelog.LeagueGameLog(season = str(season), player_or_team_abbreviation = 'P', season_type_all_star='Regular Season').get_data_frames()[0]
        playoffs_games['IS_PLAYOFFS'] = True

        players_season_games = reduce(lambda left,right: pd.merge(left,right, how='outer'), [regular_season_games, playoffs_games])

        return players_season_games
    
    def get_seasons_info(self):
        for season in range(self.start_season,self.end_season+1):
            season_games = self.get_season_games(season)
            player_season_games = self.get_player_season_games(season)
            
            self.season_games.append(season_games)
            self.player_season_games.append(player_season_games)

            print("{}/{}".format(season, self.end_season))

    def clean_seasons_info(self):
        self.season_games = reduce(lambda  left,right: pd.merge(left,right, how='outer'), self.season_games)
        self.player_season_games = reduce(lambda  left,right: pd.merge(left,right, how='outer'), self.player_season_games)
        
        self.season_games.dropna(subset=['FG_PCT','FT_PCT','FG3_PCT'], inplace=True)

        self.season_games['GAME_ID'] = pd.to_numeric(self.season_games['GAME_ID'])
        self.player_season_games['GAME_ID'] = pd.to_numeric(self.player_season_games['GAME_ID'])

        self.season_games['GAME_DATE'] = pd.to_datetime(self.season_games['GAME_DATE'])
        self.player_season_games['GAME_DATE'] = pd.to_datetime(self.player_season_games['GAME_DATE'])

        self.season_games = self.season_games.sort_values(['GAME_DATE', 'GAME_ID'], ascending=[True, True]).reset_index(drop=True)

    def run_nba_pipeline(self):

        self.get_seasons_info()

        self.clean_seasons_info()

        return self.season_games, self.player_season_games