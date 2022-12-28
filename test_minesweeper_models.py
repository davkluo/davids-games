""" Minesweeper model tests """


from datetime import datetime

import os
from unittest import TestCase

from models import (
    db, User, Role, MinesweeperScore, MinesweeperStat, MinesweeperAchievement,
    UserMinesweeperAchievement, connect_db, DEFAULT_USER_ROLE,
    DEFAULT_USER_IMAGE_URL
)

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///davids_games_test"

from app import app

connect_db(app)

db.drop_all()
db.create_all()

# Populate default user role
user_role = Role(name = DEFAULT_USER_ROLE)
db.session.add(user_role)
db.session.commit()


class MinesweeperModelTestCase(TestCase):
    """ Test minesweeper model classes """

    def setUp(self):
        """ Set up before each test """

        User.query.delete()
        MinesweeperScore.query.delete()
        MinesweeperStat.query.delete()
        MinesweeperAchievement.query.delete()
        UserMinesweeperAchievement.query.delete()

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

        db.session.rollback()


class MinesweeperScoreTestCase(MinesweeperModelTestCase):
    """ Test minesweeper score model class """

    def test_new_score(self):
        """ Test addition of new score """

        u1 = User.query.get(self.u1_id)

        score1 = MinesweeperScore(
            user_id = u1.id,
            time = 100,
            level = 'expert'
        )

        score2 = MinesweeperScore(
            user_id = u1.id,
            time = 20,
            level = 'beginner'
        )

        db.session.add_all([score1, score2])
        db.session.commit()

        score1_db = MinesweeperScore.query.get(score1.id)
        score2_db = MinesweeperScore.query.get(score2.id)

        self.assertEqual(score1, score1_db)
        self.assertEqual(score2, score2_db)

        self.assertEqual(score1.time, 100)
        self.assertEqual(score1.level, 'expert')
        self.assertIsInstance(score1.submitted_at, datetime)
        self.assertEqual(score2.time, 20)
        self.assertEqual(score2.level, 'beginner')
        self.assertIsInstance(score2.submitted_at, datetime)

        self.assertEqual(len(u1.minesweeper_scores), 2)
        self.assertEqual(score1_db.user, u1)
        self.assertEqual(score2_db.user, u1)


    def test_invalid_new_Score(self):
        """ Test invalid addition of new score """

        score_no_user = MinesweeperScore(
            user_id = None,
            time = 100,
            level = 'expert'
        )

        with self.assertRaises(IntegrityError):
            db.session.add(score_no_user)
            db.session.commit()

        db.session.rollback()

        score_no_time = MinesweeperScore(
            user_id = self.u1_id,
            time = None,
            level = 'expert'
        )

        with self.assertRaises(IntegrityError):
            db.session.add(score_no_time)
            db.session.commit()

        db.session.rollback()

        score_no_level = MinesweeperScore(
            user_id  = self.u1_id,
            time = 100,
            level = None
        )

        with self.assertRaises(IntegrityError):
            db.session.add(score_no_level)
            db.session.commit()

        db.session.rollback()


    def test_user_deletion_cascades_to_scores(self):
        """ Test that user deletion cascades to minesweeper scores """

        score1 = MinesweeperScore(
            user_id = self.u1_id,
            time = 100,
            level = 'expert'
        )

        score2 = MinesweeperScore(
            user_id = self.u1_id,
            time = 20,
            level = 'beginner'
        )

        db.session.add_all([score1, score2])
        db.session.commit()

        self.assertEqual(MinesweeperScore.query.count(), 2)

        User.query.filter_by(id = self.u1_id).delete()

        self.assertEqual(MinesweeperScore.query.count(), 0)


    def test_get_scores_for_level(self):
        """ Test get_scores_for_level class method """

        score1 = MinesweeperScore(
            user_id = self.u1_id,
            time = 100,
            level = 'expert'
        )

        score2 = MinesweeperScore(
            user_id = self.u1_id,
            time = 20,
            level = 'beginner'
        )

        score3 = MinesweeperScore(
            user_id = self.u1_id,
            time = 19,
            level = 'beginner'
        )

        db.session.add_all([score1, score2, score3])
        db.session.commit()

        self.assertEqual(
            len(MinesweeperScore.get_scores_for_level('beginner', 20)), 2
        )
        self.assertEqual(
            len(MinesweeperScore.get_scores_for_level('intermediate', 20)), 0
        )
        self.assertEqual(
            len(MinesweeperScore.get_scores_for_level('expert', 20)), 1
        )


    def test_serialize(self):
        """ Test serialize instance method """

        score1 = MinesweeperScore(
            user_id = self.u1_id,
            time = 100,
            level = 'expert'
        )

        db.session.add(score1)
        db.session.commit()

        score1_db = MinesweeperScore.query.get(score1.id)

        serialized = score1_db.serialize()
        serialized.pop('id')
        serialized.pop('submitted_at')

        self.assertEqual(serialized,
            {
                "user_id": self.u1_id,
                "time": 100,
                "level": 'expert',
                "user_display_name": 'user1'
            }
        )


