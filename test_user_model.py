""" User model tests """

import os
from unittest import TestCase
from models import (db, User, Role, connect_db, DEFAULT_USER_ROLE,
                    DEFAULT_USER_IMAGE_URL)
from sqlalchemy.exc import IntegrityError
from app import app

os.environ['DATABASE_URL'] = "postgresql:///davids_games_test"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))

connect_db(app)
with app.app_context():
    db.drop_all()
    db.create_all()

    # Populate default user role
    user_role = Role(name = DEFAULT_USER_ROLE)
    db.session.add(user_role)
    db.session.commit()


class UserModelTestCase(TestCase):
    """ Test user model class """

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


    def test_user_model(self):
        """ Test users created in setup """

        with app.app_context():
            u1 = User.query.get(self.u1_id)
            self.assertEqual(u1.role.name, DEFAULT_USER_ROLE)
            self.assertEqual(len(u1.minesweeper_scores), 0)
            self.assertEqual(len(u1.minesweeper_stat), 0)
            self.assertEqual(len(u1.minesweeper_achievements), 0)
            self.assertEqual(u1.image_url, DEFAULT_USER_IMAGE_URL)


    def test_is_admin(self):
        """ Test is_admin instance method """

        with app.app_context():
            u1 = User.query.get(self.u1_id)
            self.assertFalse(u1.is_admin())


    def test_user_signup(self):
        """ Test user signup class method """

        with app.app_context():
            u2 = User.signup(
                username = 'user2',
                password = 'password',
                display_name = 'user2',
                email = 'user2@email.com'
            )
            db.session.commit()

            u2_db = User.query.get(u2.id)
            self.assertEqual(u2, u2_db)
            self.assertEqual(len(u2_db.minesweeper_scores), 0)
            self.assertEqual(len(u2_db.minesweeper_stat), 0)
            self.assertEqual(len(u2_db.minesweeper_achievements), 0)
            self.assertNotEqual('password', u2_db.password)


    def test_invalid_user_signup(self):
        """ Test user signup with invalid inputs """

        with app.app_context():
            # Test signup with repeat username
            User.signup(
                username = 'user1',
                password = 'password',
                display_name = 'user1not',
                email = 'user1not@email.com'
            )

            with self.assertRaises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Test signup with repeat display name
            User.signup(
                username = 'user1not',
                password = 'password',
                display_name = 'user1',
                email = 'user1not@email.com'
            )

            with self.assertRaises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Test signup with repeat email
            User.signup(
                username = 'user2',
                password = 'password',
                display_name = 'user2',
                email = 'user1@email.com'
            )

            with self.assertRaises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Test signup with no username
            User.signup(
                username = None,
                password = 'password',
                display_name = 'user2',
                email = 'user2@email.com'
            )

            with self.assertRaises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Test signup with no email
            User.signup(
                username = 'user2',
                password = 'password',
                display_name = 'user2',
                email = None
            )

            with self.assertRaises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Test signup with no password
            user_no_pwd = User(
                username = 'user2',
                password = None,
                display_name = 'user2',
                email = 'user2@email.com',
            )

            with self.assertRaises(IntegrityError):
                db.session.add(user_no_pwd)
                db.session.commit()

            db.session.rollback()


    def test_user_authenticate(self):
        """ Test user authenticate class method """

        with app.app_context():
            # Test valid authenticate credentials
            u1 = User.query.get(self.u1_id)
            authenticated_user = User.authenticate('user1', 'password')

            self.assertEqual(u1, authenticated_user)

            # Invalid username
            invalid_name_auth = User.authenticate('not_a_user', 'password')

            self.assertFalse(invalid_name_auth)

            # Invalid password
            invalid_pwd_auth = User.authenticate('user1', 'not_password')

            self.assertFalse(invalid_pwd_auth)