import pandas as pd
from datetime import datetime as dt, timedelta
from selenium.webdriver.common.by import By

from ..mixins import DriverMixin


class BetExplorerScrapperService(DriverMixin):
    def __init__(
        self, start_season, end_season
    ):
        DriverMixin.__init__(
            self,
            start_season=start_season,
            end_season=end_season,
        )

    def transform_odds_date(self, date):
        return dt.strptime(date, "%d.%m.%Y")
    
    def scrape_season(self, season, stage):
        season_games = []

        url = f"https://www.betexplorer.com/basketball/usa/nba-{season}-{season+1}/results/"
        self.driver.get(url)

        try:
            if stage:
                btn = self.driver.find_element(
                    By.XPATH, f"//*[contains(text(), '{stage}')]"
                )
                btn.click()
        except:
            return
        
        self.driver.get(f"{self.driver.current_url}&month=all")

        table = self.driver.find_element(
            By.XPATH, '//*[@id="js-leagueresults-all"]/div/div/table'
        )
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        total_games = 0
        for i, r in enumerate(rows):
            print(f"{season}/{self.end_season} {i}/{len(rows)}")
            if not r.text:
                continue
            tds = r.find_elements(By.XPATH, ".//child::td")
            if len(tds) < 5:
                continue
            matchup, score, home_odds, away_odds, date = [
                t.text for t in tds
            ]

            try:
                if not score:
                    continue
                home_score, away_score = score.split(":")

                if not matchup:
                    continue
                home_team, away_team = matchup.split(" - ")

                if date == "Yesterday":
                    date = dt.now() - timedelta(days=1)
                    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    if not date.split(".")[-1]:
                        date += str(dt.now().year)

                    date = self.transform_odds_date(date)

                match_info = [
                    date,
                    home_team,
                    int(home_score),
                    float(home_odds),
                    away_team,
                    int(away_score),
                    float(away_odds),
                ]
                season_games.append(match_info)
                total_games += 1
            except Exception as e:
                continue

        return season_games


    def bet_explorer_scrapper(self):
        self.bet_explorer_seasons = dict()

        for season in range(self.start_season, self.end_season + 1):
            regular_season = self.scrape_season(season, 'Main')
            playoffs = self.scrape_season(season, 'Play Offs')
            promotion_playoffs = self.scrape_season(season, 'Promotion - Play Offs')

            complete_season_games = []

            if regular_season:
                complete_season_games.extend(regular_season)
            
            if playoffs:
                complete_season_games.extend(playoffs)
            
            if promotion_playoffs:
                complete_season_games.extend(promotion_playoffs)

            columns = [
                "date",
                "home_team",
                "home_score",
                "home_odds",
                "away_team",
                "away_score",
                "away_odds",
            ]
            
            self.bet_explorer_seasons[season] = pd.DataFrame(complete_season_games, columns=columns)

