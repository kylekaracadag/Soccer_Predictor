import requests
from bs4 import BeautifulSoup
import pandas

def get_fixture_list(soup):
    fixture_list = []
    all = soup.find_all("div", {"class": "responsive-table"})

    # Get the list of home teams for given week
    home_games = all[0].find_all("td", {"class": "text-right no-border-rechts no-border-links hauptlink hide-for-small"})
    home_team_list = []
    for index in range(9):
        home_game = home_games[index].find_all("a", attrs={'class': "vereinprofil_tooltip"})
        for tag in home_game:
            home_team_list.append(tag.text.strip())

    # Get the list of away teams for given week
    away_games = all[0].find_all("td", {"class": "no-border-links no-border-rechts hauptlink hide-for-small"})
    away_team_list = []
    for index in range(9):
        away_game = away_games[index].find_all("a", attrs={"vereinprofil_tooltip"})
        for tag in away_game:
            away_team_list.append(tag.text.strip())

    # Combine the team names in a string
    for home, away in zip(home_team_list, away_team_list):
        fixture_list.append(home + " vs. " + away)

    return fixture_list

def get_league_position(soup):
    home_positions = []
    away_positions = []
    position_list = []
    all = soup.find_all("div", {"class": "responsive-table"})
    league_positions = all[0].find_all("span", {"class": "tabellenplatz"})

    # Gather league positions from the site
    for index in range(36):
        pos = league_positions[index]
        pos_num = int(''.join(x for x in pos.text.strip() if x.isdigit()))
        position_list.append(pos_num)
        
    # Clean the position list
    league_position_list = []
    [league_position_list.append(x) for x in position_list if x not in league_position_list]

    # Divide the home team positions and the away team positions
    home_positions = league_position_list[::2]
    away_positions = league_position_list[1::2]

    return home_positions, away_positions

def main():
    fixture_data = []
    fixture_url = 'https://www.transfermarkt.com/super-lig/spieltagtabelle/wettbewerb/TR1?saison_id='

    for season in range(2005, 2006):
        print(f"\nAdding Data for Season {season}/{season+1}\n")
        for matchday in range(1, 2):
            season_requests = requests.get(fixture_url + str(season) + '&spieltag=' + str(matchday), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            
            content = season_requests.content
            soup = BeautifulSoup(content, 'html.parser')
            fixture_list = get_fixture_list(soup)

            for game in fixture_list:
                fixture_data.append({'Matches': game})

            home_positions, away_positions = get_league_position(soup)
            for home_pos in home_positions:
                fixture_data.append({'HomePositions': int(home_pos)})
            for away_pos in away_positions:
                fixture_data.append({'AwayPositions': int(away_pos)})

            print(f"Successfully Added Season {season}/{season+1} Matchday {matchday}")


    df = pandas.DataFrame(fixture_data)
    df.to_csv("TeamData.csv")
        

if __name__ == "__main__":
    main()


# X Match
# Link for home team / Link for away team
# HomeMarketVal / AwayMarketVal
# HomePositions / AwayPositions
# HomeAvgAge / AwayAvgAge
# HomeNumForeigners / AwayNumForeigners
# HomeGoalDiff / AwayGoalDiff
# HomePts / AwayPts
# StadiumCap
# HomeNumNationalPlayers / AwayNumNationalPlayers
# Result