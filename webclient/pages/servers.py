import time

from collections import defaultdict
from datetime import datetime

from ..app import app
from ..api import api_get
from ..helpers import (
    redirect,
    template,
)

LANGUAGES = {
    0: "All",
    1: "English",
    2: "German",
    3: "French",
    4: "Brazillian",
    5: "Bulgarian",
    6: "Chinese",
    7: "Czech",
    8: "Danish",
    9: "Dutch",
    10: "Esperanto",
    11: "Finnish",
    12: "Hungarian",
    13: "Icelandic",
    14: "Italian",
    15: "Japanese",
    16: "Korean",
    17: "Lithuanian",
    18: "Norwegian",
    19: "Polish",
    20: "Portuguese",
    21: "Romanian",
    22: "Russian",
    23: "Slovak",
    24: "Slovenian",
    25: "Spanish",
    26: "Swedish",
    27: "Turkish",
    28: "Ukranian",
    29: "Afrikaans",
    30: "Croatian",
    31: "Catalan",
    32: "Estonian",
    33: "Galician",
    34: "Greek",
    35: "Latvian",
}
MAPSETS = {
    0: "Temperate",
    1: "Arctic",
    2: "Tropical",
    3: "Toyland",
}
DAYS_IN_MONTH = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}
# Expire the cache after 2 minutes; the API caches for 5 minutes, so there
# is a small chances you won't receive an update for ~7 minutes when hitting
# constant refresh.
CACHE_EXPIRE_TIME = 60 * 2

_server_list_cache = None
_server_entry_cache = defaultdict(lambda: None)


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _date_to_string(date):
    # Year determination in multiple steps to account for leap years. First do
    # the large steps, then the smaller ones.

    # There are 97 leap years in 400 years.
    year = 400 * (date // (365 * 400 + 97))
    remainder = date % (365 * 400 + 97)

    if remainder >= 365 * 100 + 25:
        # There are 25 leap years in the first 100 years after every 400th
        # year, as every 400th year is a leap year.
        year += 100
        remainder -= 365 * 100 + 25

        # There are 24 leap years in the next couple of 100 years.
        year += 100 * (remainder // (365 * 100 + 24))
        remainder = remainder % (365 * 100 + 24)

    if remainder >= 365 * 4 and not is_leap_year(year):
        # The first 4 year of the century are not always a leap year.
        year += 4
        remainder -= 365 * 4

    # There is 1 leap year every 4 years.
    year += 4 * (remainder // (365 * 4 + 1))
    remainder = remainder % (365 * 4 + 1)

    # The last (max 3) years to account for; the first one can be, but is not
    # necessarily a leap year.
    while remainder >= (366 if is_leap_year(year) else 365):
        remainder -= 366 if is_leap_year(year) else 365
        year += 1

    # Skip the 29th of February in non-leap years.
    if not is_leap_year(year) and remainder >= 31 + 29 - 1:
        remainder += 1

    for month, days in DAYS_IN_MONTH.items():
        if remainder < days:
            break
        remainder -= days
    day = remainder + 1

    return f"{year}-{month:02d}-{day:02d}"


def _fix_server_info(server):
    # Set the server_id to the one based on the IPv4 or, if not available, to
    # the IPv6 variant.
    server["server_id"] = getattr(server, "ipv4", server["ipv6"])["server_id"]

    # Make dates human readable.
    server["info"]["start_date"] = _date_to_string(server["info"]["start_date"])
    server["info"]["game_date"] = _date_to_string(server["info"]["game_date"])
    server["time_first_seen"] = (
        datetime.utcfromtimestamp(server["time_first_seen"]).strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    )
    server["time_last_seen"] = (
        datetime.utcfromtimestamp(server["time_last_seen"]).strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    )


def _split_version(raw_version):
    """
    For official versions we control the format; for patchpacks we do not. So
    we are guestimating a bit here what is most likely happening. If it fails,
    we just fall back to sorting by string.
    """

    if "-" in raw_version:
        version, _, extra = raw_version.partition("-")
    else:
        version = raw_version
        extra = "stable"

    # Check if this is most likely an official release and sort it correctly.
    version_parts = version.split(".")
    if len(version_parts) == 3:
        return [int(p) for p in version_parts] + [extra]

    # Check if this is a patchpack like jgrpp-0.31.0.
    version_parts = extra.split(".")
    if len(version_parts) == 3:
        return [int(p) for p in version_parts] + [version]

    # We did not recognize what this is, so just fall back to string comparison.
    return [0, 0, 0, raw_version]


def _sort_servers(servers):
    servers.sort(key=lambda x: _split_version(x["info"]["server_revision"]), reverse=True)


@app.route("/listing/<filter>")
def servers(filter):
    global _server_list_cache

    if _server_list_cache is None or time.time() > _server_list_cache["expire"]:
        data = api_get(("server",))
        for server in data["servers"]:
            _fix_server_info(server)

        _sort_servers(data["servers"])

        _server_list_cache = {
            "servers": data["servers"],
            "cached": data["expire"],
            "expire": time.time() + CACHE_EXPIRE_TIME,
        }

    servers = _server_list_cache["servers"]
    if filter != "all":
        servers = [server for server in servers if server["info"]["server_revision"].startswith(filter)]

    expire = datetime.utcfromtimestamp(_server_list_cache["cached"]).strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    clients = sum([server["info"]["clients_on"] for server in servers])
    servers_ipv4 = len([server for server in servers if "ipv4" in server])
    servers_ipv6 = len([server for server in servers if "ipv6" in server])

    return template(
        "server_list.html",
        servers=servers,
        expire=expire,
        clients=clients,
        servers_ipv4=servers_ipv4,
        servers_ipv6=servers_ipv6,
        filter=filter,
        languages=LANGUAGES,
        mapsets=MAPSETS,
    )


@app.route("/server/<server_id>")
def server_entry(server_id):
    global _server_entry_cache

    if _server_entry_cache[server_id] is None or time.time() > _server_entry_cache[server_id]["expire"]:
        data = api_get(("server", server_id))
        server = data["server"]
        if server is not None:
            _fix_server_info(server)

        _server_entry_cache[server_id] = {
            "server": server,
            "cached": data["expire"],
            "expire": time.time() + CACHE_EXPIRE_TIME,
        }

    server = _server_entry_cache[server_id]["server"]
    if server is None:
        return redirect("error", message="This server (no longer) exists")

    return template("server_entry.html", server=server, languages=LANGUAGES, mapsets=MAPSETS)
