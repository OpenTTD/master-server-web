import click
import datetime
import flask

from .click import click_additional_options

_api_url = None


@click_additional_options
@click.option(
    "--api-url",
    help="Master Server API URL.",
    default="https://api.master.openttd.org",
    show_default=True,
    metavar="URL",
)
def click_urls(api_url):
    global _api_url
    _api_url = api_url


def template(*args, **kwargs):
    messages = kwargs.setdefault("messages", [])
    if "message" in kwargs:
        messages.append(kwargs["message"])
    if "message" in flask.request.args:
        messages.append(flask.request.args["message"])
    kwargs["globals"] = {
        "copyright_year": datetime.datetime.utcnow().year,
    }

    response = flask.make_response(flask.render_template(*args, **kwargs))
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


def api_host():
    return _api_url


def redirect(*args, **kwargs):
    return flask.redirect(flask.url_for(*args, **kwargs))
