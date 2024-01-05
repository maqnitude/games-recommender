import os
import requests
import json
from urllib.parse import urlparse
from urllib.error import URLError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from common import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
games_txt_path = os.path.join(BASE_DIR, 'collected', config.GAMES_TXT)

categories = [
    'action',
    'arcade_rhythm',
    'fighting_martial_arts',
    'action_fps',
    'hack_and_slash',
    'action_run_jump',
    'action_tps',
    'shmup',

    'rpg',
    'rpg_action',
    'rpg_jrpg',
    'rpg_party_based',
    'rogue_like_rogue_lite',
    'rpg_turn_based',

    'strategy',
    'strategy_card_board',
    'strategy_cities_settlements',
    'strategy_grand_4x',
    'strategy_military',
    'strategy_real_time',
    'tower_defense',
    'strategy_turn_based',

    'adventure',
    'adventure_rpg',
    'casual',
    'hidden_object',
    'metroidvania',
    'puzzle_matching',
    'story_rich',
    'visual_novel',

    'simulation',
    'sim_building_automation',
    'sim_dating',
    'sim_farming_crafting',
    'sim_hobby_sim',
    'sim_life',
    'sim_physics_sandbox',
    'sim_space_flight',

    'sports_and_racing',
    'sports',
    'sports_fishing_hunting',
    'sports_individual',
    'racing',
    'racing_sim',
    'sports_sim',
    'sports_team',
]

BASE_URL = 'https://store.steampowered.com/category/'
TOP_RATED = '?flavor=contenthub_toprated'

options = webdriver.FirefoxOptions()
options.add_argument('-headless')

driver = webdriver.Firefox(options=options)

app_ids = []

def is_url_valid(url):
    """Checks if a URL is valid by parsing it and handling potential errors."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])  # Ensure basic parts are present
    except URLError as e:
        print(f"Invalid URL: {url}. Error: {e}")
        return False

def get_app_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&lang=en"
    response = requests.get(url)
    return json.loads(response.text)

for category in categories:
    for offset in range(10):
        url = f"{BASE_URL}{category}/{TOP_RATED}&offset={offset * 12}"

        if is_url_valid(url):
            try:
                driver.get(url)

                print(f"Waiting for: {url}...", end=" ")

                wait = WebDriverWait(driver, 20)
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'salepreviewwidgets_SaleItemBrowserRow_y9MSd')))
                elements = driver.find_elements(By.XPATH, "//div[@class='salepreviewwidgets_StoreSaleWidgetHalfLeft_2Va3O']/a")

                print(f"DONE.\n\tFound {len(elements)} games in {category} category...")

                for element in elements:
                    href = element.get_attribute('href')
                    app_id = str(href).split('/app/')[1].split('/')[0]
                    app_type = get_app_details(app_id)[f"{app_id}"]['data']['type']
                    if app_id not in app_ids and app_type == "game":
                        app_ids.append(app_id)
            except Exception as e:
                print(f"EXCEPTION: {e}\n\tTrackback: {e.__traceback__}")
        else:
            print(f"Skipping invalid URL: {url}")

app_ids = sorted(map(int, app_ids))

print(f"Writing the app_ids to {games_txt_path}")
with open(games_txt_path, 'w', encoding='utf-8') as file:
    file.write('\n'.join(map(str, app_ids)))

print("Done\nQuiting...")
driver.quit()
