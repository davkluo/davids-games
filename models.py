""" SQLAlchemy models for David's Games """

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_USER_IMAGE_URL = '/static/images/default-pic.png'
DEFAULT_USER_ROLE = 'user'

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR


def connect_db(app):
    """ Connect this database to provided Flask app """

    with app.app_context():
        db.app = app
        db.init_app(app)


class User(db.Model):
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
    country = db.Column( #TODO: Do something with this country value
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

    minesweeper_stat = db.relationship('MinesweeperStat', backref = 'user')

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
            .order_by(cls.time, cls.submitted_at)
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

    ###### INSTANCE METHODS ######

    def serialize(self):
        """Serialize to dictionary"""

        return {
            "user_id": self.user_id,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "beginner_games_won": self.beginner_games_won,
            "intermediate_games_won": self.intermediate_games_won,
            "expert_games_won": self.expert_games_won,
            "time_played": self.time_played,
            "cells_revealed": self.cells_revealed,
            "win_streak": self.win_streak,
            "last_played_at": self.last_played_at
        }


    def calc_time_since_last_played(self):
        """ Calculate time since last played and return in format
        __D __H __M """

        time_in_s = round((datetime.utcnow() - self.last_played_at).total_seconds())

        formatted_time = ''

        days_since = time_in_s // SECONDS_PER_DAY
        hours_since = (time_in_s % SECONDS_PER_DAY) // SECONDS_PER_HOUR
        minutes_since = (time_in_s % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE

        if days_since:
            return f'{days_since}D'

        if hours_since:
            return f'{hours_since}H'

        return f'{minutes_since}M'


    @property
    def time_played_formatted(self):
        """ Format time played as __H __M __S """

        formatted_time = ''

        hours_played = self.time_played // SECONDS_PER_HOUR
        minutes_played = (self.time_played % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
        seconds_played = (self.time_played % SECONDS_PER_MINUTE)

        if hours_played:
            formatted_time += f'{hours_played}H '
        if minutes_played:
            formatted_time += f'{minutes_played}M '

        formatted_time += f'{seconds_played}S'

        return formatted_time


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
        nullable = False,
        unique = True
    )
    description = db.Column(
        db.Text,
        nullable = False
    )
    color = db.Column(
        db.Text,
        nullable = False
    )

    ###### INSTANCE METHODS ######

    def serialize(self):
        """Serialize to dictionary"""

        return {
            "title": self.title,
            "description": self.description,
            "color": self.color,
        }


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

    # TODO: In the future
    # user_preferences -> keep track of site dark mode
    # games table -> maybe when we have more games