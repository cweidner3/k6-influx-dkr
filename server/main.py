import flask

from server.protected import bp_restrict

app = flask.Flask('server')
app.register_blueprint(bp_restrict)
