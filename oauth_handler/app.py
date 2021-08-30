import flask
from flask import Flask, request

from database.storage import Storage


def launch_oauth_handler_app(database: Storage, storage_name: str):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return flask.render_template('oauth_handler.html')

    @app.route('/token/')
    def token():
        try:
            token_value = request.args.get('value')
            database.set(storage_name, token_value)
        except Exception:
            raise RuntimeError("Server going down...")

        return 'Ok'

    @app.route('/kill/')
    def shutdown():
        raise RuntimeError("Server going down...")

    app.run()
    return app
