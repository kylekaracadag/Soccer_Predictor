import requests
from bs4 import BeautifulSoup
import pandas
import re


def get_fixture_list(soup):
    """Get the list of every fixture in given week

    This function returns the name of the home and away team
    for the games being played in a given week.

    Args:
        soup: The parsed HTML data that we got from BeautifulSoup 
        on the link for the given week's fixture page on transfermarkt

    Returns:
        The first list inclduing the name of all of the home teams
        for the current week and the name of all the away teams for
        the same week
    """

    fixture_list = []
    all = soup.find_all("div", {"class": "responsive-table"})

    # Get the list of home teams for given week
    home_games = all[0].find_all("td", 
        {"class": "text-right no-border-rechts no-border-links hauptlink hide-for-small"})
    home_team_list = []
    for index, _ in enumerate(home_games):
        home_game = home_games[index].find_all("a", 
            attrs={'class': "vereinprofil_tooltip"})
        for tag in home_game:
            home_team_list.append(tag.text.strip())

    # Get the list of away teams for given week
    away_games = all[0].find_all("td", 
        {"class": "no-border-links no-border-rechts hauptlink hide-for-small"})
    away_team_list = []
    for index, _ in enumerate(away_games):
        away_game = away_games[index].find_all("a", 
            attrs={"vereinprofil_tooltip"})
        for tag in away_game:
            away_team_list.append(tag.text.strip())

    # Combine the team names in a string
    for home, away in zip(home_team_list, away_team_list):
        fixture_list.append(f"{home} vs. {away}")

    return home_team_list, away_team_list


def get_fixture_text(home_team_list, away_team_list):
    """Convert the fixture list into readable text

    Args:
        home_team_list: The list of home teams playing for the current week

        away_team_list: The list of away teams playing for the current week

    Returns:
        Combined name of the home team and away team for each game in the week
    """

    fixture_list = []

    for home, away in zip(home_team_list, away_team_list):
        fixture_list.append(f"{home} vs. {away}")

    return fixture_list


def get_league_position(soup):
    """Get the league position of each team in the current week

    Args:
        soup: The parsed HTML data that we got from BeautifulSoup 
        on the link for the given week's fixture page on transfermarkt

    Returns:
        The first list inclduing the league position of all of the home teams
        for the current week and the league position of all the away teams for
        the same week
    """

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
    [league_position_list.append(x) \
        for x in position_list if x not in league_position_list]

    # Divide the home team positions and the away team positions
    home_positions = league_position_list[::2]
    away_positions = league_position_list[1::2]

    return home_positions, away_positions


def get_score_information(soup):
    """Get the score information of each team in the current week

    This function returns the name of each team playing in the current
    week and their current number of wins, draws, losses, goals scored,
    goals conceded, goal average, and their current points. 

    Args:
        soup: The parsed HTML data that we got from BeautifulSoup 
        on the link for the given week's fixture page on transfermarkt

    Returns:
        A dictionary that has the team name as the key and a list of all
        the information listed above as the value
    """

    table_information = {}
    all = soup.find_all("table")
    table = all[4].find_all("tr")
    table = table[1:]

    # Iterate over all the teams in the league standings table
    for index, _ in enumerate(table):
        score_list = []
        team_name = table[index].find_all("td", 
            {"class": "no-border-links hauptlink"})
        team_name = team_name[0].find_all("a", 
            {"class": "vereinprofil_tooltip"})

        # Since the websites stores different names on the board and fixture
        # list we trim down the name of the team to only include the main name
        name = team_name[0].text.strip()
        name = name.split('.')[-1].strip()
        name = name.split(' ')
        if len(name) > 1:
            if len(name[0]) > len(name[1]):
                name = name[0]
            else:
                name = name[1]
        else:
            name = name[0]
    #     print(f"Name: {name}")

        score_info = table[index].find_all("td", {"class": "zentriert"})[2:]
        for index, _ in enumerate(score_info):
            if score_info[index].text.strip() == '-':
                score_list.append(0)
            else:
                score_list.append(score_info[index].text.strip())

        table_information[name] = score_list

    return table_information


