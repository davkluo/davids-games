import os
from dotenv import load_dotenv

from flask import (
    Flask, render_template, flash, request, url_for, redirect, abort, g,
    jsonify, session
)

# from flask_login import (
#     LoginManager, login_user, logout_user, current_user, login_required
# )

from urllib.parse import (
    urlparse, urljoin
)

from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension

from models import (
    db, connect_db, User, Role, MinesweeperScore, MinesweeperStat,
    MinesweeperAchievement, UserMinesweeperAchievement
)

from forms import (
    LoginForm, UserAddForm, CSRFProtection, UserEditForm
)

from minesweeper import (
    MINESWEEPER_LEVELS, calc_minesweeper_achievements
)

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


###### Flask-login redirect target check ######
# Credit to:
# https://web.archive.org/web/20120517003641/http://flask.pocoo.org/snippets/62/

def is_safe_url(target):
    """ Check if a URL is safe for redirecting to """

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


###### Flask-login setup ######

# login_manager = LoginManager()
# login_manager.init_app(app)

# login_manager.login_view = 'login'
# login_manager.login_message = 'Please log in to view this page.'
# login_manager.login_message_category = 'danger'

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)


###### User signup/login/logout ######

@app.before_request
def add_user_to_g():
    """ Add current user to Flask global if logged in """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_only_form():
    """ Add a CSRF-only form so every route can use it """

    g.csrf_form = CSRFProtection()


def login_user(user):
    """ Log in user """

    session[CURR_USER_KEY] = user.id


def logout_user():
    """ Log out user """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    """ Handle showing and submission of signup form. """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()

    if form.validate_on_submit():
        username = form.username.data
        display_name = form.display_name.data
        email = form.email.data

        try:
            user = User.signup(
                username=username,
                password=form.password.data,
                display_name=display_name,
                email=email
            )

            db.session.commit()

        except IntegrityError as e:
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

            if not is_unique_username:
                flash('Username already taken.', 'danger')
            if not is_unique_display_name:
                flash('Display name already taken.', 'danger')
            if not is_unique_email:
                flash('E-mail already taken.', 'danger')

            return render_template('users/signup.html', form=form)

        login_user(user)

        flash('Successfully signed up.', 'success')
        return redirect(url_for('homepage'))

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    """ Handle showing and submission of login form. """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username=form.username.data,
            password=form.password.data
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
def logout():
    """ Handle logout of user and redirect to home page """

    form = g.csrf_form

    if form.validate_on_submit():
        logout_user()

    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.post('/guestlogin')
def login_guest():
    """ Log user in to guest account """

    form = g.csrf_form

    if form.validate_on_submit():
        user = (User.query
            .filter(User.username == 'guest')
            .first())

        if user:
            login_user(user)
            flash('Logged in as guest.', 'success')
            return redirect(url_for('homepage'))

    flash('Something went wrong. Please sign up to proceed.', 'danger')
    return redirect(url_for('signup'))


###### General user routes ######

@app.get('/users')
def list_users():
    """ List all users, with an optional filter from the query string. """

    if not g.user:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login', next=request.path))

    search = request.args.get('q')

    if not search:
        users = User.query.order_by(User.display_name).all()
    else:
        users = (User.query
            .filter(User.display_name.like(f"%{search}%"))
            .order_by(User.display_name)
            .all())

    return render_template('users/index.html', users=users)


@app.get('/users/<int:user_id>')
def show_user_profile(user_id):
    """ Show user profile page. """

    if not g.user:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login', next=request.path))

    minesweeper_achievements = (db.session
        .query(MinesweeperAchievement)
        .join(UserMinesweeperAchievement)
        .filter(UserMinesweeperAchievement.user_id == user_id)
        .order_by(MinesweeperAchievement.id)
        .all()
    )

    minesweeper_stats = MinesweeperStat.query.get(user_id)

    return render_template(
        'users/detail.html',
        user = User.query.get_or_404(user_id),
        minesweeper_achievements = minesweeper_achievements,
        minesweeper_stats = minesweeper_stats
    )


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """ Show and handle submission of user edit form """

    if not g.user:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))

    if g.user.id != user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('homepage'))

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('show_user_profile', user_id = user_id))

    return render_template('/users/edit.html', form=form)


