.PHONY: run venv flake8

run: .env/pyvenv.cfg
	FLASK_ENV=development .env/bin/python3 -m webclient --api-url "http://localhost:8080" run

venv: .env/pyvenv.cfg

.env/pyvenv.cfg: requirements.txt
	python3 -m venv .env
	.env/bin/pip install -r requirements.txt

flake8:
	python3 -m flake8 webclient
