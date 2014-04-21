from bottle import route, run


@route('/hello')
def hello():
    return "<h1>Hello, world!</h1>"
