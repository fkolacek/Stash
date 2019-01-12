#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#

import logging


from flask import Flask, request, make_response, jsonify, render_template, send_from_directory
from git import Repo

from .exception import StashException, StashDatabaseException
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
        self.app.add_url_rule('/detail/<path:path>', 'process_detail', self.process_detail)
        self.app.add_url_rule('/about', 'process_about', self.process_about)
        self.app.add_url_rule('/static/<path:path>', 'process_static', self.process_static)

        self.app.add_url_rule('/add', 'process_add', self.process_add, methods=['POST'])
        self.app.add_url_rule('/delete', 'process_delete', self.process_delete, methods=['POST'])
        self.app.add_url_rule('/repo', 'process_repo', self.process_repo, methods=['GET', 'POST'])
        self.app.add_url_rule('/repos', 'process_repos', self.process_repos)

    def run(self):
        logging.info('Starting application')
        self.app.run(**self.config['main'])

    def authorized(self, token):
        with StashDatabase(**self.config['database']) as db:
            auth = db.is_token(token)
        return auth

    def process_index(self):
        return render_template('index.html', web=self.config['web'])

    def process_detail(self, path):
        try:
            with StashDatabase(**self.config['database']) as db:
                if not db.is_repo(path):
                    return render_template('index.html', web=self.config['web'], error='Not found')

                repo = db.get_repo(path)

                return render_template('detail.html', web=self.config['web'], repo=repo)
        except StashDatabaseException as e:
            logging.error(e)
            return make_response('Internal Server Error', 500)

    def process_about(self):
        return render_template('about.html', web=self.config['web'])

    def process_static(self, path):
        return send_from_directory('static', path)

    def process_add(self):
        if not self.authorized(request.form.get('token')):
            return make_response('Unauthorized', 401)

        name = request.form.get('name')
        t = request.form.get('type')
        remote = request.form.get('remote')
        description = request.form.get('description')

        if not all([name, t, remote]):
            return make_response('Invalid request', 400)

        try:
            with StashDatabase(**self.config['database']) as db:
                db.add_repo(name, t, remote, description)

            return make_response('Success', 200)
        except StashDatabaseException as e:
            logging.error(e)
            return make_response('Internal Server Error', 500)

    def process_delete(self):
        logging.info('Processing delete')

        if not self.authorized(request.form.get('token')):
            return make_response('Unauthorized', 401)

        id_ = request.form.get('id')

        if not id_:
            return make_response('Invalid request', 400)

        try:
            with StashDatabase(**self.config['database']) as db:
                db.del_repo(id_)

            return make_response('Success', 200)
        except StashDatabaseException as e:
            logging.error(e)
            return make_response('Internal Server Error', 500)

    def process_repo(self):
        logging.info('Processing repo')

        id_ = request.args.get('id') if request.method == 'GET' else request.form.get('id')

        try:
            with StashDatabase(**self.config['database']) as db:
                repo = db.get_repo(id_)

            return jsonify(repo)
        except StashDatabaseException as e:
            logging.error(e)
            return make_response('Internal Server Error', 500)

    def process_repos(self):
        logging.info('Processing repos')

        try:
            with StashDatabase(**self.config['database']) as db:
                repos = db.get_repos()

            return jsonify(repos)
        except StashDatabaseException as e:
            logging.error(e)
            return make_response('Internal Server Error', 500)

