import os
from dotenv import load_dotenv

from flask import (
    Flask, render_template, flash, request, url_for, redirect, abort, g
)

from flask_login import (
    LoginManager, login_user, logout_user, current_user, login_required
)

from urllib.parse import (
    urlparse, urljoin
)

from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension

from models import (
    db, connect_db, User, Role
)

from forms import (
    LoginForm, UserAddForm, CSRFProtection
)

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.session.rollback()
db.create_all()


###### Flask-login redirect target check ######
# Credit to: https://web.archive.org/web/20120517003641/http://flask.pocoo.org/snippets/62/

def is_safe_url(target):
    """ Check if a URL is safe for redirecting to """

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


###### Flask-login setup ######

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


###### User signup/login/logout ######

@app.before_request
def add_csrf_only_form():
    """ Add a CSRF-only form so every route can use it """

    g.csrf_form = CSRFProtection()


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    """ Handle showing and submission of signup form. """

    if current_user.is_authenticated:
        logout_user()

    form = UserAddForm()

    if form.validate_on_submit():
        username = form.username.data
        display_name = form.display_name.data
        email = form.email.data

        try:
            user = User.signup(
                username = username,
                password = form.password.data,
                display_name = display_name,
                email = email
            )

            db.session.commit()

            login_user(user)

            return redirect(url_for('homepage'))

        except IntegrityError:
            db.session.rollback()

            is_unique_username = (User.query
                .filter(User.username == username)
                .one_or_none()) is None
            is_unique_display_name = (User.query
                .filter(User.display_name == display_name)
                .one_or_none()) is None
            is_unique_email = (User.query
                .filter(User.email == email)
                .one_or_none()) is None

            # TODO: Decide if we want these or flash messages
            if not is_unique_username:
                form.username.errors = ['Username already taken.']
            if not is_unique_display_name:
                form.display_name.errors = ['Display name already taken.']
            if not is_unique_email:
                form.email.errors = ['Email already taken.']

    return render_template('users/signup.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    """ Handle showing and submission of login form. """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data,
            password = form.password.data
        )

        if user:
            login_user(user)
            flash('Logged in successfully.', 'success')

            next = request.args.get('next')
            if not is_safe_url(next):
                return abort(400)

            return redirect(next or url_for('homepage'))

        flash('Invalid credentials.', 'danger')

    return render_template('users/login.html', form=form)


@app.post('/logout')
@login_required
def logout():
    """ Handle logout of user and redirect to home page """

    form = g.csrf_form

    if not form.validate_on_submit():
        flash('Access unauthorized.', 'danger')
        return redirect(url_for('homepage'))

    logout_user()

    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


###### General user routes ######

# List of users with query string
# Show user



###### Minesweeper game routes ######



###### PLACEHOLDER ######

@app.get('/')
def homepage():
    """ Show the home page """

    return 'This is the home page.'