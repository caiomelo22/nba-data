from datetime import timedelta
import pandas as pd
from .bet_explorer import BetExplorerScrapperService
from thefuzz import fuzz


class ScrapperService(BetExplorerScrapperService):
    def __init__(
        self,
        start_season,
        end_season,
        nba_seasons
    ):
        # Call the constructors of parent classes explicitly
        BetExplorerScrapperService.__init__(
            self,
            start_season,
            end_season,
        )
        self.nba_seasons = nba_seasons

    def set_fuzz_score(self, home_team, away_team, row):
        home_score = fuzz.ratio(row["home_team"], home_team)
        away_score = fuzz.ratio(row["away_team"], away_team)
        return home_score + away_score

    def match_seasons_data(self):
        for season in self.bet_explorer_seasons.keys():
            columns = [
                "date",
                "home_team",
                "home_score",
                "home_odds",
                "away_team",
                "away_score",
                "away_odds",
            ]
            odds_df = pd.DataFrame(self.bet_explorer_seasons[season], columns=columns)

            self.nba_seasons["home_odds"] = None
            self.nba_seasons["away_odds"] = None

            for i, row in self.nba_seasons.iterrows():
                print(f"{season}/{self.end_season} : {i}/{len(self.nba_seasons)}")

                try:
                    plus_one_day = odds_df["date"] + timedelta(days=1)
                    minus_one_day = odds_df["date"] - timedelta(days=1)
                    same_date_matches = odds_df[
                        (odds_df["date"] == row["GAME_DATE"])
                        | (minus_one_day == row["GAME_DATE"])
                        | (plus_one_day == row["GAME_DATE"])
                    ].reset_index(drop=True)
                    same_date_matches["matchup_score"] = same_date_matches.apply(
                        lambda x: self.set_fuzz_score(
                            row["home_team"], row["away_team"], x
                        ),
                        axis=1,
                    )
                    same_date_matches = same_date_matches.sort_values(
                        by="matchup_score", ascending=False
                    ).reset_index(drop=True)
                    match = same_date_matches.iloc[0]

                    self.nba_seasons.at[i, "home_odds"] = match["home_odds"]
                    self.nba_seasons.at[i, "away_odds"] = match["away_odds"]

                except:
                    continue
