import os
import time
from multiprocessing import Lock, Manager, Pool

import requests
import json
import csv

from common import config, utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
games_txt_path = os.path.join(BASE_DIR, 'collected', config.GAMES_TXT)
games_csv_path = os.path.join(BASE_DIR, 'collected', config.GAMES_CSV)
users_games_csv_path = os.path.join(BASE_DIR, 'collected', config.USERS_GAMES_CSV)

GAMES_COLUMNS = [
    # Details
    'app_id',
    'name',
    'required_age',
    'is_free',
    'developers',
    'publishers',
    'platforms_windows',
    'platforms_mac',
    'platforms_linux',
    'metacritic',
    'categories',
    'genres', 
    'recommendations',
    'coming_soon',
    'release_date',

    # Reviews
    'review_score',
    'review_score_desc',
    'total_positive',
    'total_negative',
    'total_reivews',
]

USERS_GAMES_COLUMNS = [
    'recommendation_id',
    'steam_id',
    'app_id',
    'num_games_owned',
    'num_reviews',
    'playtime_forever',
    'playtime_last_two_weeks',
    'playtime_at_review',
    'last_played',
    'timestamp_created',
    'timestamp_updated',
    'voted_up',
    'votes_up',
    'votes_funny',
    'weighted_vote_score',
    'comment_count',
    'steam_purchase',
    'received_for_free',
    'written_during_early_access',
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
    return json.loads(response.text.encode('utf-8-sig'))

def get_app_reviews(app_id, cursor='*'):
    """Get app reviews
    Args:
        app_id (str): The game's id.

    Returns:
        dict: A Python dictionary containing the app reviews 
              retrieved from the API.
    """
    cursor = requests.utils.quote(cursor)
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&cursor={cursor}"
    response = requests.get(url)
    return json.loads(response.text.encode('utf-8-sig'))

def collect_games_data():
    existing_games = set()
    if os.path.exists(games_csv_path):
        with open(games_csv_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader) # Skip the header
            for row in reader:
                existing_games.add(row[0])

    with open(games_csv_path, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if not existing_games:
            writer.writerow(GAMES_COLUMNS)

        with open(games_txt_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                app_id = line.rstrip()
                if app_id in existing_games:
                    print(f"Skipping {app_id}. Data already collected.")
                    continue

                print(f"Retrieving details and reviews for: {app_id}...", end=" ")

                for i in range(5): # Retry up to 5 times
                    try:
                        app_details = get_app_details(app_id)[f"{app_id}"]
                        break
                    except TypeError:
                        print("TYPE_ERROR")
                        print(f"Failed to get app details for {app_id}. Retrying (attempt #{i + 1}) in 5 seconds...")
                        time.sleep(5)
                else:
                    print(f"Failed to get details for {app_id} after 5 attempts")
                    continue

                app_reviews = get_app_reviews(app_id)

                if app_details['success'] == True and app_reviews['success'] == True:
                    name = app_details['data']['name']
                    required_age = app_details['data']['required_age']
                    is_free = app_details['data']['is_free']
                    developers = '|'.join(developer for developer in app_details['data']['developers']) if 'developers' in app_details['data'] else "N/A"
                    publishers = '|'.join(publisher for publisher in app_details['data']['publishers']) if 'publishers' in app_details['data'] else "N/A"
                    platforms_windows = app_details['data']['platforms']['windows']
                    platforms_mac = app_details['data']['platforms']['mac']
                    platforms_linux = app_details['data']['platforms']['linux']
                    metacritic = app_details['data']['metacritic']['score'] if 'metacritic' in app_details['data'] else "N/A"
                    categories = '|'.join(category['description'] for category in app_details['data']['categories']) if 'categories' in app_details['data'] else "N/A"
                    genres = '|'.join(genre['description'] for genre in app_details['data']['genres']) if 'genres' in app_details['data'] else "N/A"
                    recommendations = app_details['data']['recommendations']['total'] if 'recommendations' in app_details['data'] else "N/A"
                    coming_soon = app_details['data']['release_date']['coming_soon']
                    release_date = app_details['data']['release_date']['date']

                    review_score = app_reviews['query_summary']['review_score']
                    review_score_desc = app_reviews['query_summary']['review_score_desc']
                    total_positive = app_reviews['query_summary']['total_positive']
                    total_negative = app_reviews['query_summary']['total_negative']
                    total_reviews = app_reviews['query_summary']['total_reviews']

                    row = [
                        # Details
                        app_id,
                        name,
                        required_age,
                        is_free,
                        developers,
                        publishers,
                        platforms_windows,
                        platforms_mac,
                        platforms_linux,
                        metacritic,
                        categories,
                        genres,
                        recommendations,
                        coming_soon,
                        release_date,

                        # Reviews
                        review_score,
                        review_score_desc,
                        total_positive,
                        total_negative,
                        total_reviews
                    ]

                    writer.writerow(row)

                    print("SUCCESS")
                else:
                    print("FAILURE")

    utils.read_and_sort_csv(games_csv_path, 0, as_number=True)
    print(f"Successfully written to '{games_csv_path}'")

# def process_game_reviews(args):
#     app_id, existing_user_game_pairs, lock = args
#
#     print(f"Retrieving reviews for: {app_id}...", end=" ")
#
#     rows = []
#     cursor = '*'
#     for batch in range(1, 26):
#         attempts = 2
#         for i in range(attempts):
#             try:
#                 with lock:
#                     app_reviews = get_app_reviews(app_id, cursor)
#                 if app_reviews is None:
#                     print(f"Failed to get app reviews for {app_id}. Retrying (attempt #{i + 1}) in 5 seconds...")
#                     time.sleep(5)
#                     continue
#                 break
#             except Exception as e:
#                 print(f"EXCEPTION: {e}")
#                 print(f"Failed to get app reviews for {app_id}. Retrying (attempt #{i + 1}) in 5 seconds...")
#                 time.sleep(5)
#         else:
#             print(f"Failed to get reviews for {app_id} after {attempts} attempts")
#             continue
#
#         if app_reviews['success'] == True:
#             if batch == 1:
#                 print("SUCCESS")
#
#             batch_num_reviews = app_reviews['query_summary']['num_reviews']
#             print(f"Retrieving user data from {batch_num_reviews} reviews for {app_id} (batch: {batch})...", end=" ")
#
#             for review in app_reviews['reviews']:
#                 steam_id = review['author']['steamid']
#                 if (steam_id, app_id) in existing_user_game_pairs:
#                     if review == app_reviews['reviews'][0]:
#                         print("\n", end="")
#                     print(f"Skipping ({steam_id},{app_id}). Data already collected.")
#                     continue
#
#                 num_games_owned = review['author']['num_games_owned'] if 'num_games_owned' in review['author'] else 0
#                 num_reviews = review['author']['num_reviews'] if 'num_reviews' in review['author'] else 0
#                 playtime_forever = review['author']['playtime_forever'] if 'playtime_forever' in review['author'] else 0
#                 playtime_last_two_weeks = review['author']['playtime_last_two_weeks'] if 'playtime_last_two_weeks' in review['author'] else 0
#                 playtime_at_review = review['author']['playtime_at_review'] if 'playtime_at_review' in review['author'] else 0
#                 last_played = review['author']['last_played'] if 'last_played' in review['author'] else 0
#                 timestamp_created = review['timestamp_created']
#                 timestamp_updated = review['timestamp_updated']
#                 voted_up = review['voted_up']
#                 votes_up = review['votes_up']
#                 votes_funny = review['votes_funny']
#                 weighted_vote_score = review['weighted_vote_score']
#                 comment_count = review['comment_count']
#                 steam_purchase = review['steam_purchase']
#                 received_for_free = review['received_for_free']
#                 written_during_early_access = review['written_during_early_access']
#
#                 row = [
#                     steam_id,
#                     app_id,
#                     num_games_owned,
#                     num_reviews,
#                     playtime_forever,
#                     playtime_last_two_weeks,
#                     playtime_at_review,
#                     last_played,
#                     timestamp_created,
#                     timestamp_updated,
#                     voted_up,
#                     votes_up,
#                     votes_funny,
#                     weighted_vote_score,
#                     comment_count,
#                     steam_purchase,
#                     received_for_free,
#                     written_during_early_access,
#                 ]
#
#                 rows.append(row)
#
#             cursor = app_reviews['cursor']
#             if cursor == '*':
#                 print(f"Last batch of reviews for {app_id} reached.")
#                 break
#
#             print("Batch completed.")
#             # print("Batch completed. Waiting 2 seconds before fetching next batch...")
#             # time.sleep(2)
#         else:
#             print("FAILURE")
#
#     with lock:
#         with open(users_games_csv_path, 'a', newline='', encoding='utf-8') as csv_file:
#             writer = csv.writer(csv_file)
#             for row in rows:
#                 if (row[0], row[1]) not in existing_user_game_pairs:
#                     writer.writerow(row)
#                     existing_user_game_pairs.append((row[0], row[1]))
#
# def collect_users_games_data():
#     start_time = time.time();
#
#     existing_user_game_pairs = list()
#     if os.path.exists(users_games_csv_path):
#         with open(users_games_csv_path, 'r', newline='', encoding='utf-8') as csv_file:
#             reader = csv.reader(csv_file)
#             next(reader) # Skip the header
#             for row in reader:
#                 existing_user_game_pairs.append((row[0], row[1]))
#
#     with open(users_games_csv_path, 'a', newline='', encoding='utf-8') as csv_file:
#         writer = csv.writer(csv_file)
#         if not existing_user_game_pairs:
#             writer.writerow(USERS_GAMES_COLUMNS)
#
#     with open(games_txt_path, 'r', encoding='utf-8') as f:
#         app_ids = [line.rstrip() for line in f]
#
#     with Manager() as manager:
#         lock = manager.Lock()
#         # Convert to a Manager list so that it is shared between processes
#         existing_user_game_pairs = manager.list(existing_user_game_pairs)
#         with Pool() as p:
#             p.map(process_game_reviews, [(app_id, existing_user_game_pairs, lock) for app_id in app_ids])
#
#     print("Sorting by steam_id...", end=" ")
#     utils.read_and_sort_csv(users_games_csv_path, 0)
#     print("DONE")
#     print(f"Successfully written to '{users_games_csv_path}'")
#
#     end_time = time.time();
#     execution_time = end_time - start_time
#     print(f"Finished in {execution_time} seconds.")

def collect_users_games_data():
    start_time = time.time()
    
    existing_recommendation_ids = set()
    if os.path.exists(users_games_csv_path):
        with open(users_games_csv_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader) # Skip the header
            for row in reader:
                existing_recommendation_ids.add(row[0])

    with open(users_games_csv_path, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if not existing_recommendation_ids:
            writer.writerow(USERS_GAMES_COLUMNS)

        with open(games_txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                app_id = line.rstrip()

                print(f"Retrieving reviews for: {app_id}...", end=" ")

                cursor = '*'
                cursor_history = []
                for batch in range(1, 26):
                    if cursor in cursor_history:
                        print(f"This batch (cursor={cursor}) was already processed. Skipping to next game.")
                        break

                    attempts = 2
                    delay = 2
                    for i in range(attempts):
                        try:
                            app_reviews = get_app_reviews(app_id, cursor)
                            if app_reviews is None:
                                print(f"Failed to get app reviews for {app_id}. Retrying (attempt #{i + 1}) in {delay} seconds...")
                                time.sleep(delay)
                                continue
                            cursor_history.append(cursor)
                            break
                        except Exception as e:
                            print(f"EXCEPTION: {e}")
                            print(f"Failed to get app reviews for {app_id}. Retrying (attempt #{i + 1}) in {delay} seconds...")
                            time.sleep(delay)
                    else:
                        print(f"Failed to get reviews for {app_id} after {attempts} attempts")
                        continue

                    if app_reviews['success'] == True:
                        if batch == 1:
                            print("SUCCESS")

                        batch_num_reviews = app_reviews['query_summary']['num_reviews']
                        print(f"Retrieving user data from {batch_num_reviews} reviews of {app_id} (batch: {batch})...")

                        for review in app_reviews['reviews']:
                            recommendation_id = review['recommendationid']
                            if recommendation_id in existing_recommendation_ids:
                                print(f"\tSkipping recommendation: {recommendation_id}. Data already collected.")
                                continue

                            steam_id = review['author']['steamid']
                            num_games_owned = review['author']['num_games_owned'] if 'num_games_owned' in review['author'] else 0
                            num_reviews = review['author']['num_reviews'] if 'num_reviews' in review['author'] else 0
                            playtime_forever = review['author']['playtime_forever'] if 'playtime_forever' in review['author'] else 0
                            playtime_last_two_weeks = review['author']['playtime_last_two_weeks'] if 'playtime_last_two_weeks' in review['author'] else 0
                            playtime_at_review = review['author']['playtime_at_review'] if 'playtime_at_review' in review['author'] else 0
                            last_played = review['author']['last_played'] if 'last_played' in review['author'] else 0
                            timestamp_created = review['timestamp_created']
                            timestamp_updated = review['timestamp_updated']
                            voted_up = review['voted_up']
                            votes_up = review['votes_up']
                            votes_funny = review['votes_funny']
                            weighted_vote_score = review['weighted_vote_score']
                            comment_count = review['comment_count']
                            steam_purchase = review['steam_purchase']
                            received_for_free = review['received_for_free']
                            written_during_early_access = review['written_during_early_access']

                            row = [
                                recommendation_id,
                                steam_id,
                                app_id,
                                num_games_owned,
                                num_reviews,
                                playtime_forever,
                                playtime_last_two_weeks,
                                playtime_at_review,
                                last_played,
                                timestamp_created,
                                timestamp_updated,
                                voted_up,
                                votes_up,
                                votes_funny,
                                weighted_vote_score,
                                comment_count,
                                steam_purchase,
                                received_for_free,
                                written_during_early_access,
                            ]

                            writer.writerow(row)
                            existing_recommendation_ids.add(recommendation_id)

                        print("\tBatch completed.")
                        cursor = app_reviews['cursor']
                        if cursor == '*':
                            print(f"\tLast batch of reviews for {app_id} reached.")
                            break
                    else:
                        print("FAILURE")

    print("Sorting by steam_id...", end=" ")
    utils.read_and_sort_csv(users_games_csv_path, 0)
    print("DONE")

    end_time = time.time();
    execution_time = end_time - start_time
    print(f"Finished in {execution_time} seconds.")

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'collect_games_data':
        collect_games_data()
    if sys.argv[1] == 'collect_users_games_data':
        collect_users_games_data()

