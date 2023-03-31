""" Game view tests """


import os
from unittest import TestCase

from models import (
    db, User, Role, MinesweeperScore, MinesweeperStat, MinesweeperAchievement,
    UserMinesweeperAchievement, connect_db, DEFAULT_USER_ROLE,
    DEFAULT_USER_IMAGE_URL
)

from flask import session

# from flask_login import (
#     LoginManager, login_user, logout_user, current_user, login_required
# )

os.environ['DATABASE_URL'] = "postgresql:///davids_games_test"

from app import (
    app
)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

connect_db(app)

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

# Populate default user role
user_role = Role(name = DEFAULT_USER_ROLE)
db.session.add(user_role)
db.session.commit()


class GameBaseViewTestCase(TestCase):
    """ Test user views """

    def setUp(self):
        """ Set up before each test """

        User.query.delete()

        u1 = User.signup(
            username = 'user1',
            password = 'password',
            display_name = 'user1',
            email = 'user1@email.com'
        )

        db.session.commit()

        self.u1_id = u1.id
        self.client = app.test_client()


    def tearDown(self):
        """ Tear down after each test """

        db.session.rollback()


    def test_game_list(self):
        """ Test GET to /games """

        with self.client as c:
            resp = c.get('/games')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('game-thumbnail-list', html)


class MinesweeperViewTestCase(GameBaseViewTestCase):
    """ Test minesweeper game views """

    def test_game_page(self):
        """ Test GET to /games/minesweeper """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get('/games/minesweeper')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1 class='game-title mb-4'>MINESWEEPER</h1>", html)


    # TODO: Test login_required with flask-login