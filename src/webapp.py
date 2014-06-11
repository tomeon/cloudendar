#import gevent.monkey; gevent.monkey.patch_all()
import flask
import gapi
import gevent.wsgi
import httplib2
import os
import pprint
import re
import random
import requests
import string
import time
import urllib
import utility
import werkzeug.serving

from database import db_session, db_init
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import (
    Flask,
    url_for,
    redirect,
    render_template,
    g,
    request,
    flash,
    session,
)
from flask.ext.bootstrap import Bootstrap, WebCDN
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flaskext.kvsession import KVSessionExtension
from flask.ext.moment import Moment
from flask.ext.socketio import SocketIO, emit
from forms import EventForm, LoginForm, SearchForm, SignupForm
from models import User, Event
from simplekv.memory import DictStore
from wtforms import SelectField
from wtforms.validators import InputRequired
from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, MultifieldParser


APPLICATION_NAME = 'cloudendar'


schema = Schema(name=TEXT(stored=True), value=TEXT(stored=True))
if not os.path.exists('data'):
    os.mkdir('data')


ix = index.create_in('data', schema=schema, indexname="dummy_choices")
#if not index.exists_in('data', indexname="dummy_choices"):
#    ix = index.create_in('data', schema=schema, indexname="dummy_choices")
#else:
#    ix = index.open_dir('data', indexname="dummy_choices")


dummy_users = ["Alice", "Bob", "Carol", "Del", "Edith", "Frank", "Gertrude",
                "Hiram", "Ilse", "Jon", "Karen", "Lon", "Matilda", "Nick", "Oprah", "Pete",
                "Quinn", "Rob", "Sarah", "Ted", "Ursula", "Von", "Wendy",
               "Xavier", "Yolanda", "Zane"]
dummy_choices = [(unicode(e), unicode(e)) for e in dummy_users]
dummy_onids = [{"name": unicode(e), "onid": (e)} for e in dummy_users]

selected_users = []


def index_choices(ix, choices):
    with ix.writer() as writer:
        for name, value in choices:
            writer.add_document(name=name, value=value)


def search_index(ix, term):
    qp = MultifieldParser(['name', 'value'], schema=schema)
    q = qp.parse(term)
    with ix.searcher() as searcher:
        return searcher.search(q, limit=20)


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY='secret',
    )

    cdns = {
        "jquery": WebCDN("//ajax.googleapis.com/ajax/libs/jquery/1.11.0/"),
        "jquery-ui": WebCDN("//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/"),
        "socket.io": WebCDN("//cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/"),
        "typeahead": WebCDN("//cdnjs.cloudflare.com/ajax/libs/typeahead.js/0.10.2/"),
        "handlebars": WebCDN("//cdnjs.cloudflare.com/ajax/libs/handlebars.js/2.0.0-alpha.2/"),
    }

    Moment(app)

    Bootstrap(app)
    app.extensions['bootstrap']['cdns'].update(cdns)

    # See the simplekv documentation for details
    store = DictStore()
    # This will replace the app's session handling
    KVSessionExtension(store, app)

    index_choices(ix, dummy_choices)

    return app


app = create_app()
socketio = SocketIO(app)
lm = LoginManager()
lm.init_app(app)
db_init()
flow = gapi.get_web_server_flow()


# Hooks
@app.teardown_appcontext
def shutdown_db_session(exception=None):
    # TODO handle revoking credentials more elegantly
    # revoke_credentials()

    db_session.remove()


@lm.user_loader
def load_user(onid):
    return User.query.get(str(onid))


@app.route('/')
def index():
    # Establish a CSRF state token
    # if 'state' not in session:
    #    state = make_state()
    state = make_state()


    return render_template('index.html',
                           CLIENT_ID=gapi.WEB_CLIENT_ID,
                           STATE=state,
                           APPLICATION_NAME=APPLICATION_NAME)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/login')
