SHELL := /bin/bash

pull_changes:
	git pull
install_dependencies:
	npm install && pipenv sync
migrate:
	pipenv run ./manage.py migrate
collectstatic:
	pipenv run ./manage.py collectstatic --no-input
compilemessages:
	pipenv run ./manage.py compilemessages
reload:
	touch contuga/wsgi.py
update:	pull_changes install_dependencies migrate collectstatic compilemessages reload
