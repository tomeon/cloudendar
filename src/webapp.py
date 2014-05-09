import gevent.monkey; gevent.monkey.patch_all()
import flask
import flask_sijax
import gevent.wsgi
import os
import pprint
import werkzeug.serving

from database import db_session, db_init
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.socketio import SocketIO, emit
from forms import EventForm, LoginForm, SearchForm, SignupForm
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


@flask_sijax.route(app, '/sijax')
def hello_sijax():
    def hello_handler(obj_response, hello_from, hello_to):
        obj_response.alert("Hello from %s to %s" % (hello_from, hello_to))
        obj_response.css('a', 'color', 'green')

    def goodbye_handler(obj_response):
        obj_response.alert("Goodbye, whoever you are")
        obj_response.css('a', 'color', 'red')

    if flask.g.sijax.is_sijax_request:
        flask.g.sijax.register_callback('say_hello', hello_handler)
        flask.g.sijax.register_callback('say_goodbye', goodbye_handler)
        return flask.g.sijax.process_request()

    return flask.render_template('hello.html')


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
    return flask.render_template('event.html', form=form)


@app.route('/search', methods=["GET", "POST"])
def search_form():
    form = SearchForm()
    if form.validate_on_submit():
        flask.flash("Success!")
        print(form.start.data)
        print(form.end.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('event.html', form=form)


@app.route('/source')
def sse_request():
    def message():
        counter = 0
        while counter <= 10:
            sleep(1)
            print("sent message {0}".format(counter))
            yield "data: %s\n\n" % counter
            counter += 1
    return flask.Response(message(), mimetype='text/event-stream')
    # return flask.Response(message())


@app.route('/test')
def page():
    return flask.render_template('sse.html')


@app.route('/printdb')
def print_db():
    print(db_session)
    return flask.redirect(flask.url_for('index'))


@app.route('/test_socketio')
def test_socketio():
    return flask.render_template('test.html')

@socketio.on('my event', namespace='/test')
def test_message(message):
    flask.session['receive_count'] = flask.session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': flask.session['receive_count']})


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    flask.session['receive_count'] = flask.session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': flask.session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    flask.session['receive_count'] = flask.session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': flask.session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    flask.session['receive_count'] = flask.session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': flask.session['receive_count']})


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    flask.session['receive_count'] = flask.session.get('receive_count', 0) + 1
    emit('my response',
        {'data': message['data'], 'count': flask.session['receive_count']},
        room=message['room'])


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


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
    socketio.run(app)
    #http_server = gevent.wsgi.WSGIServer(('', 5000), app)
    #http_server.serve_forever()


if __name__ == "__main__":
    run_server()
