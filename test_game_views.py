""" Game view tests """

import os
from unittest import TestCase
from models import (db, User, Role, connect_db, DEFAULT_USER_ROLE)
from app import app

os.environ['DATABASE_URL'] = "postgresql:///davids_games_test"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

connect_db(app)
with app.app_context():
    db.drop_all()
    db.create_all()

    # Populate default user role
    user_role = Role(name=DEFAULT_USER_ROLE)
    db.session.add(user_role)
    db.session.commit()

class GameBaseViewTestCase(TestCase):
    """ Test user views """

    def setUp(self):
        """ Set up before each test """

        self.client = app.test_client()
        with app.app_context():
            User.query.delete()

            u1 = User.signup(
                username = 'user1',
                password = 'password',
                display_name = 'user1',
                email = 'user1@email.com'
            )

            db.session.commit()

            self.u1_id = u1.id


    def tearDown(self):
        """ Tear down after each test """

        with app.app_context():
            db.session.rollback()


class GameListViewTestCase(GameBaseViewTestCase):
    """ Test game list views """

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