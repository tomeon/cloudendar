import gapi
import httplib2
import os
import random
import string
import utility

from database import db_session, db_init
from dateutil import parser
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.ext.bootstrap import Bootstrap, WebCDN
from flask.ext.login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required
)
from flaskext.kvsession import KVSessionExtension
from flask.ext.moment import Moment
from flask.ext.socketio import SocketIO
from forms import SearchForm
from models import User
from oauth2client.client import (
    FlowExchangeError,
    flow_from_clientsecrets,
)
from simplekv.memory import DictStore


APPLICATION_NAME = 'cloudendar'


if not os.path.exists('data'):
    os.mkdir('data')

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

    # Initialize Bootstrap environment
    Bootstrap(app)
    app.extensions['bootstrap']['cdns'].update(cdns)

    # See the simplekv documentation for details
    store = DictStore()
    # This will replace the app's session handling
    KVSessionExtension(store, app)

    return app


# Create app
app = create_app()

# Initialize nice formatting of dates and times in Jinja2 templates
moment = Moment(app)

# Initialize SocketIO environment
socketio = SocketIO(app)

# Create LoginManager
# See https://flask-login.readthedocs.org/en/latest/#configuring-login
# for Flask-Login API details.
lm = LoginManager()
# Configure the message that gets flashed when the user needs to log in.
lm.login_message = u'Please log in with your Google+ account.'
lm.login_message_category = 'info'

# Intialize app to handle logins
lm.init_app(app)

# Start scoped database session
db_init()


# Inject template variables and functions into ALL templates
@app.context_processor
def inject_variables():
    # This will be passed to a <meta /> tag that defines the permissions for the
    # Google+ Sign In button, which requires a space-delimited list of scopes.
    # See: https://developers.google.com/+/web/signin/reference#button_attr_scope
    scope = ' '.join(gapi.APP_SCOPE)
    return dict(CLIENT_ID=gapi.WEB_CLIENT_ID,
                SCOPE=scope,
                APPLICATION_NAME=APPLICATION_NAME)


# Teardown hook -- closed on exit
@app.teardown_appcontext
def shutdown_db_session(exception=None):
    db_session.remove()


@lm.user_loader
def load_user(onid):
    return User.query.filter(User.onid == str(onid)).first()


@app.route('/login')
def login():
    # If the user is already authenticated, redirect to home page
    if 'credentials' in session:
        return redirect(url_for('index'))

    # Otherwise, create CSRF token and initiate authorization flow
    state = make_state()
    return render_template('login.html',
                           STATE=state)


@app.route('/')
#@login_required
def index():
    if session.get('credentials') is None:
        return redirect(url_for('login'))

    form = SearchForm()
    # Save the CSRF token in the session so we can get it from the '/find' route
    session['csrf_token'] = form.csrf_token.current_token
    return render_template('index.html',
                           form=form)


@app.route('/query', methods=['POST'])
@login_required
def run_query():
    try:
        # Grab the JSON data from the client
        payload = request.get_json()

        # Create a list of dictionaries containing the users' names
        names = []
        for key, value in payload.iteritems():
            names.append(value)

        # Request ONIDs from the PHP script on Flip
        onids = utility.request_onids(names)
        return jsonify(onids=onids)

    except Exception as e:
        return jsonify(exception=str(e), status=400)


@app.route('/find', methods=['POST'])
@login_required
def find_times():
    stored_csrf_token = session.get('csrf_token')

    try:
        # Grab the JSON data from the client
        payload = request.get_json()

        # Confirm that the request is coming from the right client
        csrf_token = payload.get('csrf_token')
        if csrf_token is None or csrf_token != stored_csrf_token:
            return jsonify(msg='Access unauthorized', status=401)

        person = session.get('person')
        credentials = session.get('credentials')
        if person is None or credentials is None:
            return jsonify(msg='You must be logged in to access this page', status=401)

        # Ugh.  Clearly I need to have thought harder about the details of
        # transferring data between the server and client...
        usernames = []
        users = []
        usermap = {}
        for user, info in payload.get('users').iteritems():
            onid = info.get('onid')
            usernames.append(onid)
            users.append(user)
            usermap[onid] = user
        if len(usermap) == 0:
            return jsonify(msg='No results', status=200)

        start_time = parser.parse(payload.get('start'))
        end_time = parser.parse(payload.get('end'))

        # Check what kind of search we're doing.  If the value of 'search_type'
        # is 'duration', we set the argument 'whole' to 'True'.
        whole = False
        duration = False
        search_type = payload.get('search_type')
        if search_type == 'whole':
            whole = True
        elif search_type == 'duration':
            duration = True


        # Instantiate a CalendarAPI object for interacting with the Google Calendar API
        gcal = gapi.CalendarAPI(is_cli_app=False, credentials=credentials)

        # Get the list of ranges during which the various users are free
        free_ranges = gcal.get_ranges_overlaps(users=usernames,
                                               start_time=start_time,
                                               end_time=end_time,
                                               whole=whole,
                                               duration=duration,
                                               convert_func=utility.moment_format_date)

        # Google's Calendar API returns calendars keyed to emails rather than
        # usernames, and that propagates through many of the functions defined
        # on the CalendarAPI class.  Therefore, in order to work with the
        # JavaScript in search.js, we've got to strip off the email postfix.
        for item in free_ranges:
            free_users = map(lambda onid: usermap.get(utility.strip_postfix(onid)), item.get('onids'))
            item['free_users'] = free_users
            item['busy_users'] = [user for user in users if user not in free_users]

        return jsonify(free_ranges=free_ranges)

    except Exception as e:
        return jsonify(exception=str(e), status=400)


