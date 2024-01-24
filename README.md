# Games Recommender
## Project overview
This is the final project of CS114 - Machine Learning @ UIT

In this project, we created a collaborative filtering model based on the matrix factorization model, and a content-based filtering recommender based on the softmax model using the data we collected from Steam.
This project is mostly based on this [course](https://developers.google.com/machine-learning/recommendation/) by Google.

## Collect your own data
### Create a virtual environment
You should run the scripts in a Python virtual environment. Create `venv/` in the project root using:
```bash
python -m venv venv
```
Activate the virtual environment, then run `pip install -r requirements.txt` to install the dependencies.

### Run the scripts
Before doing anything, you should read the [README](https://github.com/maqnitude/games-recommender/blob/master/common/README.md) in `common/`.

First, you will need to scrape the `app_id`s from Steam:
```bash
python -m data.scraper
```
This script will create a text file called `games.txt` (specified in `common/config.py`) containing the scraped `app_id`s.

Then, collect the games data using:
```bash
python -m data.collector collect_games_data
```
And finally, collect the user reviews data with:
```bash
python -m data.collector collect_users_games_data
```
Sorry for the weird name, it will be changed in the future.

After running the scripts, you should see `games.txt`, `games.csv`, and `user_game.csv` located in `data/collected/`.

## Data
The collected data can be found [here](https://drive.google.com/drive/folders/1pAoRBzDp_FkVgdMPweaNPEXSmBU3fmOD?usp=sharing).

**NOTE**: We only collect publicly available data from Steam. Our collected data does not contain any data associated with Steam users, except their `steam_id`.

## Our teams
| ID | Name | Github |
| -- | ---- | ------ |
| 21520411 | Mai Anh Quân | https://github.com/maqnitude |
| 21520456 | Trần Xuân Thành | https://github.com/LukasAbraham |
| 21520531 | Nguyễn Hà Anh Vũ | https://github.com/AnhVu32 |
