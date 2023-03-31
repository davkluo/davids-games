""" Minesweeper API tests """


from datetime import datetime

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


class MinesweeperAPITestCase(TestCase):
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


    def test_score_submission(self):
        """ Test POST to /api/minesweeper/scores """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.post(
                '/api/minesweeper/scores',
                json={
                    "time": 100,
                    "level": "expert"
                }
            )

            self.assertEqual(resp.json['score']['user_id'], self.u1_id)
            self.assertEqual(resp.json['score']['time'], 100)
            self.assertEqual(resp.json['score']['level'], 'expert')

            u1 = User.query.get(self.u1_id)

            self.assertEqual(resp.status_code, 201)
            self.assertEqual(MinesweeperScore.query.count(), 1)
            self.assertEqual(len(u1.minesweeper_scores), 1)


    def test_score_retrieval(self):
        """ Test GET to /api/minesweeper/scores """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get('/api/minesweeper/scores')
            top_scores = resp.json['scores']

            self.assertIsInstance(top_scores['beginner'], list)
            self.assertIsInstance(top_scores['intermediate'], list)
            self.assertIsInstance(top_scores['expert'], list)


    # TODO: Finish test and refactor achievements checking logic for when
    #       achievement doesn't exist in DB yet

    # def test_stat_submission(self):
    #     """ Test POST to /api/minesweeper/stats """

    #     with self.client as c:
    #         d = {
    #             "username": "user1",
    #             "password": "password",
    #         }
    #         c.post('/login', data=d, follow_redirects=True)

    #         resp = c.post(
    #             '/api/minesweeper/stats',
    #             json={
    #                 "games_played": 1,
    #                 "games_won": 1,
    #                 "beginner_games_won": 0,
    #                 "intermediate_games_won": 0,
    #                 "expert_games_won": 1,
    #                 "time_played": 100,
    #                 "cells_revealed": 381,
    #                 "last_played_at": datetime.now()
    #             }
    #         )
    #         stats = resp.json['stats']
    #         new_achievements = resp.json['new_achievements']

    #         self.assertIsInstance(stats['last_played_at'], datetime)
    #         stats_copy = stats.copy()
    #         stats_copy.pop('last_played_at')

    #         self.assertEqual(stats,
    #             {
    #                 "games_played": 1,
    #                 "games_won": 1,
    #                 "beginner_games_won": 0,
    #                 "intermediate_games_won": 0,
    #                 "expert_games_won": 1,
    #                 "time_played": 100,
    #                 "cells_revealed": 381
    #             }
    #         )

    #         self.assertIsInstance(new_achievements, list)


    # TODO: Test login_required routes with flask-login
    # TODO: Test getting new achievements