# Master Server web front-end

[![GitHub License](https://img.shields.io/github/license/OpenTTD/master-server-web)](https://github.com/OpenTTD/master-server-web/blob/main/LICENSE)

This is a front-end for the Master Server Public Server listing.
It works together with [master-server](https://github.com/OpenTTD/master-server), which serves the HTTP API.

## Development

This front-end is written in Python 3.11 with Flask.

## Usage

To start it, you are advised to first create a virtualenv:

```bash
python3 -m venv .env
.env/bin/pip install -r requirements.txt
```

After this, you can run the flask application by running:

```bash
make run
```

### Running via docker

```bash
docker build -t openttd/master-server-web:local .
docker run --rm -p 127.0.0.1:5000:80 openttd/master-server-web:local
```
