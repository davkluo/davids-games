from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length


class CSRFProtection(FlaskForm):
    """ Blank form for CSRF protection only. """


class UserAddForm(FlaskForm):
    """ Form for adding users. """

    username = StringField(
        'Username',
        validators=[Length(min=5, max=20)]
    )
    password = PasswordField(
        'Password',
        validators=[Length(min=6, max=20)]
    )
    display_name = StringField(
        'Display Name',
        validators=[Length(min=5, max=20)]
    )
    email = StringField(
        'E-mail',
        validators=[InputRequired(), Email()]
    )


class LoginForm(FlaskForm):
    """ Login form. """

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=20)]
    )
    password = PasswordField(
        'Password',
        validators=[Length(min=6, max=20)]
    )