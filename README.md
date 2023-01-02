# contuga-web

Simple web-based expense manager application.

## Setup

### Prerequisites

The following requirements need to be satisfied to setup the project.

1. [**Python**](https://www.python.org/) - While the project may work with any Python version above 3.5 it is actively developed using 3.10 and it is the officially supported version. Use any other Python version at your own risk.
1. [**Pipenv**](https://github.com/pypa/pipenv) - Used for installing backend dependencies. The latest version is the one usually used for development but the tool is stable and most versions should work flawlessly.
1. [**NodeJS**](https://nodejs.org/) - The project is currently using the latest LTS version.
1. [**NPM**](https://www.npmjs.com/) - Used for installing frontend dependencies. Use the one that usually comes with the latest LTS version of Node but a newer one should also work.
1. [**SassC**](https://github.com/sass/sassc) - The project uses SassC libsass driver for compiling Sass code to plain CSS. Check the official repository to find out how to get SassC installed on your system. For Debian-based Linux distributions, you can just install it - `sudo apt install sassc`.

### Installation steps

1. Navigate to the project's root directory.
1. Run `npm install` to install the frontend dependencies.
1. Execute `pipenv install` to install the backend dependencies.
1. Use `pipenv shell` to activate the virtual environment.
1. Type `./manage.py migrate` on Linux/Mac or `python manage.py migrate` on Windows to apply all database migrations. Currently, the default database is SQLite. Edit the settings.py file if you want to use MySQL/MariaDB or PostgreSQL. Read the official Django [documentation](https://docs.djangoproject.com/en/2.2/ref/databases/) to learn more.

### Development

Start the development server using `./manage.py runserver` on Linux/Mac or `python manage.py runserver` on Windows and navigate to http://localhost:8000 in your browser.
If you need admin access you can create a user by executing `python manage.py createsuperuser`.

### Running using Docker

The project can also be started from a Docker container either by running it manually or using the existing docker-compose manifest. The latter is preconfigured to use PostgreSQL database and nGINX as HTTP server. If you choose not to use docker-compose, you will have to configure these services manually.

#### Using docker

1. Configure the database connection in the settings.
1. Navigate to the project's root directory.
1. Build the image with `docker build -t contuga-web .`
1. Create a volume for the static files using `docker volume create contuga-web-static`.
1. Create a volume for the media files using `docker volume create contuga-web-media`.
1. Execute `docker inspect contuga-web-static` to find where the named volumes are stored.
1. Run the docker container using `docker run --network=host -v contuga-web-static:/usr/src/app/static -v contuga-web-media:/usr/src/app/media contuga-web`
1. Configure your HTTP server to connect with the running WSGI application and to serve the two directories under `/static` and `/media`. You can use existing [nginx.conf](nginx/nginx/conf) as an example. You can check if the WSGI application is up and running by accessing http://localhost:8000.

#### Using docker-compose

1. Configure the database connection in the settings.
1. Run `docker-compose up` to start the services.