def login():
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    error = request.args.get('error')
    post_flow = gapi.get_web_server_flow_post_auth()

    # TODO add guard so that user can't access this without first authorizing.
    if error:
        flash("Cannot proceed without authorization", 'warning')
    else:
        credentials = None
        if code and post_flow:
            post_flow.redirect_uri = request.base_url
            try:
                credentials = flow.step2_exchange(code)
                pprint.pprint(vars(credentials))
            except Exception as e:
                print("Unable to get an access token because: {0}".format(e.message))

            me = gapi.PeopleAPI(is_cli_app=False, credentials=credentials)
            print("USERINFO {0}".format(pprint.pformat(me.get_userinfo())))
            print("USERNAMES: {0}".format(me.get_usernames()))
            print("STATE: {0}".format(request.args.get('state')))

            session['credentials'] = credentials

        else:
            flash("Unable to authorize Google API", 'warning');

    return redirect(url_for('index'))


@app.route('/signup', methods=["GET", "POST"])
def signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        flash("Success!")
        session['username'] = form.username.data
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/add', methods=["GET", "POST"])
def event_form():
    form = EventForm()
    if form.validate_on_submit():
        flash("Success!")
        print(form.start.data)
        print(form.end.data)
        return redirect(url_for('index'))
    return render_template('search.html', form=form)


@app.route('/results')
def print_results():
    res = search_index(ix, "o")
    pprint.pprint(res)
    pprint.pprint(ix)
    for item in res:
        print(item)
    print(res)
    return "Hello, world!"


@app.route('/search', methods=["GET", "POST"])
def search_form():
    form = SearchForm()
    if form.validate_on_submit():
        flash("Success!")
        for field in form:
            print(field)
        return redirect(url_for('index'))
    for field in form:
        print(field)
    return render_template('search.html', form=form)


@app.route('/test')
def testbed():
    me = utility.request_onid("matt", "schreiber")
    gcal = gapi.CalendarAPI(credentials=credentials)
    now = datetime.now()
    soon = now + relativedelta(weeks=+1)
    free = gcal.query_calendars_free([me])
    free = gcal.query_calendars_free([me], now, soon)
    print(free)
    return me


@app.route('/me')
def return_me():
    me = utility.request_onid("matt", "schreiber")
    gcal = gapi.CalendarAPI()
    now = datetime.now()
    soon = now + relativedelta(weeks=+1)
    free = gcal.query_calendars_free([me])
    free = gcal.query_calendars_free([me], now, soon)
    print(free)
    #free_times = free.get('schreibm@onid.oregonstate.edu').get('free')[0]
    free_times = free.get(me + gapi.EMAIL_POSTFIX).get('free')[0]
    start = free_times.get('start')
    end = free_times.get('end')
    start = utility.pretty_date(start)
    end = utility.pretty_date(end)
    return "{} is free from {} to {}".format(me, start, end)


@socketio.on('connect', namespace='/search')
def create_search_list():
    emit('onids', {'data': dummy_onids})


@socketio.on('search', namespace='/search')
def get_possibles(msg):
    # Pull ONID email address out of msg argument
    onid = msg.get('data')

    if onid is None:
        ret = "Empty email"

    else:
        # Try to grab the prefix of the email address
        match = re.match(r'(.+)@.+', onid)
        user = match.group(1)

        if user is None:
            ret = "Invalid email"

        # Filter matches from list of fake users
        hits = filter(lambda e: e == user, dummy_users)

        # Set returned message
        if len(hits) > 0:
            ret = "Found match: {0}".format(hits[0])
        else:
            ret = "No such user"

    # Send data back down the socket
    emit('result', {'data': ret})


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
        flash("Success!")
        print(form.start.data)
        print(form.end.data)
        return redirect(url_for('index'))
    return render_template('search.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# TODO better exception handling
def revoke_credentials(credentials=None):
    credentials = credentials or session.get('credentials')
    http = httplib2.Http()
    try:
        credentials.revoke(http)
    except:
        print("Failed to revoke credentials")


def login_user(onid=None, credentials=None):
    credentials = credentials or session.get('credentials')
    if onid is None:
        me = gapi.PeopleAPI(is_cli_app=False, credentials=credentials)
        userinfo = me.get_userinfo()


def make_state():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return state


if __name__ == "__main__":
    app.debug = True
    socketio.run(app)
