""" SQLAlchemy models for David's Games """

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_USER_IMAGE_URL = '/static/images/default-pic.png'
DEFAULT_USER_ROLE = 'user'


def connect_db(app):
    """ Connect this database to provided Flask app """

    app.app_context().push()
    db.app = app
    db.init_app(app)


class User(db.Model, UserMixin):
    """ User table model """

    __tablename__ = 'users'

    ###### TABLE COLUMNS ######

    id = db.Column(
        db.Integer,
        primary_key = True,
        autoincrement = True
    )
    username = db.Column(
        db.String(20),
        nullable = False,
        unique = True
    )
    password = db.Column(
        db.Text,
        nullable = False
    )
    display_name = db.Column(
        db.String(20),
        nullable = False,
        unique = True
    )
    email = db.Column(
        db.Text,
        nullable = False,
        unique = True
    )
    role_name = db.Column(
        db.String(20),
        db.ForeignKey('roles.name'),
        nullable = False,
        default = DEFAULT_USER_ROLE
    )
    image_url = db.Column(
        db.Text,
        nullable = False,
        default = DEFAULT_USER_IMAGE_URL
    )
    country = db.Column(
        db.String(30)
    )
    bio = db.Column(
        db.Text
    )

    ###### INSTANCE METHODS ######

    def __repr__(self):
        return f'<User {self.id} {self.username}>'


    def is_admin(self):
        """ Return true if user has an admin role """

        return self.role.name == 'admin'


    ###### CLASS METHODS ######

    @classmethod
    def signup(cls, username, password, display_name, email):
        """ Register user in system with hashed password.

        Returns user.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        new_user = User(
            username = username,
            password = hashed_pwd,
            display_name = display_name,
            email = email
        )

        db.session.add(new_user)
        return new_user


    @classmethod
    def authenticate(cls, username, password):
        """ Try to authenticate user with provided username.

        Returns user on successful authentication, otherwise False.
         """

        user = cls.query.filter_by(username = username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    ###### RELATIONSHIPS ######

    role = db.relationship('Role', backref = 'users')

    minesweeper_scores = db.relationship('MinesweeperScore', backref = 'user')

    minesweeper_stats = db.relationship('MinesweeperStat', backref = 'user')

    minesweeper_achievements = db.relationship(
        'MinesweeperAchievement',
        secondary = 'users_minesweeper_achievements',
        backref = 'users'
    )


class Role(db.Model):
    """ Roles table model """

    __tablename__ = 'roles'

    ###### TABLE COLUMNS ######

    id = db.Column(
        db.Integer,
        primary_key = True,
        autoincrement = True
    )
    name = db.Column(
        db.String(20),
        nullable = False,
        unique = True
    )


class MinesweeperScore(db.Model):
    """ Minesweeper scores table model """

    __tablename__ = 'minesweeper_scores'

    ###### TABLE COLUMNS ######

    id = db.Column(
        db.Integer,
        primary_key = True,
        autoincrement = True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable = False
    )
    time = db.Column(
        db.Integer,
        nullable = False
    )
    level = db.Column(
        db.String(30),
        nullable = False
    )
    submitted_at = db.Column(
        db.DateTime,
        nullable = False,
        default = db.func.now()
    )

    ###### INSTANCE METHODS ######

    def serialize(self):
        """Serialize to dictionary"""

        return {
            "id": self.id,
            "user_id": self.user_id,
            "time": self.time,
            "level": self.level,
            "submitted_at": self.submitted_at,
            "user_display_name": self.user.display_name
        }

    @classmethod
    def get_scores_for_level(cls, level, qty):
        """ Query the top <qty> scores for a given <level>
        Return a list of score objects.
        """

        return (cls.query
            .filter(cls.level == level)
            .order_by(cls.time)
            .limit(qty)
            .all())


class MinesweeperStat(db.Model):
    """ Minesweeper stats table model """

    __tablename__ = 'minesweeper_stats'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key = True,
    )
    games_played = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    games_won = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    beginner_games_won = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    intermediate_games_won = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    expert_games_won = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    time_played = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    cells_revealed = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    win_streak = db.Column(
        db.Integer,
        nullable = False,
        default = 0
    )
    last_played_at = db.Column(
        db.DateTime,
        nullable = False,
        default = db.func.now()
    )


class MinesweeperAchievement(db.Model):
    """ Minesweeper achievements table model """

    __tablename__ = 'minesweeper_achievements'

    id = db.Column(
        db.Integer,
        primary_key = True,
        autoincrement = True
    )
    title = db.Column(
        db.String(50),
        nullable = False
    )
    description = db.Column(
        db.Text,
        nullable = False
    )
    color = db.Column(
        db.Text,
        nullable = False
    )


class UserMinesweeperAchievement(db.Model):
    """ User - minesweeper achievements association table model """

    __tablename__ = 'users_minesweeper_achievements'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key = True
    )
    achievement_id = db.Column(
        db.Integer,
        db.ForeignKey('minesweeper_achievements.id', ondelete='CASCADE'),
        primary_key = True
    )
    achieved_at = db.Column(
        db.DateTime,
        nullable = False,
        default = db.func.now()
    )


    # TODO:
    # preferences -> make this a to-do for now...
    # games table -> maybe when we have more games