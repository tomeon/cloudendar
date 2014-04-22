import bottle
import sqlite3

app = application = bottle.Bottle()


@app.route('/login')
def login():
    return ""

@app.route('/')
def index():
    return "<h1>Hello, world!</h1>"


if __name__ == "__main__":
    bottle.run(host='localhost', port=9090)