# This function, as well as the 'disconnect' function below, were adapted from
# the Google Python starter application available at:
# https://developers.google.com/+/quickstart/python
@app.route('/connect', methods=["POST"])
def connect():
    # TODO delete
    """Exchange the one-time authorization code for a token and
    store the token in the session."""
    # Pull out the state that we saved to authenticate request
    state = session.get('state')

    # If we didn't receive back the 'state' token sent from login(),
    # bail out.
    if state != request.args.get('state') or state is None:
        #response = make_response(json.dumps('Invalid state parameter.'), 401)
        response = jsonify(msg='Invalid state parameter.', status=401)
        return response

    # Delete the state token
    del session['state']

    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(gapi.WEB_CLIENT_SECRET_FILE, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError as e:
        response = jsonify(msg='Failed to upgrade the authorization code.', status=401, exception=str(e))
        return response

    # An ID Token is a cryptographically-signed JSON object encoded in base 64.
    # Normally, it is critical that you validate an ID Token before you use it,
    # but since you are communicating directly with Google over an
    # intermediary-free HTTPS channel and using your Client Secret to
    # authenticate yourself to Google, you can be confident that the token you
    # receive really comes from Google and is valid. If your server passes the
    # ID Token to other components of your app, it is extremely important that
    # the other components validate the token before using it.
    gplus_id = credentials.id_token['sub']

    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = jsonify(msg='Current user is already connected.', status=200, redirect=url_for('index'))
        return response

    person = gapi.PeopleAPI(is_cli_app=False, credentials=credentials)

    # Check whether the user is already in our database; if not, add them.
    onid = person.get_username()
    user = User.query.filter(User.onid == onid).first()
    if user is None:
        email = person.get_email()
        fname, mname, lname = person.get_names()
        user = User(onid=onid, fname=fname, mname=mname, lname=lname, email=email, credentials=credentials)
        db_session.add(user)
        db_session.commit()

    # Call the Flask-Login login_user function to set up user login session
    login_user(user)

    # Store the access token and other items in the session for later use
    session['credentials'] = credentials
    session['gplus_id'] = gplus_id
    session['username'] = onid
    session['person'] = person

    # Flash a success message
    flash("Logged in successfully.")

    return jsonify(msg='Successfully connected user.', status=200, redirect=url_for('index'))


@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Revoke current user's token and reset their session."""

    # Only disconnect a connected user.
    credentials = session.get('credentials')
    if credentials is None:
        response = jsonify(msg='Current user not connected.', status=401)
        return response

    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = "https://accounts.google.com/o/oauth2/revoke?token={0}".format(access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[0]

    if result.get('status') == '200':
        # Reset the user's session.
        del session['credentials']
        flash('Successfully revoked your permissions.')
        response = jsonify(msg='Successfully disconnected.', status=200, redirect=url_for('index'))
        return response
    else:
        # For whatever reason, the given token was invalid.
        flash('Could not revoke permission, please visit your Google account console.', 'warning')
        response = jsonify(msg='Failed to revoke token for given user.', status=400, redirect=url_for('index'))
        return response


# TODO: implement destruction of JUST the session and other identifiers.
# This route cannot be accessed by GET request.  It has to be done by POST,
# which is currently handled in src/templates/interpreted_js/gplus, in
# the 'logoutUser()' function
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Delete the session
    logout_user()
    session.destroy()
    return jsonify(msg="Logged out successfully", status=200, redirect=url_for('login'))


@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html',
                           ERROR_CODE=e,
                           ERROR_MSG="You do not have the necessary permissions to access this resource"), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',
                           ERROR_CODE=e,
                           ERROR_MSG="That page does not exist on this server"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html',
                           ERROR_CODE=e,
                           ERROR_MSG="An unknown error occurred"), 500


def make_state():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return state


if __name__ == "__main__":
    app.debug = True
    socketio.run(app)
