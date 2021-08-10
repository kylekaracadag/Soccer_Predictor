import requests
from bs4 import BeautifulSoup
import pandas

def main():
    games_list = []
    base_url = 'https://www.transfermarkt.com/super-lig/startseite/wettbewerb/TR1/plus/?saison_id='

    for season in range(2020, 2021):
        season_requests = requests.get(base_url + str(season), 
            headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
        content = season_requests.content
        soup = BeautifulSoup(content, 'html.parser')
        print(soup.prettify())
        

if __name__ == "__main__":
    main()