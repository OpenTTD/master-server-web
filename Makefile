.PHONY: run venv flake8

run: .venv/pyvenv.cfg
	FLASK_ENV=development .venv/bin/python3 -m webclient --api-url "http://localhost:8080" run

venv: .venv/pyvenv.cfg

.venv/pyvenv.cfg: requirements.txt
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

flake8:
	python3 -m flake8 webclient
