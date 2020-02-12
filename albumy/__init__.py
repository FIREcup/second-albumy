import os

import click
from flask import Flask, render_template

from .blueprints.main import main_bp
from .extensions import bootstrap, db, mail, moment, dropzone, csrf, avatar
from .settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('albumy')
    app.config.from_object(config[config_name])

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    dropzone.init_app(app)
    csrf.init_app(app)
    avatar.init_app(app)


def register_blueprints(app):
    app.register_blueprint(main_bp)


def register_template_context(app):
    pass


def register_errorhandler(app):
    @app.errorhander(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhander(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhander(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhander(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


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
    def forge():
        """Generate fake data."""
        pass