class MinesweeperStatTestCase(MinesweeperModelTestCase):
    """ Test minesweeper stat model class """

    def test_new_stat(self):
        """ Test addition of new minesweeper stat """

        u1 = User.query.get(self.u1_id)

        stat = MinesweeperStat(
            user_id = u1.id,
            games_played = 1,
            games_won = 1,
            beginner_games_won = 0,
            intermediate_games_won = 0,
            expert_games_won = 1,
            time_played = 100,
            cells_revealed = 381,
            win_streak = 1,
            last_played_at = db.func.now()
        )

        db.session.add(stat)
        db.session.commit()

        stat_db = MinesweeperStat.query.get(u1.id)

        self.assertEqual(stat, stat_db)

        self.assertEqual(stat_db.games_played, 1)
        self.assertEqual(stat_db.games_won, 1)
        self.assertEqual(stat_db.beginner_games_won, 0)
        self.assertEqual(stat_db.intermediate_games_won, 0)
        self.assertEqual(stat_db.expert_games_won, 1)
        self.assertEqual(stat_db.time_played, 100)
        self.assertEqual(stat_db.cells_revealed, 381)
        self.assertEqual(stat_db.win_streak, 1)
        self.assertIsInstance(stat_db.last_played_at, datetime)

        self.assertEqual(len(u1.minesweeper_stat), 1)
        self.assertEqual(stat_db.user, u1)


    def test_invalid_new_stat(self):
        """ Test addition of invalid new minesweeper stat """

        stat = MinesweeperStat(
            user_id = None,
            games_played = 1,
            games_won = 1,
            beginner_games_won = 0,
            intermediate_games_won = 0,
            expert_games_won = 1,
            time_played = 100,
            cells_revealed = 381,
            win_streak = 1,
            last_played_at = db.func.now()
        )

        with self.assertRaises(IntegrityError):
            db.session.add(stat)
            db.session.commit()

        db.session.rollback()


    def test_stat_defaults(self):
        """ Test default values for stats not provided """

        stat = MinesweeperStat(
            user_id = self.u1_id,
            games_played = None,
            games_won = None,
            beginner_games_won = None,
            intermediate_games_won = None,
            expert_games_won = None,
            time_played = None,
            cells_revealed = None,
            win_streak = None,
            last_played_at = None
        )

        db.session.add(stat)
        db.session.commit()

        stat_db = MinesweeperStat.query.get(self.u1_id)

        self.assertEqual(stat_db.games_played, 0)
        self.assertEqual(stat_db.games_won, 0)
        self.assertEqual(stat_db.beginner_games_won, 0)
        self.assertEqual(stat_db.intermediate_games_won, 0)
        self.assertEqual(stat_db.expert_games_won, 0)
        self.assertEqual(stat_db.time_played, 0)
        self.assertEqual(stat_db.cells_revealed, 0)
        self.assertEqual(stat_db.win_streak, 0)
        self.assertIsInstance(stat_db.last_played_at, datetime)


    def test_user_deletion_cascades_to_stats(self):
        """ Test that user deletion cascades to minesweeper stats """

        stat = MinesweeperStat(
            user_id = self.u1_id,
            games_played = 1,
            games_won = 1,
            beginner_games_won = 0,
            intermediate_games_won = 0,
            expert_games_won = 1,
            time_played = 100,
            cells_revealed = 381,
            win_streak = 1,
            last_played_at = db.func.now()
        )

        db.session.add(stat)
        db.session.commit()

        self.assertEqual(MinesweeperStat.query.count(), 1)

        User.query.filter_by(id = self.u1_id).delete()

        self.assertEqual(MinesweeperStat.query.count(), 0)


    def test_time_played_formatted(self):
        """ Test time_played_formatted @property method """

        stat = MinesweeperStat(
            user_id = self.u1_id,
            games_played = 1,
            games_won = 1,
            beginner_games_won = 0,
            intermediate_games_won = 0,
            expert_games_won = 1,
            time_played = 7199,
            cells_revealed = 381,
            win_streak = 1,
            last_played_at = db.func.now()
        )

        db.session.add(stat)
        db.session.commit()

        stat_db = MinesweeperStat.query.get(self.u1_id)

        self.assertEqual(stat_db.time_played_formatted, '1H 59M 59S')


    def test_serialize(self):
        """ Test serialize instance method """

        stat = MinesweeperStat(
            user_id = self.u1_id,
            games_played = 1,
            games_won = 1,
            beginner_games_won = 0,
            intermediate_games_won = 0,
            expert_games_won = 1,
            time_played = 100,
            cells_revealed = 381,
            win_streak = 1,
            last_played_at = db.func.now()
        )

        db.session.add(stat)
        db.session.commit()

        stat_db = MinesweeperStat.query.get(self.u1_id)

        serialized = stat_db.serialize()
        serialized.pop('last_played_at')

        self.assertEqual(serialized,
            {
                "user_id": self.u1_id,
                "games_played": 1,
                "games_won": 1,
                "beginner_games_won": 0,
                "intermediate_games_won": 0,
                "expert_games_won": 1,
                "time_played": 100,
                "cells_revealed": 381,
                "win_streak": 1,
            }
        )


