# Master Server web front-end

[![GitHub License](https://img.shields.io/github/license/OpenTTD/master-server-web)](https://github.com/OpenTTD/master-server-web/blob/master/LICENSE)
[![GitHub Tag](https://img.shields.io/github/v/tag/OpenTTD/master-server-web?include_prereleases&label=stable)](https://github.com/OpenTTD/master-server-web/releases)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/OpenTTD/master-server-web/latest/master)](https://github.com/OpenTTD/master-server-web/commits/master)

[![GitHub Workflow Status (Testing)](https://img.shields.io/github/workflow/status/OpenTTD/master-server-web/Testing/master?label=master)](https://github.com/OpenTTD/master-server-web/actions?query=workflow%3ATesting)
[![GitHub Workflow Status (Publish Image)](https://img.shields.io/github/workflow/status/OpenTTD/master-server-web/Publish%20image?label=publish)](https://github.com/OpenTTD/master-server-web/actions?query=workflow%3A%22Publish+image%22)
[![GitHub Workflow Status (Deployments)](https://img.shields.io/github/workflow/status/OpenTTD/master-server-web/Deployment?label=deployment)](https://github.com/OpenTTD/master-server-web/actions?query=workflow%3A%22Deployment%22)

[![GitHub deployments (Staging)](https://img.shields.io/github/deployments/OpenTTD/master-server-web/staging?label=staging)](https://github.com/OpenTTD/master-server-web/deployments)
[![GitHub deployments (Production)](https://img.shields.io/github/deployments/OpenTTD/master-server-web/production?label=production)](https://github.com/OpenTTD/master-server-web/deployments)

This is a front-end for the Master Server Public Server listing.
It works together with [master-server](https://github.com/OpenTTD/master-server), which serves the HTTP API.

## Development

This front-end is written in Python 3.7 with Flask.

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
