import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
games_txt_path = os.path.join(BASE_DIR, 'collected', settings.GAMES_TXT)

categories = [
    'action',
    'action_fps',

    'rpg',
    'rpg_action',

    'strategy',
    'strategy_real_time',

    'adventure',
    'adventure_rpg',

    'simulation',
    'sports_and_racing',
]

BASE_URL = 'https://store.steampowered.com/category/'
TOP_RATED = '?flavor=contenthub_toprated'

options = webdriver.FirefoxOptions()
options.add_argument('-headless')

driver = webdriver.Firefox(options=options)

app_ids = []

for category in categories:
    url = f"{BASE_URL}{category}/{TOP_RATED}"
    driver.get(url)

    print(f"Waiting for: {url}...", end=" ")

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'salepreviewwidgets_SaleItemBrowserRow_y9MSd')))

    elements = driver.find_elements(By.XPATH, "//div[@class='salepreviewwidgets_StoreSaleWidgetHalfLeft_2Va3O']/a")

    print(f"DONE.\n\tFound {len(elements)} games in {category} category...")

    for element in elements:
        href = element.get_attribute('href')
        app_id = str(href).split('/app/')[1].split('/')[0]
        if app_id not in app_ids:
            app_ids.append(app_id)

app_ids = sorted(map(int, app_ids))

print(f"Writing the app_ids to {games_txt_path}")
with open(games_txt_path, 'w', encoding='utf-8') as file:
    file.write('\n'.join(map(str, app_ids)))

print("Done\nQuiting...")
driver.quit()
