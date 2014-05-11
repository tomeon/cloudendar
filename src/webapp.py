import gevent.monkey; gevent.monkey.patch_all()
import flask
import flask_sijax
import gevent.wsgi
import os
import pprint
import time
import werkzeug.serving

from database import db_session, db_init
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
from forms import EventForm, LoginForm, SearchForm, SignupForm
from wtforms import SelectField
from wtforms.validators import InputRequired
from threading import Thread
from time import sleep


def create_app():
    sijax_path = os.path.join('.', os.path.dirname(__file__),
                              'static/lib/sijax')

    app = flask.Flask(__name__)
    app.config.update(
        SECRET_KEY='secret',
        SIJAX_STATIC_PATH=sijax_path,
        SIJAX_JSON_URL = '/static/lib/sijax/json2.js',
    )

    flask_sijax.Sijax(app)
    Bootstrap(app)
    Moment(app)

    return app


app = create_app()
socketio = SocketIO(app)
db_init()


# Hooks
@app.teardown_appcontext
def shutdown_db_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return flask.render_template('user.html', name=name)


@app.route('/login', methods=["GET", "POST"])
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        flask.flash("Success!")
        flask.session['username'] = form.username.data
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        flask.flash("Success!")
        flask.session['username'] = form.username.data
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('signup.html', form=form)


@app.route('/add', methods=["GET", "POST"])
def event_form():
    form = EventForm()
    if form.validate_on_submit():
        flask.flash("Success!")
        print(form.start.data)
        print(form.end.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('search.html', form=form)


@app.route('/search', methods=["GET", "POST"])
def search_form():
    form = SearchForm()
    if form.validate_on_submit():
        flask.flash("Success!")
        print(form.start.data)
        print(form.end.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('search.html', form=form)


dummy_choices = [(e, e) for e in ['Alice', 'Bob', 'Carol', 'Del', 'Edith', 'Frank',
                                  'Gertrude', 'Hiram', 'Ilse', 'Jon', 'Karen',
                                  'Lon', 'Matilda', 'Nick', 'Oprah', 'Pete',
                                  'Quinn', 'Rob', 'Sarah', 'Ted', 'Ursula',
                                  'Von', 'Wendy', 'Xavier', 'Zelda']]


def search_user(num):
    label = "User %d" % num;
    return SelectField(label,
                       validators=[InputRequired()],
                       choices=dummy_choices,
                       )


@app.route('/expand')
def expand_form(users=1):
    class ExpandForm(SearchForm):
        pass
    for user in range(1, users + 1):
        setattr(ExpandForm, "user%d" % user, search_user(user))
    form = ExpandForm()
    if form.validate_on_submit():
        flask.flash("Success!")
        print(form.start.data)
        print(form.end.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('search.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return flask.render_template('500.html'), 500


# This needs to be at the bottom of the file, just before 'if __name__ ...'
@werkzeug.serving.run_with_reloader
def run_server():
    app.debug = True
    #Thread(target=background_thread).start()
    socketio.run(app)
    #http_server = gevent.wsgi.WSGIServer(('', 5000), app)
    #http_server.serve_forever()


if __name__ == "__main__":
    run_server()
