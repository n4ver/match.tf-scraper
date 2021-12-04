import requests
import re
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup


TOURNAMENT_NAME = ""


def scrape_tournament_page(URL):
    global TOURNAMENT_NAME
    team_pages = []
    disband = "Disbanded"
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all("tr")
    TOURNAMENT_NAME = soup.title.text.split("-")[0].strip("\n")
    print(TOURNAMENT_NAME + "\n")
    
    for tr in results:
        tds = tr.find_all("td", class_=None)
        if tds and not re.search(disband, str(tds[0])):
            team_pages += [tds[0].contents[0].attrs['href']]
            print(tds[0].text)

    return team_pages


def command_generator(list_of_players):
    with open("cast_aliases.cfg", "w+", encoding="utf-8") as f:
        for playerdata in list_of_players:
            try:
                f.write(f'ce_playeraliases_add {playerdata[1]} "{playerdata[0]}"\n')
            except UnicodeEncodeError as e:
                print(e)
                print(playerdata)


def write_to_json(list_of_players, filename):
    new_dict = {}
    list_of_players = [(i, j) for j, i in list_of_players]
    for player in list_of_players:
        name = player[1]
        steamid = player[0]
        new_dict[f"[{steamid}]"] = name

    with open(filename, "w+") as f:
        json.dump(new_dict, f)


def scrape_team_page(URL):
    global TOURNAMENT_NAME
    print(f"PARSING {URL}")
    player_list = []
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="panel-heading")
    for header in results:
        if re.search(TOURNAMENT_NAME, header.text):
            active_roster = header.find_next_sibling("ul")
            break

    player_details = active_roster.find_all('div', 'user-details')
    for player in player_details:
        player_info = player.text.replace("captain", "PLACEHOLDER").replace("\n", "PLACEHOLDER")
        player_list += [tuple([i for i in player_info.split("PLACEHOLDER") if i])]
        
    return player_list


def main():
    URL = input("Enter match.tf tournament URL:")
    BASE_URL = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(URL))
    team_pages = scrape_tournament_page(URL)
    list_of_players = []
    
    for team in team_pages:
        list_of_players += scrape_team_page(BASE_URL + team)

    command_generator(list_of_players)
    write_to_json(list_of_players, "real_aliases.json")
    

if __name__ == "__main__":
    main()
