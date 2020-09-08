import flask

from ..app import app
from ..helpers import (
    redirect,
    template,
)


@app.route("/")
def root():
    return redirect("servers_all")


@app.route("/error")
def error():
    return template("error.html")


@app.route("/healthz")
def healthz_handler():
    response = flask.make_response("200: OK")
    response.headers["Content-Type"] = "text/plain"
    return response
