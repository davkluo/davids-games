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

        serialized = score1.serialize()
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


    # def test_new_message(self):
    #     """ create a message instance and test it's properties """

    #     u1 = User.query.get(self.u1_id)

    #     new_message = Message(text = "This is a test message", user_id = u1.id)

    #     db.session.add(new_message)
    #     db.session.commit()

    #     new_message_db = Message.query.get(new_message.id)

    #     #testing message table
    #     self.assertEqual(new_message_db, new_message)
    #     self.assertEqual(new_message_db.text, "This is a test message")


    #     #testing user to message relationship
    #     self.assertEqual(new_message_db.user, u1)
    #     self.assertEqual(len(new_message_db.likers), 0)


    # def test_new_invalid_message(self):
    #     """ Test creating messages with invalid inputs """

    #     new_message_no_text = Message(text = None, user_id=self.u1_id)

    #     with self.assertRaises(IntegrityError):
    #         db.session.add(new_message_no_text)
    #         db.session.commit()
    #     db.session.rollback()

    #     new_message_no_user = Message(text = "This is text", user_id=None)

    #     with self.assertRaises(IntegrityError):
    #         db.session.add(new_message_no_user)
    #         db.session.commit()
    #     db.session.rollback()

    #     new_message_non_existent_user = Message(text = "This is also text", user_id=0)

    #     with self.assertRaises(IntegrityError):
    #         db.session.add(new_message_non_existent_user)
    #         db.session.commit()
    #     db.session.rollback()

    # def test_like_message(self):
    #     """ Test liking a message """

    #     u1 = User.query.get(self.u1_id)
    #     m1 = Message.query.get(self.m1_id)

    #     u1.liked_messages.append(m1)
    #     db.session.commit()

    #     self.assertIn(u1, m1.likers)
    #     self.assertIn(m1, u1.liked_messages)
    #     self.assertEqual(len(Like.query.all()), 1)

    # def test_unlike_message(self):
    #     """ Test unliking a message """

    #     u1 = User.query.get(self.u1_id)
    #     m1 = Message.query.get(self.m1_id)

    #     u1.liked_messages.append(m1)
    #     db.session.commit()

    #     num_likes_before_unliking = len(Like.query.all())

    #     u1.liked_messages.remove(m1)
    #     db.session.commit()

    #     num_likes_after_unliking = len(Like.query.all())

    #     self.assertNotIn(u1, m1.likers)
    #     self.assertNotIn(m1, u1.liked_messages)
    #     self.assertEqual(num_likes_before_unliking - 1, num_likes_after_unliking)


    # def test_is_liked_by(self):
    #     """ Test the Message.is_liked_by method """

    #     u1 = User.query.get(self.u1_id)
    #     u2 = User.query.get(self.u2_id)
    #     m1 = Message.query.get(self.m1_id)

    #     u1.liked_messages.append(m1)
    #     db.session.commit()

    #     self.assertTrue(m1.is_liked_by(u1))
    #     self.assertFalse(m1.is_liked_by(u2))


    # def test_delete_user_deletes_messages(self):
    #     """ Test that deleting a user deletes their messages """

    #     u1 = User.query.get(self.u1_id)
    #     u1_num_messages = len(u1.messages)
    #     num_messages_before = len(Message.query.all())

    #     User.query.filter(User.id == u1.id).delete()
    #     db.session.commit()

    #     # Querying the message should now return None because message is deleted
    #     m1 = Message.query.get(self.m1_id)

    #     num_messages_after = len(Message.query.all())

    #     self.assertIsNone(m1)
    #     self.assertEqual(num_messages_before - u1_num_messages, num_messages_after)