""" SQLAlchemy models for David's Games """

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_USER_IMAGE_URL = '/static/images/default-pig.png'
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
        primary_key = True
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

    # TODO:
    # def __repr__(self) -> str:
    #     return super().__repr__()


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

    # TODO:
    # preferences
    # minesweeper scores
    # achievements
    # minesweeper_stats
    # history


class Role(db.Model):
    """ Roles table model """

    __tablename__ = 'roles'

    id = db.Column(
        db.Integer,
        primary_key = True
    )
    name = db.Column(
        db.String(20),
        nullable = False,
        unique = True
    )