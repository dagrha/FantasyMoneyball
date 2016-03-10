import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

class LeagueStandings:
    """ESPN Fantasy Baseball standings aggregator"""
    
    base_url = 'http://games.espn.go.com/flb/standings'

    def __init__(self, leagueId, seasonId):
        """Initializes standings object based on your league ID number and year
        
        Required arguments
        leagueId -- ID of ESPN league, get from standings page url
        seasonId -- Year
        """
        self.league_id = leagueId
        self.season_id = seasonId
        self.league_data = {'leagueId': self.league_id,
                            'seasonId': self.season_id,
                            'view': 'official'}
        self.soup = self.make_soup(LeagueStandings.base_url)
        self.get_standings()
        self.get_stats()
        self.get_title()
        
    def make_soup(self, base_url):
        """Makes HTTP request and creates a BeautifulSoup object"""
        response = requests.post(base_url, params=self.league_data)
        self.url = response.url
        soup = BeautifulSoup(response.content, 'lxml')
        return soup

    def get_standings(self):
        """Gets HTML standings table"""
        self.standings = self.soup.find('table', id='standingsTable')
        
    def get_stats(self):
        """Gets HTML cumulative stats table"""
        self.stats = self.soup.find('table', id='statsTable')
    
    def get_title(self):
        """Retrieves title of the page"""
        title_tag = self.soup.find('title').text
        title_list = string.split(sep='-')
        self.title = title_list[0].strip()
    
    def parse_soup(self, table):
        """Parses soup object to extract relevant data and add it to a list of lists"""
        rows = table.find_all('tr')
        list_of_lists = list()
        time = pd.Timestamp('now')
        for row in rows:
            row_list = list()
            row_list.append(time)
            for td in row.find_all('td')[1:]:
                row_list.append(td.text)
                if td('a'):
                    for a in td('a'):
                        if a.get('href'):
                            m = re.search('teamId\=(\d+)', a.get('href'))
                            if m:
                                row_list.append(m.group(1))
            list_of_lists.append(row_list)
        return [[y for y in x if y] for x in list_of_lists[3:]]
    
    def make_stats_df(self):
        """Creates a pandas dataframe from the HTML stats table"""
        columns = ['DATE', 'TEAM', 'teamId', 'R', 'HR', 'RBI', 'SBN', 'OBP', 
                   'K', 'QS', 'SV', 'ERA', 'WHIP', 'MOVES', 'CHANGE']
        trimmed_table = self.parse_soup(self.stats)
        self.df_stats = pd.DataFrame(trimmed_table, columns=columns)        
        # load season standings csv from file
        try: # if it already exists
            df = pd.read_csv('2016_stats.csv', index_col=0)
        except OSError:
            df = pd.DataFrame(columns=columns) # if it doesn't already exist
        df = df.append(self.df_stats)
        df.to_csv('2016_stats.csv')
        
    def make_standings_df(self):
        """Creates a pandas dataframe from the HTML standings table"""
        columns = ['DATE', 'TEAM', 'teamId', 'R', 'HR', 'RBI', 'SBN', 'OBP', 
                   'K', 'QS', 'SV', 'ERA', 'WHIP', 'POINTS', 'CHANGE']
        trimmed_table = self.parse_soup(self.standings)
        self.df_standings = pd.DataFrame(trimmed_table, columns=columns)       
        # load season standings csv from file
        try: # if it already exists
            df = pd.read_csv('2016_standings.csv', index_col=0)
        except OSError:
            df = pd.DataFrame(columns=columns) # if it doesn't already exist
        df = df.append(self.df_standings)
        df.to_csv('2016_standings.csv')
        
def main():
    league = LeagueStandings('183180', '2016')
    league.make_stats_df()
    league.make_standings_df()
    
if __name__ == "__main__":
    main()