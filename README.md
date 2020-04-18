# contuga-web
Simple web-based expense manager application.


## Setup

### Prerequisites

The following requirements need to be satisfied to setup the project.

1. [**Python 3.7**](https://www.python.org/) - While the project may work with any Python version above 3.5 it is actively developed using 3.7 and it is the officially supported version. Use any other Python version on your own risk.
1. [**Pipenv**](https://github.com/pypa/pipenv) - Used for installing backend dependencies.
1. [**NPM**](https://www.npmjs.com/) - Used for installing frontend dependencies.
1. [**SassC**](https://github.com/sass/sassc) - The project uses SassC libsass driver for compiling Sass code to plain CSS. Check the official repository to find out how to get SassC installed on your system. For Debian-based Linux distributions, you can just apt install it - `sudo apt install sassc`.

### Installation steps

1. Navigate to the project's root directory.
1. Run `npm install` to install the frontend dependencies.
1. Execute `pipenv install` to install the backend dependencies.
1. Use `pipenv shell` to activate the virtual environment.
1. Type `./manage.py migrate` on Linux/Mac or `python manage.py migrate` on Windows to apply all database migrations. Currently, the default database is SQLite. Edit the settings.py file if you want to use MySQL/MariaDB or PostgreSQL. Read the official Django [documentation](https://docs.djangoproject.com/en/2.2/ref/databases/) to learn more.

### Development

Start the development server using `./manage.py runserver` on Linux/Mac or `python manage.py runserver` on Windows and navigate to http://localhost:8000 in your browser.
If you need admin access you can create user executing `python manage.py createsuperuser`.
