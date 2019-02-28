SHELL := /bin/bash

gitfetch:
	git pull
install_dependencies:
	npm install && pipenv install
collectstatic:
	pipenv run ./manage.py collectstatic --no-input
compilemessages:
	pipenv run ./manage.py compilemessages
restart:
	touch contuga/wsgi.py
update:	gitfetch install_dependencies collectstatic compilemessages restart
