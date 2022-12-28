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
    app, login_manager
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


# class UserInfoViewTestCase(UserBaseViewTestCase):
#     """ Tests for viewing user info """

#     def test_users_listing(self):
#         """ Test GET /users route with login """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.get('/users')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('Here is the user listing page', html)

#     def test_users_listing_w_query(self):
#         """ Test GET /users route with query string with login """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.get('/users?q=u1')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('Here is the user listing page', html)
#             self.assertNotIn('u2', html)

#     def test_users_listing_wo_auth(self):
#         """ Test accessing /users route without authorization """

#         with self.client as c:

#             resp = c.get("/users", follow_redirects=True)

#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>Sign up now to get your own personalized timeline!</p>', html)
#             self.assertIn("Access unauthorized.", html)

#     def test_user_profile(self):
#         """ Test user profile page with login """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.get(f'/users/{self.u2_id}')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('Here is the user profile page', html)
#             self.assertIn('<h4 id="sidebar-username">@u2</h4>', html)


# class UserFollowViewTestCase(UserBaseViewTestCase):
#     """ Tests for viewing user follows """

#     def test_user_following_page(self):
#         """ Test GET /users/<user_id>/following """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             u1 = User.query.get(self.u1_id)
#             u2 = User.query.get(self.u2_id)

#             u2.following.append(u1)
#             db.session.commit()

#             resp = c.get(f'/users/{self.u2_id}/following')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>@u1</p>', html)
#             self.assertIn('Here is the following page', html)

#     def test_user_following_page_wo_auth(self):
#         """ Test accessing /users/<user_id>/following route without authorization """

#         with self.client as c:

#             resp = c.get(f'/users/{self.u2_id}/following', follow_redirects=True)

#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>Sign up now to get your own personalized timeline!</p>', html)
#             self.assertIn("Access unauthorized.", html)

#     def test_user_followers_page(self):
#         """ Test GET /users/<user_id>/followers """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             u1 = User.query.get(self.u1_id)
#             u2 = User.query.get(self.u2_id)

#             u1.following.append(u2)
#             db.session.commit()

#             resp = c.get(f'/users/{self.u2_id}/followers')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>@u1</p>', html)
#             self.assertIn('Here is the followers page', html)

#     def test_user_followers_page_wo_auth(self):
#         """ Test accessing /users/<user_id>/followers route without authorization """

#         with self.client as c:

#             resp = c.get(f'/users/{self.u2_id}/followers', follow_redirects=True)

#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>Sign up now to get your own personalized timeline!</p>', html)
#             self.assertIn("Access unauthorized.", html)

#     def test_follow_user_post(self):
#         """ Test POST route to follow a user """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.post(f'/users/follow/{self.u2_id}', follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             u1 = User.query.get(self.u1_id)
#             u2 = User.query.get(self.u2_id)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>@u2</p>', html)
#             self.assertIn('Here is the following page', html)
#             self.assertIn(u1, u2.followers)

#     def test_unfollow_user_post(self):
#         """ Test POST route to unfollow a user """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             u1 = User.query.get(self.u1_id)
#             u2 = User.query.get(self.u2_id)

#             u2.followers.append(u1)
#             db.session.commit()

#             resp = c.post(f'/users/stop-following/{self.u2_id}', follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertNotIn('<p>@u2</p>', html)
#             self.assertIn('Here is the following page', html)
#             self.assertNotIn(u1, u2.followers)

# class UserUpdateViewTestCase(UserBaseViewTestCase):
#     """ Tests for updating a user """

#     def test_update_user_form(self):
#         """ Test display of user update form """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.get('/users/profile')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', html)
#             self.assertIn(
#                 '<input class="form-control" id="username" name="username" placeholder="Username" required type="text" value="u1">',
#                 html
#             )

