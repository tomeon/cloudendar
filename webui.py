<<<<<<< HEAD:webui.py
import localpath
from modules import bottle

=======
from bottle import route, run
>>>>>>> parent of 9b5e49a... Cleaning up testing:app.py


<<<<<<< HEAD:webui.py

@app.route('/login')
def login():
    return ""


@app.route('/')
def index():
    return "<h1>Hello, world!</h1>"


if __name__ == "__main__":
    bottle.run(app, host='localhost', port=8080, reloader=True, debug=True)
=======
@route('/hello')
def hello():
    return "<h1>Hello, world!</h1>"
>>>>>>> parent of 9b5e49a... Cleaning up testing:app.py
