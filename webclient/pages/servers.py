import time

from collections import defaultdict
from datetime import datetime

from ..app import app
from ..api import api_get
from ..helpers import (
    redirect,
    template,
)

GAMESCRIPT_VERSION_NONE = 4294967295  # (int32)-1 as uint32
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
    # Make dates human readable.
    server["info"]["start_date"] = _date_to_string(server["info"]["start_date"])
    server["info"]["game_date"] = _date_to_string(server["info"]["game_date"])


def _split_version(raw_version):
    """
    For official versions we control the format; for patchpacks we do not. So
    we are guestimating a bit here what is most likely happening. If it fails,
    we just fall back to sorting by string.
    """

    if "-" in raw_version:
        version, *extra = raw_version.split("-")
        priority = 5
    else:
        version = raw_version
        extra = ["stable"]
        priority = 10

    # Check if this is most likely an official release and sort it correctly.
    version_parts = version.split(".")
    if len(version_parts) == 3 and all([p.isdecimal() for p in version_parts]):
        return [priority] + [int(p) for p in version_parts] + ["official"] + ["-".join(extra)]

    # Check if this is a patchpack like jgrpp-0.31.0.
    version_parts = extra[0].split(".")
    if len(version_parts) == 3 and all([p.isdecimal() for p in version_parts]):
        return [priority] + [int(p) for p in version_parts] + [version] + ["-".join(extra[1:])]

    # We did not recognize what this is, so just fall back to string comparison.
    return [0, 0, 0, 0, "unknown", raw_version]


def _sort_servers(servers):
    servers.sort(
        key=lambda x: _split_version(x["info"]["openttd_version"])
        + [x["info"]["clients_on"], x["info"]["companies_on"]],
        reverse=True,
    )


def _list_servers(filter):
    global _server_list_cache

    if _server_list_cache is None or time.time() > _server_list_cache["expire"]:
        data = api_get(("server",))
        for server in data["servers"]:
            _fix_server_info(server)

        _sort_servers(data["servers"])

        _server_list_cache = {
            "servers": data["servers"],
            "expire": data["expire"] + 1,  # Allow some clock-drift
        }

    servers = _server_list_cache["servers"]
    if filter:
        servers = [server for server in servers if server["info"]["openttd_version"].startswith(filter)]

    expire = datetime.utcfromtimestamp(_server_list_cache["expire"]).strftime("%Y-%m-%d %H:%M:%S") + " UTC"
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
        mapsets=MAPSETS,
        GAMESCRIPT_VERSION_NONE=GAMESCRIPT_VERSION_NONE,
    )


@app.route("/listing")
def servers_all():
    return _list_servers(filter=None)


@app.route("/listing/<filter>")
def servers(filter):
    return _list_servers(filter=filter)


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
            "expire": data["expire"] + 1,  # Allow some clock-drift
        }

    server = _server_entry_cache[server_id]["server"]
    if server is None:
        return redirect("error", message="This server (no longer) exists")

    expire = datetime.utcfromtimestamp(_server_entry_cache[server_id]["expire"]).strftime("%Y-%m-%d %H:%M:%S") + " UTC"

    return template(
        "server_entry.html",
        server=server,
        expire=expire,
        mapsets=MAPSETS,
        GAMESCRIPT_VERSION_NONE=GAMESCRIPT_VERSION_NONE,
    )
