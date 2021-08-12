import requests
from bs4 import BeautifulSoup
import pandas

def get_fixture_list(soup):
    fixture_list = []
    all = soup.find_all("div", {"class": "responsive-table"})

    # Get the list of home teams for given week
    home_games = all[0].find_all("td", {"class": "text-right no-border-rechts no-border-links hauptlink hide-for-small"})
    home_team_list = []
    for index, _ in enumerate(home_games):
        home_game = home_games[index].find_all("a", attrs={'class': "vereinprofil_tooltip"})
        for tag in home_game:
            home_team_list.append(tag.text.strip())

    # Get the list of away teams for given week
    away_games = all[0].find_all("td", {"class": "no-border-links no-border-rechts hauptlink hide-for-small"})
    away_team_list = []
    for index, _ in enumerate(away_games):
        away_game = away_games[index].find_all("a", attrs={"vereinprofil_tooltip"})
        for tag in away_game:
            away_team_list.append(tag.text.strip())

    # Combine the team names in a string
    for home, away in zip(home_team_list, away_team_list):
        fixture_list.append(f"{home} vs. {away}")

    return fixture_list

def get_league_position(soup):
    home_positions = []
    away_positions = []
    position_list = []
    all = soup.find_all("div", {"class": "responsive-table"})
    league_positions = all[0].find_all("span", {"class": "tabellenplatz"})

    # Gather league positions from the site
    for index, _ in enumerate(league_positions):
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

def get_match_results(soup):
    result_list = []
    all = soup.find_all("div", {"class": "responsive-table"})
    match_results = all[0].find_all("span", {"class": "matchresult finished"})

    # Gather the match scores from the site
    for index, _ in enumerate(match_results):
        result = match_results[index]
        result_text = result.text.strip()
        home_result, away_result = result_text.split(':')
        home_result = int(home_result)
        away_result = int(away_result)
        
        # If home result is equal to the away result we categorize the game 
        # as a draw or 0. If home result is greater than the away result we 
        # categorize the game as a win ir 1. If home result is less than the 
        # away result we categorize the game as a loss ir 2
        if home_result == away_result:
            result_list.append(0)
        elif home_result > away_result:
            result_list.append(1)
        else:
            result_list.append(2)

    return result_list

def main():
    fixture_data = []
    fixture_url = 'https://www.transfermarkt.com/super-lig/spieltagtabelle/wettbewerb/TR1?saison_id='

    for season in range(2005, 2006):
        print(f"\nAdding Data for Season {season}/{season+1}\n")
        for matchday in range(1, 3):
            season_requests = requests.get(fixture_url + str(season) + '&spieltag=' + str(matchday), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            
            content = season_requests.content
            soup = BeautifulSoup(content, 'html.parser')
            fixture_list = get_fixture_list(soup)
            home_positions, away_positions = get_league_position(soup)
            result_list = get_match_results(soup)

            for index, _ in enumerate(fixture_list):
                tmp_dictionary = {}

                # Add the matches to the dictionary
                tmp_dictionary['Matches'] = f"{str(season)[2:]}/{str(season+1)[2:]} - {fixture_list[index]}"

                # Add the home and away positions to the dictionary
                # For the first week set league position values to 0
                if matchday == 1:
                    tmp_dictionary['HomePositions'] = 0
                    tmp_dictionary['AwayPositions'] = 0
                else:
                    tmp_dictionary['HomePositions'] = home_positions[index]
                    tmp_dictionary['AwayPositions'] = away_positions[index]

                # Add the match scores to the dictionary
                tmp_dictionary['Result'] = result_list[index]

                fixture_data.append(tmp_dictionary)

            print(f"Successfully Added Season {season}/{season+1} Matchday {matchday}")


    df = pandas.DataFrame(fixture_data)
    df.to_csv("TeamData.csv")
        

if __name__ == "__main__":
    main()


# [Done] Match
# Link for home team / Link for away team
# HomeMarketVal / AwayMarketVal
# [Done] HomePositions / AwayPositions
# HomeAvgAge / AwayAvgAge
# HomeNumForeigners / AwayNumForeigners
# HomeGoalDiff / AwayGoalDiff
# HomeGoalsScored / AwayGoalsScored
# HomeGoalsConceded / AwayGoalsConceded
# HomePts / AwayPts
# HomeStadiumCap
# HomeNumNationalPlayers / AwayNumNationalPlayers
# [Done] Result

# OPTIONAL
# HomeInjuredMarketVal / AwayInjuredMarketVal
# HomeAvgRating / AwayAvgRating
# HomeInjuredAvgRating / AwayInjuredAvgRating
# HomeWinningStreak / AwayWinningStreak