def get_club_data(soup):
    """Get the club data of each team

    This function returns the name of each team in the current season
    and returns a dictionary with their squad size, average age, number
    of foreigners, average market value, and the total market 
    value (in thousands)

    Args:
        soup: The parsed HTML data that we got from BeautifulSoup 
        on the link for the given season's club table page on transfermarkt

    Returns:
        A dictionary that has the team name as the key and a list of all
        the information listed above as the value
    """

    all = soup.find_all("table", {"class": "items"})
    table_all = all[0].find_all("tbody")
    teams = table_all[0].find_all("td", {"class": "hauptlink no-border-links show-for-small show-for-pad"})

    # Get the names of all the teams and add to dictionary
    team_names = {}
    for index, _ in enumerate(teams):
        name = teams[index].text.strip()
        name = name.split('.')
        name = name[-1].strip()
        name = name.split(' ')
        if len(name) > 1:
            if len(name[0]) > len(name[1]):
                name = name[0]
            else:
                name = name[1]
        else:
            name = name[0]
        team_names[name.strip()] = []

    team_info_list = []
    odd_team_info = []
    even_team_info = []
    odd_teams = table_all[0].find_all("tr", {"class": "odd"})
    even_teams = table_all[0].find_all("tr", {"class": "even"})

    # Get the squad size, average age, and number of foreigners for each club
    for index, _ in enumerate(odd_teams):
        curr_team = odd_teams[index]

        # Get squad size, average age, and number of foreigners
        squad_info = odd_teams[index].find_all("td", {"class": "zentriert"})
        tmp_list = []
        tmp_list.append(int(squad_info[1].text.strip())) # Squad Size
        tmp_list.append(float(squad_info[2].text.strip())) # Average Age
        tmp_list.append(int(squad_info[3].text.strip())) # Number of Foreigners
        odd_team_info.append(tmp_list)

    for index, _ in enumerate(even_teams):
        curr_team = even_teams[index]

        # Get squad size, average age, and number of foreigners
        squad_info = even_teams[index].find_all("td", {"class": "zentriert"})
        tmp_list = []
        tmp_list.append(int(squad_info[1].text.strip())) # Squad Size
        tmp_list.append(float(squad_info[2].text.strip())) # Average Age
        tmp_list.append(int(squad_info[3].text.strip())) # Number of Foreigners
        even_team_info.append(tmp_list)

    for odd, even in zip(odd_team_info, even_team_info):
        team_info_list.append(odd)
        team_info_list.append(even)

    if len(odd_team_info) > len(even_team_info):
        team_info_list.append(odd_team_info[-1])

    market_values = table_all[0].find_all("td", {"class": "rechts hide-for-small hide-for-pad"})
    avg_market_val_list = market_values[::2]
    total_market_val_list = market_values[1::2]
    market_val_list = []

    # Get the average and total market value for each team
    index = 0
    for avg, total in zip(avg_market_val_list, total_market_val_list):
        avg_million = False
        total_million = False
        if 'm' in avg.text:
            avg_million = True
        if 'm' in total.text:
            total_million = True

        if avg_million:
            avg_num = round(float(re.findall("\d+\.\d+", avg.text)[0])*1000)
        else:
            avg_num = round(float(re.findall(r'\d+', avg.text)[0]))

        if total_million:
            total_num = round(float(re.findall("\d+\.\d+", total.text)[0])*1000)
        else:
            total_num = round(float(re.findall(r'\d+', avg.text)[0]))

        team_info_list[index].append(avg_num)
        team_info_list[index].append(total_num)
        index += 1

    index = 0
    for key in team_names:
        team_names[key] = team_info_list[index]
        index += 1

    return team_names


def get_match_results(soup):
    """Get the match results of each fixture in the current week

    This functions returns the result of each fixture: 
        0 if the game ends in a draw
        1 if the home team wins the game and away team loses
        2 if the away team wins the game and home team loses

    Args:
        soup: The parsed HTML data that we got from BeautifulSoup 
        on the link for the given week's fixture page on transfermarkt

    Returns:
        A list with the result of each game based on the numbering
        mentioned above
    """
    
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
    """Clean up the list with score information

    This function converts all the values from score list that we
    got from the get_score_information function into an integer

    Args:
        score_list: score_list that the get_score_information function returned

    Returns:
        The same list as the score_list but all the values are converted to int
    """

    table_information = []

    table_information.append(int(score_list[0])) # NumWins
    table_information.append(int(score_list[1])) # NumDraws
    table_information.append(int(score_list[2])) # NumLosses

    if isinstance(score_list[3], str):
        goals = score_list[3].split(':')
        table_information.append(int(goals[0])) # GoalsScored
        table_information.append(int(goals[1])) #GoalsConceded
    else:
        table_information.append(0) # GoalsScored
        table_information.append(0) #GoalsConceded

    table_information.append(int(score_list[4])) # GoalAvg
    table_information.append(int(score_list[5])) # Points

    return table_information