@app.post('/users/<int:user_id>/delete')
def delete_user(user_id):
    """Delete user.

    Redirect to signup page.
    """

    if not g.user:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))

    if g.user.id != user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('homepage'))

    form = g.csrf_form

    if form.validate_on_submit():
        logout_user()

        User.query.filter(User.id == g.user.id).delete()
        db.session.commit()

        flash('User successfully deleted. See you again!', 'success')
        return redirect(url_for('signup'))

    flash('Unauthorized access.', 'danger')
    return redirect('/')


###### Minesweeper game routes ######

@app.get('/games/minesweeper')
def show_minesweeper_game():
    """ Show minesweeper game to user """

    if not g.user:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login', next=request.path))

    return render_template('minesweeper.html')


###### Minesweeper game API ######

@app.get('/api/minesweeper/scores')
def get_minesweeper_scores():
    """ Get minesweeper scores from database. Top 20 for each difficulty. """

    if not g.user:
        return jsonify(error="Please log in to access this endpoint."), 401

    scores = {}

    for level in MINESWEEPER_LEVELS:
        scores_for_level = MinesweeperScore.get_scores_for_level(level, 20)
        scores[level] = [score.serialize() for score in scores_for_level]

    return jsonify(scores=scores)


@app.post('/api/minesweeper/scores')
def submit_minesweeper_score():
    """ Submit minesweeper score to database.
    Expects JSON format data with fields for time and level.
    """

    if not g.user:
        return jsonify(error="Please log in to access this endpoint."), 401

    new_score = MinesweeperScore(
        user_id = g.user.id,
        time = request.json['time'],
        level = request.json['level']
    )
    db.session.add(new_score)
    db.session.commit()

    serialized = new_score.serialize()

    return (jsonify(score=serialized), 201)


@app.post('/api/minesweeper/stats')
def submit_minesweeper_stats():
    """ Submit minesweeper stats to database.
    Calculates achievements and sends back in JSON response.
    """

    if not g.user:
        return jsonify(error="Please log in to access this endpoint."), 401

    data = request.json
    curr_stat = MinesweeperStat.query.get(g.user.id)

    if not curr_stat:
        curr_stat = MinesweeperStat(user_id = g.user.id)

        db.session.add(curr_stat)
        db.session.commit()

    curr_stat.games_played += data['games_played']
    curr_stat.games_won += data['games_won']
    curr_stat.beginner_games_won += data['beginner_games_won']
    curr_stat.intermediate_games_won += data['intermediate_games_won']
    curr_stat.expert_games_won += data['expert_games_won']
    curr_stat.time_played += data['time_played']
    curr_stat.cells_revealed += data['cells_revealed']
    curr_stat.win_streak = (
        (curr_stat.win_streak + 1)
        if data['games_won'] else
        0
    )
    curr_stat.last_played_at = data['last_played_at']

    db.session.add(curr_stat)
    db.session.commit()

    new_achievements = calc_minesweeper_achievements(g.user, data)
    g.user.minesweeper_achievements.extend(new_achievements)

    db.session.commit()

    serialized = [a.serialize() for a in new_achievements]
    return jsonify(
        stats=curr_stat.serialize(),
        new_achievements=serialized
    )


###### GENERAL ROUTES ######

@app.get('/')
def homepage():
    """ Show the home page """

    return redirect(url_for('show_games_page'))


@app.get('/games')
def show_games_page():
    """ Show the games page that lists all available games """

    return render_template('games.html')


###### ERROR HANDLING ROUTES ######

@app.errorhandler(404)
def page_not_found(e):
    """ Show the 404 page """

    return render_template('404_not_found.html')


#TODO:
# Restructure using flask blueprints
# Testing with flask-login
# Testing 404 route