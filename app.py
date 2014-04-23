import bottle
import sqlite3

# Enable debugging
bottle.debug(True)

# Automatically reload testing server
bottle.run(reloader=True)

app = application = bottle.Bottle()


@app.route('/login')
def login():
    return ""


@app.route('/')
def index():
    return "<h1>Hello, world!</h1>"


if __name__ == "__main__":
    bottle.run(app, host='localhost', port=8080)
