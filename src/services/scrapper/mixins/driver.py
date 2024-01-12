import undetected_chromedriver as uc

class DriverMixin:
    def __init__(self, start_season, end_season):
        self.start_season = start_season
        self.end_season = end_season
        self.driver = None

    def start_driver(self):
        options = uc.ChromeOptions()
        options.headless = True
        self.driver = uc.Chrome(options=options)

    def close_driver(self):
        self.driver.close()