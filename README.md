# Website Beobachtergruppe

This project contains the new website of https://www.beobachtergruppe.de

## Installation 

This has been tested with Linux, but the Windows Subsystem for Linux (WSL) should also work.

### Development environment

Make sure that your development tools are installed:
* Python 3.12
* Database: Postgresql 16 (see https://www.postgresql.org/download/)
* git utilities
* vscode IDE


To install the development environment you first need to clone 
the git repository (for that you need to have your public SSH key setup in Githib):

```shell
git clone git@github.com:beobachtergruppe/beobgrp_site.git
```

Then go into the newly created project `beobgrp_site` and do the following:

* Setup the virtual environment (see e.g. https://virtualenv.pypa.io/en/latest/user_guide.html):
```
virtualenv venv
```
* Upgrade the pip Python package installation tool:
```
pip install --upgrade pip
```
* Install all the packages for this project:
```
pip install -r requirements.txt
```
* Set the database password
```
export WAGTAIL_DB_PASSWORD="some_password" 
```
* Create the role 'wagtail' with the password as above 
(on Linux using postgres account from installation):
```
sudo -u postgres psql -c "CREATE USER wagtail WITH PASSWORD '$WAGTAIL_DB_PASSWORD';"
```
* Create the database beobgrp_site and allow access for user 'wagtail':
```
sudo -u postgres createdb beobgrp_site
sudo -u postgres psql -c "ALTER DATABASE beobgrp_site OWNER TO wagtail;"
```

* Run the database migration to create the database:
```
./manage.py migrate
```
* Optionally restore a backup of the site data:
```
export DJANGO_BACKUP_DIR=/your/backup/dir
./manage.py dbrestore
./manage.py mediarestore
```
Your backup directory may contain a backup from our server.
* Collect all static files:
```
manage.py collectstatic --noinput --clear
```
* Start the server in development mode:
```
./manage.py runserver 8001
```
Now you can access the server on http://localhost:8001

### Production

The production server runs with a Docker compose configuration.

* Define the environment variables as in the previous section 
(DJANGO_DB_PASSWORD and DJANGO_BACKUP_DIR)
* Run the startup script `start_docker.sh` with one of the following modes:
  - none: Just start the server without anything else
  - restore: Restore the data before starting the server
  - migrate: Run the migrations (should be done after any model change)

- The server is reachable under http://localhost:8000

