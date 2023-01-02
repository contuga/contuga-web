FROM python:3.10

RUN apt update && apt install -y sassc cssmin gettext
RUN pip3 install uwsgi pipenv gunicorn

ENV NODE_VERSION=18.12.1
ENV NVM_VERSION=0.39.1
ENV NVM_DIR=/root/.nvm

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh | bash
RUN . "${NVM_DIR}/nvm.sh" && nvm install ${NODE_VERSION}
ENV PATH="${NVM_DIR}/versions/node/v${NODE_VERSION}/bin/:${PATH}"

RUN npm install -g uglify-js

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
