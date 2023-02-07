import os
from typing import Optional

import flask
import flask.logging

from server import cmd

APP_SECRET = os.environ.get('APP_SECRET', 'very-secret-phrase')

bp_restrict = flask.Blueprint('server', 'restrict')

def _handle_ingest():
    val = flask.request.args.get('secret')
    if val is None or val != APP_SECRET:
        return 'Unauthorized', 401


bp_restrict.before_request(_handle_ingest)


@bp_restrict.route('/run', methods=['POST'])
def run_load_tests():
    log = flask.logging.create_logger(flask.current_app)
    kwargs = {
        'name': flask.request.args.get('name')
    }
    if flask.request.files:
        files = flask.request.files
        log.info('Found files in request: %s', files.keys())
        script = flask.request.files['file'].stream.read()
    elif flask.request.data:
        log.info('Found data in request: %s', flask.request.data[:50])
        script = flask.request.get_data()
    else:
        return 'Must provide script in the body of the request', 400
    # log.info('Using script for tests: %s', script)
    status = cmd.run_k6(script, **kwargs)
    return 'OK', 202 if status is cmd.ReturnStatus.NO_ACTION else 201


@bp_restrict.route('/status', methods=['GET'])
def load_test_status():
    stat, code, last_run, metadata = cmd.get_status()
    if flask.request.accept_mimetypes.accept_json:
        jstat = {
            'lastRun': last_run,
            'code': code,
            'metadata': metadata,
            'message': stat,
        }
        return jstat, code
    return stat, code
