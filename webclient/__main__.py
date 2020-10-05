import click
import flask

from openttd_helpers.logging_helper import click_logging
from openttd_helpers.sentry_helper import click_sentry
from werkzeug import serving

from . import pages  # noqa
from .app import app
from .helpers import click_urls


# Patch the werkzeug logger to only log errors
def log_request(self, code="-", size="-"):
    if str(code).startswith(("2", "3")):
        return
    original_log_request(self, code, size)


original_log_request = serving.WSGIRequestHandler.log_request
serving.WSGIRequestHandler.log_request = log_request


@click.group(cls=flask.cli.FlaskGroup, create_app=lambda: app)
@click_logging
@click_sentry
@click_urls
def cli():
    pass


if __name__ == "__main__":
    cli(auto_envvar_prefix="WEBCLIENT")