def main():
    fixture_data = []
    fixture_url = 'https://www.transfermarkt.com/super-lig/spieltagtabelle/wettbewerb/TR1?saison_id='
    club_table_url = 'https://www.transfermarkt.com/super-lig/startseite/wettbewerb/TR1/saison_id/'

    for season in range(2005, 2021):
        print(f"\nAdding Data for Season {season}/{season+1}\n")
        upper_matchday = 35
        if season == 2020:
            upper_matchday = 43

        for matchday in range(1, upper_matchday):
            season_requests = requests.get(
                fixture_url + str(season) + '&spieltag=' + str(matchday), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            prev_season_requests = requests.get(
                fixture_url + str(season) + '&spieltag=' + str(matchday-1), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            clubs_requests = requests.get(
                club_table_url + str(season), 
                headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
            
            content = season_requests.content
            soup = BeautifulSoup(content, 'html.parser')

            prev_content = prev_season_requests.content
            prev_soup = BeautifulSoup(prev_content, 'html.parser')

            club_content = clubs_requests.content
            club_soup = BeautifulSoup(club_content, 'html.parser')

            home_team_list, away_team_list = get_fixture_list(soup)
            fixture_list = get_fixture_text(home_team_list, away_team_list)
            home_positions, away_positions = get_league_position(soup)
            result_list = get_match_results(soup)
            club_data = get_club_data(club_soup)

            score_info = {}
            if matchday != 1:
                score_info = get_score_information(prev_soup)

            for index, _ in enumerate(fixture_list):
                tmp_dictionary = {}

                # Add the match day to the dictionary
                tmp_dictionary['Matchday'] = matchday
                
                # Add the matches to the dictionary
                m = f"{str(season)[2:]}/{str(season+1)[2:]} - {fixture_list[index]}"
                tmp_dictionary['Matches'] = m

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

                # Add the club table information to the dictionary
                home_team_name = home_team_list[index]
                away_team_name = away_team_list[index]
                home_table_list = []
                away_table_list = []
                for key in club_data:
                    if key in home_team_name:
                        home_table_list = club_data[key]
                    if key in away_team_name:
                        away_table_list = club_data[key]

                tmp_dictionary['HomeSquadSize'] = home_table_list[0]
                tmp_dictionary['AwaySquadSize'] = away_table_list[0]
                tmp_dictionary['HomeAvgAge'] = home_table_list[1]
                tmp_dictionary['AwayAvgAge'] = away_table_list[1]
                tmp_dictionary['HomeNumForeigners'] = home_table_list[2]
                tmp_dictionary['AwayNumForeigners'] = away_table_list[2]
                tmp_dictionary['HomeAvgMarketVal'] = home_table_list[3]
                tmp_dictionary['AwayAvgMarketVal'] = away_table_list[3]
                tmp_dictionary['HomeMarketVal'] = home_table_list[4]
                tmp_dictionary['AwayMarketVal'] = away_table_list[4]
                
                # Add the match scores to the dictionary
                if len(result_list) < 9 and index == 8:
                    tmp_dictionary['Result'] = 0
                else:
                    tmp_dictionary['Result'] = result_list[index]

                fixture_data.append(tmp_dictionary)

            print(f"Successfully Added Season {season}/{season+1} Matchday {matchday}")

    # Convert the data into a csv file
    df = pandas.DataFrame(fixture_data)
    df.to_csv("TeamData.csv")
        

if __name__ == "__main__":
    main()


# [Done] Matchday
# [Done] Matches
# [Done] HomePositions / AwayPositions
# [Done] HomeWins / AwayWins
# [Done] HomeDraws / AwayDraws
# [Done] HomeLosses / AwayLosses
# [Done] HomeGoalsScored / AwayGoalsScored
# [Done] HomeGoalsConceded / AwayGoalsConceded
# [Done] HomeGoalDiff / AwayGoalDiff
# [Done] HomePoints / AwayPoints
# [Done] HomeSquadSize / AwaySquadSize
# [Done] HomeAvgAge / AwayAvgAge
# [Done] HomeNumForeigners / AwayNumForeigners
# [Done] HomeAvgMarketVal / AwayAvgMarketVal
# [Done] HomeMarketVal / AwayMarketVal
# [Done] Result