#     def test_update_user_form_submit(self):
#         """ Test submission of user update form """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             d={
#                 "username": 'u1',
#                 "email": 'u1new@email.com',
#                 "image_url": DEFAULT_IMAGE_URL,
#                 "header_image_url": DEFAULT_HEADER_IMAGE_URL,
#                 "bio": 'what bio',
#                 "location": 'Hawaii',
#                 "password": "password"
#             }
#             resp = c.post('/users/profile', data=d, follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             u1 = User.query.get(self.u1_id)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('Here is the user profile page', html)
#             self.assertIn('Hawaii', html)
#             self.assertIn('what bio', html)
#             self.assertEqual(u1.location, 'Hawaii')
#             self.assertEqual(u1.bio, 'what bio')
#             self.assertEqual(u1.email, 'u1new@email.com')
#             self.assertEqual(u1.username, 'u1')

# class UserDeleteViewTestCase(UserBaseViewTestCase):
#     """ Tests for deleting a user """

#     def test_user_delete(self):
#         """ Test POST to /users/delete route """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.post('/users/delete', follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
#             self.assertIn("User successfully deleted :(", html)
#             self.assertIsNone(User.query.get(self.u1_id))

#     def test_user_delete_wo_auth(self):
#         """ Test POST to /users/delete route without authentication """

#         with self.client as c:

#             resp = c.post('/users/delete', follow_redirects=True)

#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<p>Sign up now to get your own personalized timeline!</p>', html)
#             self.assertIn("Access unauthorized.", html)

# class UserLikesListTestCase(UserBaseViewTestCase):
#     """ Tests for listing a user's likes """

#     def test_user_likes_page(self):
#         """ Test GET to /users/<int:user_id>/likes """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             m1 = Message.query.get(self.m1_id)
#             u1 = User.query.get(self.u1_id)
#             u1.liked_messages.append(m1)
#             db.session.commit()

#             resp = c.get(f"/users/{self.u1_id}/likes")
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('m1-text', html)

# class UserSignupTestCase(UserBaseViewTestCase):
#     """ Tests for when a user attempts to signup or visit the signup page """

#     def test_signup_page(self):
#         """ Test GET to /signup """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.get("/signup")
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
#             self.assertNotIn(CURR_USER_KEY, session)

#     def test_signup_submission(self):
#         """ Test POST to /signup """

#         with self.client as c:

#             d = {
#                 "username": "test_4",
#                 "password": "password",
#                 "email": "test_4@email.com",
#                 "image_url": ""
#             }

#             resp = c.post("/signup", data=d, follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             u4 = User.query.filter_by(username = "test_4").one()

#             self.assertEqual(resp.status_code, 200)
#             self.assertEqual(session[CURR_USER_KEY], u4.id)
#             self.assertIn('<p>@test_4</p>', html)

#     def test_signup_submission_repeat_name(self):
#         """ Test POST to /signup with repeat username """

#         with self.client as c:

#             d = {
#                 "username": "u1",
#                 "password": "password",
#                 "email": "test_4@email.com",
#                 "image_url": ""
#             }

#             resp = c.post('/signup', data=d, follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('Username already taken', html)
#             self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
#             self.assertNotIn(CURR_USER_KEY, session)




# class UserLogoutViewTestCase(UserBaseViewTestCase):
#     """ Tests for logging out a user """

#     def test_user_logout(self):
#         """ Test POST to /logout """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.post('/logout', follow_redirects=True)
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('You have been succesfully logged out!', html)
#             self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
#             self.assertIn('<form method="POST" id="user_form">', html)
#             self.assertNotIn(CURR_USER_KEY, session)


# class UserHomepageViewTestCase(UserBaseViewTestCase):
#     """ Tests for home page """

#     def test_user_homepage(self):
#         """ Test homepage for logged in user """

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1_id

#             resp = c.get('/')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn('Here is the home page', html)
#             self.assertIn('<p>@u1</p>', html)


#     def test_user_homepage_logged_out(self):
#         """ Test homepage for logged out user """

#         with self.client as c:
#             resp = c.get('/')
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn(
#                 '<p>Sign up now to get your own personalized timeline!</p>',
#                 html
#             )