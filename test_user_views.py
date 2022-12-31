""" User view tests """


import os
from unittest import TestCase

from models import (
    db, User, Role, MinesweeperScore, MinesweeperStat, MinesweeperAchievement,
    UserMinesweeperAchievement, connect_db, DEFAULT_USER_ROLE,
    DEFAULT_USER_IMAGE_URL
)

from flask import session

from flask_login import (
    LoginManager, login_user, logout_user, current_user, login_required
)

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


class UserBaseViewTestCase(TestCase):
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


class UserLoginViewTestCase(UserBaseViewTestCase):
    """ Test user login views """

    def test_login_form(self):
        """ Test GET to /login """

        with self.client as c:
            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('WELCOME BACK', html)
            self.assertIn('id="user-form"', html)


    def test_login_submission(self):
        """ Test POST to /login with valid credentials """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }

            resp = c.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("id='game-thumbnail-list'", html)
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(current_user.id, self.u1_id)


    def test_invalid_pwd_login_submission(self):
        """ Test POST to /login with invalid password """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "pAsSwOrD",
            }

            resp = c.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('WELCOME BACK', html)
            self.assertIn('id="user-form"', html)
            self.assertIn('Invalid credentials.', html)
            self.assertFalse(current_user.is_authenticated)


    def test_invalid_user_login_submission(self):
        """ Test POST to /login with invalid username """

        with self.client as c:
            d = {
                "username": "user1000",
                "password": "password",
            }

            resp = c.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('WELCOME BACK', html)
            self.assertIn('id="user-form"', html)
            self.assertIn('Invalid credentials.', html)
            self.assertFalse(current_user.is_authenticated)


class UserSignupTestCase(UserBaseViewTestCase):
    """ Test user signup """

    def test_signup_page(self):
        """ Test GET to /signup """

        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('CREATE AN ACCOUNT', html)


    def test_signup_submission(self):
        """ Test POST to /signup """

        with self.client as c:
            d = {
                "username": "user2",
                "password": "password",
                "email": "user2@email.com",
                "display_name": "user2"
            }

            resp = c.post("/signup", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            u2 = User.query.filter_by(username = "user2").one()

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(current_user.is_authenticated)
            self.assertIn('game-thumbnail-list', html)


    def test_invalid_signup_submission(self):
        """ Test POST to /signup with repeat username """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
                "email": "user1@email.com",
                "display_name": "user1"
            }

            resp = c.post('/signup', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username already taken.', html)
            self.assertIn('Display name already taken.', html)
            self.assertIn('E-mail already taken.', html)
            self.assertIn('CREATE AN ACCOUNT', html)


class UserInfoViewTestCase(UserBaseViewTestCase):
    """ Tests for viewing user info """

    def test_users_listing(self):
        """ Test GET /users route with login """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user-index', html)


    def test_users_listing_w_query(self):
        """ Test GET /users route with query string with login """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get('/users?q=user1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user-index', html)
            self.assertIn('user1', html)


    # TODO: Figure out how to test login_required of flask-login
    # def test_users_listing_wo_auth(self):
    #     """ Test accessing /users route without authorization """

    #     with self.client as c:
    #         resp = c.get('/users')
    #         html = resp.get_data(as_text=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('WELCOME BACK', html)
    #         self.assertIn('Please log in to view this page.', html)


    def test_user_profile(self):
        """ Test user profile page with login """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get(f'/users/{self.u1_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user-profile', html)
            self.assertIn('user1', html)


class UserUpdateViewTestCase(UserBaseViewTestCase):
    """ Tests for updating a user """

    def test_update_user_form(self):
        """ Test display of user update form """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get(f'/users/{self.u1_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('EDIT PROFILE', html)
            self.assertIn('user-form', html)


    def test_update_user_form_submit(self):
        """ Test submission of user update form """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            d={
                "image_url": DEFAULT_USER_IMAGE_URL,
                "bio": 'what bio',
            }
            resp = c.post(f'/users/{self.u1_id}/edit', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            u1 = User.query.get(self.u1_id)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user-profile', html)
            self.assertIn('what bio', html)
            self.assertEqual(u1.bio, 'what bio')


    # TODO: Test login_required with flask-login


class UserDeleteViewTestCase(UserBaseViewTestCase):
    """ Tests for deleting a user """

    def test_user_delete(self):
        """ Test POST to /users/delete route """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.post(f'/users/{self.u1_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('CREATE AN ACCOUNT', html)
            self.assertIn('User successfully deleted. See you again!', html)
            self.assertIsNone(User.query.get(self.u1_id))


    # TODO: Make the below test work with flask-login
    # def test_user_delete_wo_auth(self):
    #     """ Test POST to /users/delete route without authentication """

    #     with self.client as c:
    #         resp = c.post('/users/delete', follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('CREATE AN ACCOUNT', html)
    #         self.assertIn('Unauthorized access.', html)


class UserLogoutViewTestCase(UserBaseViewTestCase):
    """ Tests for logging out a user """

    def test_user_logout(self):
        """ Test POST to /logout """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Logged out successfully.', html)
            self.assertIn('WELCOME BACK', html)
            self.assertIn('user-form', html)
            self.assertFalse(current_user.is_authenticated)

    # TODO: Test login_required with flask-login


class UserHomepageViewTestCase(UserBaseViewTestCase):
    """ Tests for home page """

    def test_user_homepage(self):
        """ Test homepage for logged in user """

        with self.client as c:
            d = {
                "username": "user1",
                "password": "password",
            }
            c.post('/login', data=d, follow_redirects=True)

            resp = c.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('game-thumbnail-list', html)