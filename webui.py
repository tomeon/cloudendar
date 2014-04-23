import localpath
from modules import bottle


app = application = bottle.Bottle()


@app.route('/login')
def login():
    return ""


@app.route('/')
def index():
    return "<h1>Hello, world!</h1>"


if __name__ == "__main__":
    bottle.run(app, host='localhost', port=8080, reloader=True, debug=True)
