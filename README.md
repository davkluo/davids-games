# David's Games
Game vault site with leaderboards, personal achievements, and gameplay stats

## Table of Contents

- [To-Do](#to-do)
- [Tech Stack](#tech-stack)
- [Screenshots](#screenshots)
- [Setup](#setup)
- [Running the App](#running-the-app)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API](#api)

## To-Do

- Add more tests
- Add more games
- Add more achievements to existing games

## Tech Stack
Built with Flask, Jinja, and PostgreSQL

## Screenshots

<img width="1432" alt="Screen Shot 2023-03-20 at 10 49 11 AM" src="https://user-images.githubusercontent.com/108588437/226425675-45e55f7b-42a8-4bad-93cc-bddf5c62b7da.png">

<img width="1430" alt="Screen Shot 2023-03-20 at 10 49 32 AM" src="https://user-images.githubusercontent.com/108588437/226425773-134a6e8c-3431-45e7-9549-6675db037ddc.png">

<img width="1428" alt="Screen Shot 2023-03-20 at 10 49 59 AM" src="https://user-images.githubusercontent.com/108588437/226425933-efc3c931-e6ff-4cf9-83f0-e1d84ef9b64e.png">

<img width="1429" alt="Screen Shot 2023-03-20 at 10 51 25 AM" src="https://user-images.githubusercontent.com/108588437/226426060-42451d11-be40-4585-bff4-a72241c9f6b0.png">

## Setup

### Clone the repo

```bash
git clone git@github.com:davkluo/davids-games.git
cd davids-games
```

### Set environment variables

```bash
cp .env.example .env
# open .env and modify the secret key environment variable
```

### Create virtual env

```bash
python3 -m venv venv
```

### Activate virtual env

```bash
source venv/bin/activate
```

### Install python packages

```bash
pip install -r requirements.txt
```

### Create database in psql

```bash
psql
CREATE DATABASE davids_games;
```

### Seed achievements into database

```bash
psql -f minesweeper_achievements.sql
```

## Running the App

```bash
flask run -p 5000
```

Then visit http://localhost:5000 to see the running app

## Testing

### Create test database in psql

```bash
psql
CREATE DATABASE davids_games_test;
```

### Running all tests (from root directory)

```python3 -m unittest```

## Project Structure

```
\                                 # Root folder
 |--app.py                        # main routes scripts
 |--forms.py                      # WTForms classes
 |--minesweeper_achievements.sql  # minesweeper achievements seed file
 |--minesweeper.py                # minesweeper helper functions
 |--models.py                     # database models and methods
 |--readme.md                     # project readme
 |--requirements.txt              # dependencies
 |--test_game_views.py            # game views tests
 |--test_minesweeper_api.py       # minesweeper api tests
 |--test_minesweeper_models.py    # minesweeper model tests
 |--test_user_model.py            # user model tests 
 |--test_user_views.py            # user views tests

 \static                          # static files folder
 |--/images                       # images folder
 |--/stylesheets                  # stylesheets folder
 |--/js                           # javascript files folder
 
 \templates                       # jinja templates folder
 |--/users                        # user route templates
 |--404_not_found.html            # 404 page template
 |--base.html                     # base template
 |--games.html                    # games page template
 |--minesweeper.html              # minesweeper game page template
```

## API

List of available routes:

**Auth/Signup routes**:\
`GET /signup` - renders user signup form\
`POST /signup` - submits user signup form\
`GET /login` - renders user login form\
`POST /login` - submits user login form\
`POST /logout` - user logout request (login required)\

**General routes**:\
`GET /` - redirects to games listing page\

**User routes**:\
`GET /users` - renders user index with optional username filter (login required)\
`GET /users/:user_id` - renders user profile page (login required)\
`GET /users/:user_id/edit` - renders edit profile form (login required)\
`POST /users/:user_id/edit` - submits edit profile form (login required)\
`POST /users/:user_id/delete - deletes user account (login required)\

**Game routes**:\
`GET /games` - renders games listing page\
`GET /games/minesweeper` - renders minesweeper game (login required)\

**Minesweeper API routes**:\
`GET /api/minesweeper/scores` - gets JSON data of top 20 scores for each difficulty (login required)\
`POST /api/minesweeper/scores` - submits minesweeper score to database
`POST /api/minesweeper/stats` - submits minesweeper stats to database
