#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#

import logging


from flask import Flask, request, make_response, jsonify
from git import Repo

from .exception import StashException
from .config import StashConfig
from .database import StashDatabase


class Stash:

    config = None
    app = None

    def __init__(self, config_name='config.ini'):
        try:
            self.config = StashConfig(config_name)
            self.init_logging()
            self.init_app()

        except StashException as e:
            logging.fatal(e)
            raise

    def init_logging(self):
        level = logging.DEBUG if self.config['main']['debug'] else logging.INFO

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=level)

    def init_app(self):
        self.app = Flask(__name__.split('.')[0])

        self.app.add_url_rule('/', 'process_index', self.process_index)
        self.app.add_url_rule('/add', 'process_add', self.process_add, methods=['POST'])
        self.app.add_url_rule('/delete', 'process_delete', self.process_delete, methods=['POST'])
        self.app.add_url_rule('/repo', 'process_repo', self.process_repo, methods=['GET', 'POST'])
        self.app.add_url_rule('/repos', 'process)repos', self.process_repos)

    def run(self):
        logging.info('Starting application')
        self.app.run(**self.config['main'])

    def authorized(self, token):
        with StashDatabase(**self.config['database']) as db:
            auth = db.is_token(token)
        return auth

    def process_index(self):
        logging.info('Processing index')

        return make_response('This is private stash, there is nothing for you, go away!', 200)

    def process_add(self):
        if not self.authorized(request.form.get('token')):
            return make_response('Unauthorized', 401)

        name = request.form.get('name')
        type_ = request.form.get('type')
        remote = request.form.get('remote')
        description = request.form.get('description')

        if not all[name, type_, remote]:
            return make_response('Invalid request', 400)

        with StashDatabase(**self.config['database']) as db:
            db.add_repo(name, type_, remote, description)

        return make_response('Success', 200)

    def process_delete(self):
        logging.info('Processing delete')

        if not self.authorized(request.form.get('token')):
            return make_response('Unauthorized', 401)

        name = request.form.get('name')

        if not name:
            return make_response('Invalid request', 400)

        with StashDatabase(**self.config['database']) as db:
            db.del_repo(name)

        return make_response('Success', 200)

    def process_repo(self):
        logging.info('Processing repo')

        name = request.form.get('name')

        with StashDatabase(**self.config['database']) as db:
            repo = db.get_repo(name)

        return jsonify(repo)

    def process_repos(self):
        logging.info('Processing repos')

        with StashDatabase(**self.config['database']) as db:
            repos = db.get_repos()

        return jsonify(repos)