#TODO: Figure out how to test calc_time_since_last_played


class MinesweeperAchievementTestCase(MinesweeperModelTestCase):
    """ Test minesweeper achievement model class """

    def test_new_achievement(self):
        """ Test addition of new achievement """

        achievement = MinesweeperAchievement(
            title = 'Test Achievement',
            description = 'For testing only',
            color = 'rgb(0, 0, 0)'
        )

        db.session.add(achievement)
        db.session.commit()

        achievement_db = MinesweeperAchievement.query.get(achievement.id)

        self.assertEqual(achievement, achievement_db)

        self.assertEqual(achievement_db.title, 'Test Achievement')
        self.assertEqual(achievement_db.description, 'For testing only')
        self.assertEqual(achievement_db.color, 'rgb(0, 0, 0)')

        self.assertEqual(len(achievement_db.users), 0)


    def test_invalid_new_achievement(self):
        """ Test invalid addition of new achievement """

        # No title
        achievement_no_title = MinesweeperAchievement(
            title = None,
            description = 'For testing only',
            color = 'rgb(0, 0, 0)'
        )

        with self.assertRaises(IntegrityError):
            db.session.add(achievement_no_title)
            db.session.commit()

        db.session.rollback()

        # No description
        achievement_no_description = MinesweeperAchievement(
            title = 'Test Achievement',
            description = None,
            color = 'rgb(0, 0, 0)'
        )

        with self.assertRaises(IntegrityError):
            db.session.add(achievement_no_description)
            db.session.commit()

        db.session.rollback()

        # No color
        achievement_no_color = MinesweeperAchievement(
            title = 'Test Achievement',
            description = 'For testing only',
            color = None
        )

        with self.assertRaises(IntegrityError):
            db.session.add(achievement_no_color)
            db.session.commit()

        db.session.rollback()


    def test_achievement_user_relationship(self):
        """ Test relationship between minesweeper achievement and user """

        achievement = MinesweeperAchievement(
            title = 'Test Achievement',
            description = 'For testing only',
            color = 'rgb(0, 0, 0)'
        )

        db.session.add(achievement)
        db.session.commit()

        u1 = User.query.get(self.u1_id)

        u1.minesweeper_achievements.append(achievement)

        self.assertEqual(UserMinesweeperAchievement.query.count(), 1)
        self.assertIn(achievement, u1.minesweeper_achievements)
        self.assertIn(u1, achievement.users)


    def test_user_deletion_cascades_to_achievements(self):
        """ Test that user deletion cascades to achievements """

        achievement = MinesweeperAchievement(
            title = 'Test Achievement',
            description = 'For testing only',
            color = 'rgb(0, 0, 0)'
        )

        db.session.add(achievement)
        db.session.commit()

        u1 = User.query.get(self.u1_id)

        u1.minesweeper_achievements.append(achievement)

        self.assertEqual(UserMinesweeperAchievement.query.count(), 1)
        self.assertEqual(MinesweeperAchievement.query.count(), 1)

        User.query.filter_by(id = self.u1_id).delete()

        self.assertEqual(UserMinesweeperAchievement.query.count(), 0)
        self.assertEqual(MinesweeperStat.query.count(), 0)


    def test_serialize(self):
        """ Test serialize instance method """

        achievement = MinesweeperAchievement(
            title = 'Test Achievement',
            description = 'For testing only',
            color = 'rgb(0, 0, 0)'
        )

        db.session.add(achievement)
        db.session.commit()

        achievement_db = MinesweeperAchievement.query.get(achievement.id)

        serialized = achievement_db.serialize()

        self.assertEqual(serialized,
            {
                'title': 'Test Achievement',
                'description': 'For testing only',
                'color': 'rgb(0, 0, 0)',
            }
        )