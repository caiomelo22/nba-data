from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.static import teams 
from functools import reduce
import pandas as pd
import numpy as np
from tqdm import tqdm

class NBAService():
    def __init__(self, start_season, end_season):
        self.start_season = start_season
        self.end_season = end_season

        self.season_games = []
        self.player_season_games = []

    def get_season_games(self, season):
        regular_season_games = leaguegamelog.LeagueGameLog(season = str(season), season_type_all_star='Regular Season').get_data_frames()[0]
        regular_season_games['IS_PLAYOFFS'] = False

        playoffs_games = leaguegamelog.LeagueGameLog(season = str(season), season_type_all_star='Playoffs').get_data_frames()[0]
        playoffs_games['IS_PLAYOFFS'] = True

        season_games = reduce(lambda left,right: pd.merge(left,right, how='outer'), [regular_season_games, playoffs_games])

        return season_games

    def get_player_season_games(self, season):
        regular_season_games = leaguegamelog.LeagueGameLog(season = str(season), player_or_team_abbreviation = 'P', season_type_all_star='Regular Season').get_data_frames()[0]
        regular_season_games['IS_PLAYOFFS'] = False

        playoffs_games = leaguegamelog.LeagueGameLog(season = str(season), player_or_team_abbreviation = 'P', season_type_all_star='Playoffs').get_data_frames()[0]
        playoffs_games['IS_PLAYOFFS'] = True

        players_season_games = reduce(lambda left,right: pd.merge(left,right, how='outer'), [regular_season_games, playoffs_games])

        return players_season_games
    
    def get_seasons_info(self):
        print("Getting seasons info")
        for season in tqdm(range(self.start_season,self.end_season+1)):
            season_games = self.get_season_games(season)
            player_season_games = self.get_player_season_games(season)

            self.season_games.append(season_games)
            self.player_season_games.append(player_season_games)

    def get_teams(self):
        self.teams = []

        teams_list = teams.get_teams()

        for team in teams_list:
            self.teams.append(self.get_team_object(team))

        self.teams = pd.DataFrame(self.teams)

    def get_match_object(self, home_game, away_game, winner):
        match_info = {
            'id': home_game['GAME_ID'],
            'date': home_game['GAME_DATE'],
            'season': int(str(home_game['SEASON_ID'])[1:]),
            'is_playoff': home_game['IS_PLAYOFFS'],
            'winner': winner,

            'home_id': home_game['TEAM_ID'],
            'home_team': home_game['TEAM_NAME'],
            'home_pts': home_game['PTS'],
            'home_fgm': home_game['FGM'],
            'home_fga': home_game['FGA'],
            'home_fg_pct': home_game['FG_PCT'],
            'home_fg3m': home_game['FG3M'],
            'home_fg3a': home_game['FG3A'],
            'home_fg3_pct': home_game['FG3_PCT'],
            'home_ftm': home_game['FTM'],
            'home_fta': home_game['FTA'],
            'home_ft_pct': home_game['FT_PCT'],
            'home_oreb': home_game['OREB'],
            'home_dreb': home_game['DREB'],
            'home_reb': home_game['REB'],
            'home_ast': home_game['AST'],
            'home_stl': home_game['STL'],
            'home_blk': home_game['BLK'],
            'home_tov': home_game['TOV'],
            'home_pf': home_game['PF'],
            
            'away_id': away_game['TEAM_ID'],
            'away_team': away_game['TEAM_NAME'],
            'away_pts': away_game['PTS'],
            'away_fgm': away_game['FGM'],
            'away_fga': away_game['FGA'],
            'away_fg_pct': away_game['FG_PCT'],
            'away_fg3m': away_game['FG3M'],
            'away_fg3a': away_game['FG3A'],
            'away_fg3_pct': away_game['FG3_PCT'],
            'away_ftm': away_game['FTM'],
            'away_fta': away_game['FTA'],
            'away_ft_pct': away_game['FT_PCT'],
            'away_oreb': away_game['OREB'],
            'away_dreb': away_game['DREB'],
            'away_reb': away_game['REB'],
            'away_ast': away_game['AST'],
            'away_stl': away_game['STL'],
            'away_blk': away_game['BLK'],
            'away_tov': away_game['TOV'],
            'away_pf': away_game['PF']
        }

        return match_info
    
    def get_team_object(self, team):
        team_info = {
            'id': team['id'],
            'name': team['full_name'],
            'abbreviation': team['abbreviation']
        }
        return team_info

    def get_player_object(self, player_id, name):
        player_info = {
            'id': player_id,
            'name': name
        }
        return player_info

    def get_player_game_object(self, game):
        player_game_info = {
            'team_id': game['TEAM_ID'],
            'player_id': game['PLAYER_ID'],
            'game_id': game['GAME_ID'],
            'minutes': game['MIN'],
            'pts': game['PTS'],
            'fgm': game['FGM'],
            'fga': game['FGA'],
            'fg_pct': game['FG_PCT'],
            'fg3m': game['FG3M'],
            'fg3a': game['FG3A'],
            'fg3_pct': game['FG3_PCT'],
            'ftm': game['FTM'],
            'fta': game['FTA'],
            'ft_pct': game['FT_PCT'],
            'oreb': game['OREB'],
            'dreb': game['DREB'],
            'reb': game['REB'],
            'ast': game['AST'],
            'stl': game['STL'],
            'blk': game['BLK'],
            'tov': game['TOV'],
            'pf': game['PF'],
            'plus_minus': game['PLUS_MINUS']
        }
        return player_game_info

    def clean_seasons_info(self):
        # Merge season games and player season games
        self.season_games = reduce(lambda left, right: pd.merge(left, right, how='outer'), self.season_games)
        self.player_season_games = reduce(lambda left, right: pd.merge(left, right, how='outer'), self.player_season_games)

        # Clean up missing data
        self.season_games.dropna(subset=['FG_PCT', 'FT_PCT', 'FG3_PCT'], inplace=True)

        # Convert columns to appropriate data types
        self.season_games['GAME_ID'] = pd.to_numeric(self.season_games['GAME_ID'])
        self.player_season_games['GAME_ID'] = pd.to_numeric(self.player_season_games['GAME_ID'])

        self.season_games['GAME_DATE'] = pd.to_datetime(self.season_games['GAME_DATE'])
        self.player_season_games['GAME_DATE'] = pd.to_datetime(self.player_season_games['GAME_DATE'])

        # Sort the season games by date and game ID
        self.season_games = self.season_games.sort_values(['GAME_DATE', 'GAME_ID'], ascending=[True, True]).reset_index(drop=True)

        season_games_cleaned = []
        player_season_games_cleaned = []
        self.players = []

        # Group by GAME_ID to process each game
        for game_id, game_group in tqdm(self.season_games.groupby('GAME_ID'), desc="Processing season games"):
            # Ensure the group contains exactly two rows (home and away)
            if len(game_group) != 2:
                continue

            # Extract home and away rows based on 'MATCHUP'
            if '@' in game_group.iloc[0]['MATCHUP']:
                away_game = game_group.iloc[0]
                home_game = game_group.iloc[1]
                winner = 'H' if home_game['WL'] == 'W' else 'A'
            else:
                home_game = game_group.iloc[0]
                away_game = game_group.iloc[1]
                winner = 'H' if home_game['WL'] == 'W' else 'A'

            # Get players for the current game
            game_players = self.player_season_games.loc[self.player_season_games['GAME_ID'] == game_id]
            game_players = game_players.replace({np.nan: 0})

            # Append cleaned game data
            season_games_cleaned.append(self.get_match_object(home_game, away_game, winner))

            # Process and append player data
            for _, player in game_players.iterrows():
                self.players.append(self.get_player_object(player['PLAYER_ID'], player['PLAYER_NAME'].replace("'", "")))
                player_season_games_cleaned.append(self.get_player_game_object(player))

        # Convert lists to DataFrames
        self.players = pd.DataFrame(self.players)
        self.season_games = pd.DataFrame(season_games_cleaned)
        self.player_season_games = pd.DataFrame(player_season_games_cleaned)


    def run_nba_pipeline(self):

        self.get_teams()

        self.get_seasons_info()

        self.clean_seasons_info()

        return self.season_games, self.player_season_games