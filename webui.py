import gevent.monkey ; gevent.monkey.patch_all()
import flask
import gevent.wsgi
import os
import werkzeug.serving

from database import db_session, db_init
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from forms import LoginForm, SignupForm
from time import sleep


def create_app():
    app = flask.Flask(__name__)
    app.config.update(
        SECRET_KEY='secret',
    )

    Bootstrap(app)
    Moment(app)

    return app


app = create_app()
db = SQLAlchemy(app)


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
        print(form.username.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        flask.redirect('/')
    return flask.render_template('submit.html', form=form)


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
    #return flask.Response(message())


@app.route('/test')
def page():
    return flask.render_template('sse.html')


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
    http_server = gevent.wsgi.WSGIServer(('', 5000), app)
    http_server.serve_forever()


if __name__ == "__main__":
    run_server()
