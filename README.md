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
1. Type `pipenv run migrate` to apply all database migrations. Currently, the default database is SQLite. Edit the settings.py file if you want to use MySQL/MariaDB or PostgreSQL. Read the official Django [documentation](https://docs.djangoproject.com/en/4.2/ref/databases/) to learn more.

### Development

Start the development server using `pipenv run server` and navigate to http://localhost:8000 in your browser.
If you need admin access you can create a privileged user by executing `pipenv run manage createsuperuser`.
If you need to execute something else within the project's environment, you can enter the environment using `pipenv shell`.

### Running using Docker

The project can also be started from a Docker container either by running it manually or using the existing docker-compose manifest. The latter is preconfigured to use PostgreSQL database and nGINX as HTTP server. If you choose not to use docker-compose, you will have to configure these services manually.

If you want to use the debug toolbar, you should add the gateway IP of the container to `INTERNAL_IPS`. To find the IP, use `docker inspect <identifier>`.

#### Using docker

Use the following steps to prepare and run the dev image:

1. Configure the database connection in the settings. You can use SQLite or configure your own database server.
1. Navigate to the project's root directory.
1. Build the image with `docker build -f Dockerfile.dev -t contuga-web .`
1. Run the docker container using `docker run -it -p 8000:8000 -v $(pwd):/usr/src/app/ contuga-web`
1. Access the app at http://localhost:8000.
1. You can now edit the source files and the changes will be applied to the running app.

Use the following steps to prepare and run the prod image:

1. Configure the database connection in the settings. You can use SQLite or configure your own database server.
1. Navigate to the project's root directory.
1. Build the image with `docker build -t contuga-web .`
1. Run the docker container using `docker run --network=host -v contuga-web-static:/usr/src/app/static -v contuga-web-media:/usr/src/app/media contuga-web`
1. Configure your HTTP server to connect with the running WSGI application and to serve the two directories under `/static` and `/media`. You can use the existing [nginx.conf](nginx/nginx/conf) as an example. You can check if the WSGI application is up and running by accessing http://localhost:8000.

#### Using compose

If you are using the Compose plugin, Docker Compose can be used directly from the docker cli via `docker compose`. If you are using the standalone Compose, use `docker-compose`. The instruction in this section will use the Compose plugin but `docker-compose` will also work.

Use the following steps to start the app in dev mode:

1. Configure the database connection in the settings.
1. Run `docker compose -f docker-compose.dev.yaml up` to start the services.
1. You can now edit the source files and the changes will be applied to the running app.
1. Access the app at http://localhost:8000.

To use `ipdb` or `pdb`, you have to attach to the container first with `docker attach contuga-web-web-1`.

Use the following steps to start the app in prod mode:

1. Configure the database connection in the settings.
1. Run `docker compose up` to start the services.
1. Access the app at http://localhost.
