import requests
from bs4 import BeautifulSoup
import pandas

def get_fixture_list(soup):
    fixture_list = []
    all = soup.find_all("div", {"class": "responsive-table"})

    home_games = all[0].find_all("td", {"class": "text-right no-border-rechts no-border-links hauptlink hide-for-small"})
    home_team_list = []
    for index in range(9):
        home_game = home_games[index].find_all("a", attrs={'class': "vereinprofil_tooltip"})
        for tag in home_game:
            home_team_list.append(tag.text.strip())

    away_games = all[0].find_all("td", {"class": "no-border-links no-border-rechts hauptlink hide-for-small"})
    away_team_list = []
    for index in range(9):
        away_game = away_games[index].find_all("a", attrs={"vereinprofil_tooltip"})
        for tag in away_game:
            away_team_list.append(tag.text.strip())

    for home, away in zip(home_team_list, away_team_list):
        fixture_list.append(home + " vs. " + away)

    return fixture_list

def main():
    fixture_data = []
    fixture_url = 'https://www.transfermarkt.com/super-lig/spieltagtabelle/wettbewerb/TR1?saison_id='

    for season in range(2005, 2007):
        print(f"\nAdding Data for Season {season}/{season+1}\n")
        for matchday in range(1, 35):
            season_requests = requests.get(fixture_url + str(season) + '&spieltag=' + str(matchday), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            
            content = season_requests.content
            soup = BeautifulSoup(content, 'html.parser')
            fixture_list = get_fixture_list(soup)

            for game in fixture_list:
                fixture_data.append({'Matches': game})

            print(f"Successfully Added Season {season}/{season+1} Matchday {matchday}")


    df = pandas.DataFrame(fixture_data)
    df.to_csv("TeamData.csv")
        

if __name__ == "__main__":
    main()


# Match, HomeMarketVal, AwayMarketVal, HomePos, AwayPos, HomeAvgAge, AwayAvgAge, HomeNumForeigners, AwayNumForeigners, HomeGoalDiff, AwayGoalDiff
# HomePts, AwayPts, StadiumCap, HomeNumNationalPlayers, AwayNumNationalPlayers, Result