import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from .blueprints.main import main_bp
from .blueprints.user import user_bp
from .blueprints.auth import auth_bp
from .extensions import bootstrap, db, mail, moment, dropzone, csrf, avatar, login_manager
from .settings import config
from .models import Role, User, Photo, Tag, Comment
from celery import Celery


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('albumy')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandler(app)
    register_shell_context(app)
    register_template_context(app)

    return app


def make_celery(app=None):
    app = app or create_app()
    celery = Celery('albumy', broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    dropzone.init_app(app)
    csrf.init_app(app)
    avatar.init_app(app)
    login_manager.init_app(app)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Photo=Photo, Tag=Tag, Comment=Comment)


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_template_context(app):
    pass


def register_errorhandler(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    def init():
        """Initialize Albumy."""
        click.echo('Initializing the database.')
        db.create_all()

        click.echo('Done.')

    @app.cli.command()
    @click.option('--user', default=10, help='Quantity of users, default is 10.')
    @click.option('--photo', default=30, help='Quantity of photos, default is 500.')
    @click.option('--tag', default=20, help='Quantity of tags, default is 500.')
    @click.option('--comment', default=100, help='Quantity of comments, default is 500.')
    def forge(user, photo, tag, comment):
        """Generate fake data."""
        from .fakes import fake_admin, fake_comment, fake_photo, fake_tag, fake_user

        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.init_role()
        click.echo('Generating the administrator...')
        fake_admin()
        click.echo('Generating {} users...'.format(user))
        fake_user(user)
        click.echo('Generating {} tags...'.format(tag))
        fake_tag(tag)
        click.echo('Generating {} photos...'.format(photo))
        fake_photo(photo)
        click.echo('Generating {} comments...'.format(comment))
        fake_comment(comment)
        click.echo('Done.')
