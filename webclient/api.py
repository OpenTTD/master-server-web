import flask
import requests
import urllib

from .app import app
from .helpers import (
    api_host,
    redirect,
)


def api_call(method, path, params=None, json=None, session=None, return_errors=False):
    url = api_host() + "/" + "/".join(urllib.parse.quote(p, safe="") for p in path)
    headers = None
    if session and session.api_token:
        headers = {"Authorization": "Bearer " + session.api_token}

    error_response = redirect("error", message="API call failed; sorry for the inconvenience")
    try:
        r = method(url, params=params, headers=headers, json=json)

        success = r.status_code in (200, 201, 204)
        if not success:
            app.logger.warning("API failed: {} {}".format(r.status_code, r.text))

        if success:
            result = None
            try:
                result = r.json()
            except Exception:
                result = None
            if return_errors:
                return (result, None)
            else:
                return result
        elif r.status_code == 404:
            if return_errors:
                return (None, "Data not found")
            error_response = redirect("error", message="Data not found")
        elif r.status_code == 400 and path[0] == "server":
            error_response = redirect("error", message="Unknown server")
        elif return_errors:
            error = str(r.json().get("errors", "API call failed"))
            return (None, error)
    except Exception:
        # If anything failed we did not capture, return the latest error we
        # have to the caller.
        pass

    if not return_errors:
        flask.abort(error_response)

    return (None, "API call failed")


def api_get(*args, **kwargs):
    return api_call(requests.get, *args, **kwargs)
