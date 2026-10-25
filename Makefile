SHELL := /bin/bash

pull_changes:
	git pull
install_dependencies:
	npm install && poetry install --with dev
migrate:
	poetry run ./manage.py migrate
collectstatic:
	poetry run ./manage.py collectstatic --no-input
compilemessages:
	poetry run ./manage.py compilemessages
reload:
	touch contuga/wsgi.py
update:	pull_changes install_dependencies migrate collectstatic compilemessages reload
