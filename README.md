

# Website Beobachtergruppe

This repository contains the source code for the new website of [beobachtergruppe.de](https://www.beobachtergruppe.de).

## About This Project

This is a Wagtail-based web application. Wagtail is an open source CMS built on Django. For a list of features, see the [Wagtail features page](https://wagtail.org/features/).

A good entrypoint for getting to know wagtail better is this page: [Wagtail getting started](https://docs.wagtail.org/en/stable/getting_started/index.html)

## Table of Contents
- [Development Setup (Linux)](#development-setup-linux)
- [Production Setup (Docker Compose)](#production-setup-docker-compose)
- [Testing](#testing)
- [Windows/WSL Notes](#windowswsl-notes)
- [License](#license)

---

## Development Setup (Linux)

This project is primarily developed and tested on Linux. You can also try using Windows Subsystem for Linux (WSL), but it is not officially tested.

### Prerequisites

- Python 3.12
- PostgreSQL 16 ([Download](https://www.postgresql.org/download/))
- Node.js and npm (for Dart Sass compilation)
- Git
- VS Code (recommended)

### Database Configuration (Linux)

PostgreSQL needs to be configured to allow the wagtail user to connect with password authentication.

1. Edit `pg_hba.conf` to enable password authentication:
   ```bash
   sudo nano /etc/postgresql/16/main/pg_hba.conf
   ```
   Ensure you have a line like this for local connections:
   ```
   local   all   all   scram-sha-256
   ```
   Or for peer authentication (allows `postgres` user without password):
   ```
   local   all   postgres   peer
   local   all   all        scram-sha-256
   ```

2. Restart PostgreSQL to apply changes:
   ```bash
   sudo systemctl restart postgresql
   ```

For more details on PostgreSQL authentication, see the [official documentation](https://www.postgresql.org/docs/16/auth-pg-hba-conf.html).

### Clone the Repository

Clone via SSH (ensure your public key is added to GitHub):
```bash
git clone git@github.com:beobachtergruppe/beobgrp_new_site.git
```

### Python Environment Setup

```bash
cd beobgrp_new_site
virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Setup

Set your database password:
```bash
export WAGTAIL_DB_PASSWORD="your_password"
```
Create the role and database:
```bash
sudo -u postgres psql -c "CREATE USER wagtail WITH PASSWORD '$WAGTAIL_DB_PASSWORD';"
sudo -u postgres createdb beobgrp_site
sudo -u postgres psql -c "ALTER DATABASE beobgrp_site OWNER TO wagtail;"
```

Run migrations:
```bash
./manage.py migrate
```

### Dart Sass Installation

This project uses Dart Sass to compile SCSS files. Install it globally via npm:
```bash
sudo npm install --global sass
npm install bulma@1.0.4
```

Then compile and compress the CSS/JS assets:
```bash
./manage.py compress
```

Optionally restore backup data:
```bash
export DJANGO_BACKUP_DIR=/your/backup/dir
./manage.py dbrestore
./manage.py mediarestore
```

Collect static files:
```bash
./manage.py collectstatic --noinput --clear
```

Start the development server:
```bash
./manage.py runserver 8001
```
Visit: http://localhost:8001

---

## Production Setup (Docker Compose)

Production runs via Docker Compose. See `docker-compose.yml` and related scripts.

### Environment Variables
Set the following required environment variables:
- `WAGTAIL_DB_PASSWORD`: Database password for the wagtail user
- `DJANGO_BACKUP_DIR`: Directory path for storing backups (optional, defaults to `../beobgrp_site_backup`)

### Starting the Server
Use the `start_website.sh` script with one of the following modes:
```bash
./start_website.sh [none|restore|migrate]
```
- `none`: Start server only
- `restore`: Restore database and media from backup before starting
- `migrate`: Run database migrations before starting

This script runs `docker compose` with building the Docker image for the server.

The server will be available at http://localhost:8000

### Backup and Restore Scripts

**For development (local):**
- `backup.sh`: Create database and media backups
- `restore.sh`: Restore database and media from backup, then run migrations

**For production (Docker):**
- `server_backup.sh`: Execute backup inside Docker container and clean up old backups (>3 days)

---

## Testing

This project includes **23 tests** covering all Wagtail page models and custom blocks. The tests:
- Validate model structure and configuration
- Protect against API changes in Wagtail and Django  
- Run quickly (~50ms) using simplified test approach
- Focus on critical functionality without complex integration testing

### Prerequisites for Testing

The PostgreSQL user needs the `CREATEDB` privilege to create test databases:

```bash
sudo -u postgres psql -c "ALTER USER wagtail CREATEDB;"
```

Or run the provided helper script:
```bash
./grant_test_db_permission.sh
```

**If tests hang**, drop the test database:
```bash
PGPASSWORD="$WAGTAIL_DB_PASSWORD" psql -h localhost -U wagtail -d postgres -c "DROP DATABASE IF EXISTS test_beobgrp_site;"
```

### Running Tests

Run all tests (23 tests in ~50ms):
```bash
python manage.py test home.tests
```

Run specific test modules:
```bash
python manage.py test home.tests.test_setup
python manage.py test home.tests.test_home_page
python manage.py test home.tests.test_events_simple
python manage.py test home.tests.test_gallery_simple
python manage.py test home.tests.test_blocks_simple
```

Run with verbose output:
```bash
python manage.py test home.tests -v 2
```

For detailed information about test coverage and troubleshooting, see [home/tests/README.md](home/tests/README.md).

---

## Windows/WSL Notes

You may be able to use Windows Subsystem for Linux (WSL) for development. However, this setup is not officially tested. If you encounter issues, please consult the WSL documentation or seek help from the community.

Common caveats:
- File system differences may affect database and media file handling.
- Docker Desktop is required for running Docker containers on Windows.
- Some Linux-specific commands may need adaptation.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

