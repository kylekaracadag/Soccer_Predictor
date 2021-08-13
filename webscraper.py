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

    return home_team_list, away_team_list

def get_fixture_text(home_team_list, away_team_list):
    fixture_list = []

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


def get_score_information(soup):
    table_information = {}
    all = soup.find_all("table")
    table = all[4].find_all("tr")
    table = table[1:]

    for index, _ in enumerate(table):
        score_list = []
        team_name = table[index].find_all("td", {"class": "no-border-links hauptlink"})
        team_name = team_name[0].find_all("a", {"class": "vereinprofil_tooltip"})
        name = team_name[0].text.strip()
        name = name.split('.')[-1].strip()
        
        score_info = table[index].find_all("td", {"class": "zentriert"})[2:]
        for index, _ in enumerate(score_info):
            if score_info[index].text.strip() == '-':
                score_list.append(0)
            else:
                score_list.append(score_info[index].text.strip())
            
        table_information[name] = score_list

    return table_information


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
        # categorize the game as a win or 1. If home result is less than the 
        # away result we categorize the game as a loss or 2
        if home_result == away_result:
            result_list.append(0)
        elif home_result > away_result:
            result_list.append(1)
        else:
            result_list.append(2)

    return result_list

def clean_score_list(score_list):
    table_information = []

    table_information.append(int(score_list[0])) # NumWins
    table_information.append(int(score_list[1])) # NumDraws
    table_information.append(int(score_list[2])) # NumLosses

    goals = score_list[3].split(':')
    table_information.append(int(goals[0])) # GoalsScored
    table_information.append(int(goals[1])) #GoalsConceded

    table_information.append(int(score_list[4])) # GoalAvg
    table_information.append(int(score_list[5])) # Points

    return table_information


def main():
    fixture_data = []
    fixture_url = 'https://www.transfermarkt.com/super-lig/spieltagtabelle/wettbewerb/TR1?saison_id='

    for season in range(2005, 2006):
        print(f"\nAdding Data for Season {season}/{season+1}\n")
        for matchday in range(1, 3):
            season_requests = requests.get(fixture_url + str(season) + '&spieltag=' + str(matchday), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            prev_season_requests = requests.get(fixture_url + str(season) + '&spieltag=' + str(matchday-1), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            
            content = season_requests.content
            soup = BeautifulSoup(content, 'html.parser')
            prev_content = prev_season_requests.content
            prev_soup = BeautifulSoup(prev_content, 'html.parser')

            home_team_list, away_team_list = get_fixture_list(soup)
            fixture_list = get_fixture_text(home_team_list, away_team_list)
            home_positions, away_positions = get_league_position(soup)
            result_list = get_match_results(soup)
            score_info = {}
            if matchday != 1:
                score_info = get_score_information(prev_soup)

            for index, _ in enumerate(fixture_list):
                tmp_dictionary = {}

                # Add the match day to the dictionary
                tmp_dictionary['Matchday'] = matchday
                
                # Add the matches to the dictionary
                tmp_dictionary['Matches'] = f"{str(season)[2:]}/{str(season+1)[2:]} - {fixture_list[index]}"

                # Add the home and away positions to the dictionary
                # For the first week set league position values to 0
                if matchday == 1:
                    tmp_dictionary['HomePositions'] = 0
                    tmp_dictionary['AwayPositions'] = 0
                    tmp_dictionary['HomeWins'] = 0
                    tmp_dictionary['AwayWins'] = 0
                    tmp_dictionary['HomeDraws'] = 0
                    tmp_dictionary['AwayDraws'] = 0
                    tmp_dictionary['HomeLosses'] = 0
                    tmp_dictionary['AwayLosses'] = 0
                    tmp_dictionary['HomeGoalsScored'] = 0
                    tmp_dictionary['AwayGoalsScored'] = 0
                    tmp_dictionary['HomeGoalsConceded'] = 0
                    tmp_dictionary['AwayGoalsConceded'] = 0
                    tmp_dictionary['HomeGoalDiff'] = 0
                    tmp_dictionary['AwayGoalDiff'] = 0
                    tmp_dictionary['HomePoints'] = 0
                    tmp_dictionary['AwayPoints'] = 0
                else:
                    home_team_name = home_team_list[index]
                    away_team_name = away_team_list[index]
                    home_score_list = []
                    away_score_list = []
                    for key in score_info:
                        if key in home_team_name:
                            home_score_list = clean_score_list(score_info[key])
                        if key in away_team_name:
                            away_score_list = clean_score_list(score_info[key])

                    tmp_dictionary['HomePositions'] = home_positions[index]
                    tmp_dictionary['AwayPositions'] = away_positions[index]
                    tmp_dictionary['HomeWins'] = home_score_list[0]
                    tmp_dictionary['AwayWins'] = away_score_list[0]
                    tmp_dictionary['HomeDraws'] = home_score_list[1]
                    tmp_dictionary['AwayDraws'] = away_score_list[1]
                    tmp_dictionary['HomeLosses'] = home_score_list[2]
                    tmp_dictionary['AwayLosses'] = away_score_list[2]
                    tmp_dictionary['HomeGoalsScored'] = home_score_list[3]
                    tmp_dictionary['AwayGoalsScored'] = away_score_list[3]
                    tmp_dictionary['HomeGoalsConceded'] = home_score_list[4]
                    tmp_dictionary['AwayGoalsConceded'] = away_score_list[4]
                    tmp_dictionary['HomeGoalDiff'] = home_score_list[5]
                    tmp_dictionary['AwayGoalDiff'] = away_score_list[5]
                    tmp_dictionary['HomePoints'] = home_score_list[6]
                    tmp_dictionary['AwayPoints'] = away_score_list[6]



                # Add the match scores to the dictionary
                tmp_dictionary['Result'] = result_list[index]

                fixture_data.append(tmp_dictionary)

            print(f"Successfully Added Season {season}/{season+1} Matchday {matchday}")


    df = pandas.DataFrame(fixture_data)
    df.to_csv("TeamData.csv")
        

if __name__ == "__main__":
    main()


# [Done] Match
# Matchday
# [Done] HomeWins / AwayWins
# [Done] HomeDraws / AwayDraws
# [Done] HomeLosses / AwayLosses
# [Done] HomeGoalsScored / AwayGoalsScored
# [Done] HomeGoalsConceded / AwayGoalsConceded
# [Done] HomeGoalDiff / AwayGoalDiff
# [Done] HomePoints / AwayPoints

# Link for home team / Link for away team
# HomeMarketVal / AwayMarketVal
# [Done] HomePositions / AwayPositions
# HomeAvgAge / AwayAvgAge
# HomeNumForeigners / AwayNumForeigners
# HomeStadiumCap
# HomeNumNationalPlayers / AwayNumNationalPlayers
# [Done] Result

# OPTIONAL
# HomeInjuredMarketVal / AwayInjuredMarketVal
# HomeAvgRating / AwayAvgRating
# HomeInjuredAvgRating / AwayInjuredAvgRating
# HomeWinningStreak / AwayWinningStreak