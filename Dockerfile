FROM node:14.15.3-buster
RUN apt update && apt install -y python3 python3-pip sassc cssmin gettext
RUN pip3 install uwsgi pipenv gunicorn
RUN npm install -g yuglify

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system

COPY package.json .
COPY package-lock.json .

RUN npm install

COPY . .

ENV DJANGO_ENV=production

EXPOSE 8000

CMD sh docker-entrypoint.sh
