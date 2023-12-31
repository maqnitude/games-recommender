import os

import requests
import json
import csv

from common import config, utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
games_txt_path = os.path.join(BASE_DIR, 'collected', config.GAMES_TXT)
games_csv_path = os.path.join(BASE_DIR, 'collected', config.GAMES_CSV)
users_games_csv_path = os.path.join(BASE_DIR, 'collected', config.USERS_GAMES_CSV)

GAMES_COLUMNS = [
    'app_id', 'name', 'required_age', 'is_free',
    'categories', 'genres',
    'short_description',
    'developers', 'publishers',
    'release_date',
    'metacritic_score',
    'review_score', 'review_score_desc', 'total_positive', 'total_negative', 'total_reivews',
]

USERS_GAMES_COLUMNS = [
    'steam_id', 'app_id',
    'voted_up', 'votes_up', 'votes_funny',
    'playtime_forever', 'playtime_last_two_weeks', 'playtime_at_review',
    'timestamp_created', 'timestamp_updated'
]

# USERS RELATED APIs

def resolve_vanity_url(vanity_url):
    """Get steam_id from accounts with custom url

    Args:

    Returns:

    """

    url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={config.STEAM_API_KEY}&vanityurl={vanity_url}"
    response = requests.get(url)
    return json.loads(response.text)


def get_player_summaries(steam_id):
    """Get player summaries from steam_id
    
    Args:

    Returns:

    """

    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={config.STEAM_API_KEY}&steamids={steam_id}"
    response = requests.get(url)
    return json.loads(response.text)

def get_recently_played_games(steam_id):
    url = f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key={config.STEAM_API_KEY}&steamid={steam_id}"
    response = requests.get(url)
    return json.loads(response.text)

# GAMES (APPS) RELATED APIs

def get_app_details(app_id):
    """Get app details in English.

    Args:
        app_id (str): The game's id.

    Returns:
        dict: A Python dictionary containing the app details
              retrieved from the API.
    """

    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&lang=en"
    response = requests.get(url)
    return json.loads(response.text)

def get_app_reviews(app_id):
    """Get app reviews

    Args:
        app_id (str): The game's id.

    Returns:
        dict: A Python dictionary containing the app reviews 
              retrieved from the API.
    """

    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    response = requests.get(url)
    return json.loads(response.text)

def collect_games_data():
    with open(games_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(GAMES_COLUMNS)

        with open(games_txt_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                app_id = line.rstrip()

                print(f"Retrieving details and reviews for: {app_id}...", end=" ")

                app_details = get_app_details(app_id)[f"{app_id}"]
                app_reviews = get_app_reviews(app_id)

                if app_details['success'] == True and app_reviews['success'] == True:
                    name = app_details['data']['name']
                    required_age = app_details['data']['required_age']
                    is_free = app_details['data']['is_free']
                    categories = '|'.join(category['description'] for category in app_details['data']['categories'])
                    genres = '|'.join(genre['description'] for genre in app_details['data']['genres'])
                    short_description = app_details['data']['short_description']
                    developers = '|'.join(developer for developer in app_details['data']['developers'])
                    publishers = '|'.join(publisher for publisher in app_details['data']['publishers'])
                    release_date = app_details['data']['release_date']['date']
                    metacritic_score = app_details['data']['metacritic']['score'] if 'metacritic' in app_details['data'] else 'N/A'

                    review_score = app_reviews['query_summary']['review_score']
                    review_score_desc = app_reviews['query_summary']['review_score_desc']
                    total_positive = app_reviews['query_summary']['total_positive']
                    total_negative = app_reviews['query_summary']['total_negative']
                    total_reviews = app_reviews['query_summary']['total_reviews']

                    row = [
                        app_id, name, required_age, is_free,
                        categories, genres,
                        short_description,
                        developers, publishers,
                        release_date,
                        metacritic_score,
                        review_score, review_score_desc, total_positive, total_negative, total_reviews
                    ]

                    writer.writerow(row)

                    print("SUCCESS")
                else:
                    print("FAILURE")

    print(f"Successfully written to '{games_csv_path}'")

def collect_users_games_data():
    with open(users_games_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(USERS_GAMES_COLUMNS)

        with open(games_txt_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                app_id = line.rstrip()

                print(f"Retrieving reviews for: {app_id}...", end=" ")

                app_reviews = get_app_reviews(app_id)

                if app_reviews['success'] == True:
                    print("SUCCESS")
                    print(f"Retrieving user data from reviews of {app_id}...", end=" ")

                    for review in app_reviews['reviews']:
                        steam_id = review['author']['steamid']
                        voted_up = review['voted_up']
                        votes_up = review['votes_up']
                        votes_funny = review['votes_funny']
                        playtime_forever = review['author']['playtime_forever']
                        playtime_last_two_weeks = review['author']['playtime_last_two_weeks']
                        playtime_at_review = review['author']['playtime_at_review']
                        timestamp_created = review['timestamp_created']
                        timestamp_updated = review['timestamp_updated']

                        row = [
                            steam_id, app_id,
                            voted_up, votes_up, votes_funny,
                            playtime_forever, playtime_last_two_weeks, playtime_at_review,
                            timestamp_created, timestamp_updated
                        ]

                        writer.writerow(row)

                    print("DONE")
                else:
                    print("FAILURE")

    print("Sorting by steam_id...", end=" ")
    utils.read_and_sort_csv(users_games_csv_path, 0)
    print("DONE")

    print(f"Successfully written to '{users_games_csv_path}'")

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'collect_games_data':
        collect_games_data()
    if sys.argv[1] == 'collect_users_games_data':
        collect_users_games_data()

