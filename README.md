

# Website Beobachtergruppe

This repository contains the source code for the new website of [beobachtergruppe.de](https://www.beobachtergruppe.de).

## About This Project

This is a Wagtail-based web application. Wagtail is an open source CMS built on Django. For a list of features, see the [Wagtail features page](https://wagtail.org/features/).

A good entrypoint for getting to know wagtail better is this page: [Wagtail getting started](https://docs.wagtail.org/en/stable/getting_started/index.html)

## Table of Contents

- [Development Setup (Linux)](#development-setup-linux)
  - [Prerequisites](#prerequisites)
  - [Database Configuration (Linux)](#database-configuration-linux)
  - [Clone the Repository](#clone-the-repository)
  - [Python Environment Setup](#python-environment-setup)
  - [Database Setup](#database-setup)
  - [Dart Sass Installation](#dart-sass-installation)
  - [VS Code Debugging](#vs-code-debugging)
- [Production Setup (Docker Compose)](#production-setup-docker-compose)
  - [Overview](#overview)
  - [Environment Variables](#environment-variables)
  - [Version Management](#version-management)
  - [Local Docker Registry](#local-docker-registry)
  - [Building Images](#building-images)
  - [Starting Instances](#starting-instances)
  - [Stopping Instances](#stopping-instances)
  - [Typical Development Workflow](#typical-development-workflow)
  - [Docker Registry Setup](#docker-registry-setup)
  - [Access URLs](#access-urls)
  - [Database and Media](#database-and-media)
  - [Complete Workflow Example](#complete-workflow-example)
  - [Backup and Restore Scripts](#backup-and-restore-scripts)
- [Testing](#testing)
  - [Prerequisites for Testing](#prerequisites-for-testing)
  - [Running Tests](#running-tests)
- [Type Checking](#type-checking)
  - [Setup](#setup)
  - [Running Type Checks](#running-type-checks)
  - [Configuration](#configuration)
  - [Type Annotations](#type-annotations)
  - [Running All Quality Checks](#running-all-quality-checks)
- [Windows/WSL Notes](#windowswsl-notes)
- [License](#license)

---

## Development Setup (Linux)

This project is primarily developed and tested on Linux. You can also try using Windows Subsystem for Linux (WSL), but it is not officially tested.

This section describes how to setup a local development environment to run the website in debug mode and have realtime website updates, when code or CSS files are changed. Once your fixes are fine you can push your code and proceed with testing the production as described in the next section.

### Prerequisites

Install these exact versions:

| Component | Version |
|---|---|
| Python | 3.15.2 (with the `venv` module) |
| pip | 26.3 |
| PostgreSQL server | 16 |
| PostgreSQL client | 16.15 |
| Node.js | 18.20.4 |
| npm | 9.2.0 |
| Dart Sass | 1.99.0 |
| Bulma | 1.0.4 |
| gunicorn | 26.2.0 |

Follow the steps for your distribution (Ubuntu 22.04 or 24.04, or Debian 12).

**1. Python 3.15.2 with `venv`**

Ubuntu 22.04 and 24.04 (deadsnakes PPA):
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.15 python3.15-venv python3.15-dev
```

Debian 12: Python 3.15 is not in the bookworm repositories. Install a 3.15.2 build, for example with pyenv (`pyenv install 3.15.2`), and make sure `python3.15` points to it.

**2. Build dependencies**

Ubuntu 22.04 and 24.04:
```bash
sudo apt install build-essential libpq-dev libjpeg-turbo8-dev zlib1g-dev libwebp-dev pkg-config lsb-release curl ca-certificates
```
Debian 12: use `libjpeg62-turbo-dev` instead of `libjpeg-turbo8-dev`.

**3. PostgreSQL 16 server and client**

Use the PostgreSQL apt repository, which works on Ubuntu 22.04, Ubuntu 24.04, and Debian 12. Then check that `psql --version` reports 16.x:
```bash
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt install postgresql-16 postgresql-client-16
```
Install Git and VS Code (recommended) as well.

Node.js, npm, Dart Sass and Bulma are described in [Dart Sass Installation](#dart-sass-installation) below.

### Database Configuration (Linux)

Allow the `postgres` user to log in over the local socket without a password, so you can create the `wagtail` role and database later:

1. Edit `pg_hba.conf`:
   ```bash
   sudo nano /etc/postgresql/16/main/pg_hba.conf
   ```
   Change the existing `local all postgres peer` line to:
   ```
   local   all   postgres   trust
   ```

2. Restart PostgreSQL to apply the change:
   ```bash
   sudo systemctl restart postgresql
   ```

3. Check that this works without a password prompt:
   ```bash
   psql -U postgres -c "SELECT current_user;"
   ```

### Clone the Repository

Clone via SSH (ensure your public key is added to GitHub):
```bash
git clone git@github.com:beobachtergruppe/beobgrp_new_site.git
```

### Python Environment Setup

```bash
cd beobgrp_new_site
python3.15 -m venv venv
source venv/bin/activate
pip install "pip==26.3"
pip install -r requirements.txt
pip install "gunicorn==26.2.0"
```

### Database Setup

Set your database password:
```bash
export WAGTAIL_DB_PASSWORD="your_password"
```
Create the role and database:
```bash
psql -U postgres -c "CREATE USER wagtail WITH PASSWORD '$WAGTAIL_DB_PASSWORD';"
psql -U postgres -c "CREATE DATABASE beobgrp_site OWNER wagtail;"
```

#### Restore an existing backup (recommended)

To work with the current website data, restore the latest database and media backup with `restore.sh`. Put the backup files in a directory and point `DJANGO_BACKUP_DIR` to it (default: `../beobgrp_site_backup`, next to the project). Then, from the project root with the venv activated:

```bash
source venv/bin/activate
export WAGTAIL_DB_PASSWORD="your_password"
export DJANGO_BACKUP_DIR=/path/to/backup
export WAGTAIL_DB_HOST=localhost        # default if not set
./restore.sh
```

`restore.sh` runs these steps in order:
1. Drops and recreates the `public` schema of `beobgrp_site`. **All existing data in this local database is lost.**
2. Restores the database backup with `manage.py dbrestore`.
3. Restores the media files with `manage.py mediarestore` (into `media/`, or `DJANGO_MEDIA_DIR` if set).
4. Runs `manage.py migrate`.

Never point `restore.sh` at the production database.

#### Empty database (no backup)

If you don't have a backup, create the tables for an empty site:
```bash
./manage.py migrate
```

### Dart Sass Installation

Node.js, npm, Dart Sass and Bulma must be these exact versions: Node.js 18.20.4, npm 9.2.0, Sass 1.99.0 and Bulma 1.0.4. Sass 1.100+ requires Node.js 20.19+, so keep Sass at 1.99.0 while using Node.js 18.

Ubuntu's `nodejs` package does not provide 18.20.4 (22.04 ships Node.js 12, 24.04 ships 18.19.1), so install Node.js with nvm, which does not need `sudo`:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.41.0/install.sh | bash
# open a new terminal, or run: source ~/.bashrc
nvm install 18.20.4
nvm use 18.20.4
nvm alias default 18.20.4
npm install --global npm@9.2.0
npm install --global sass@1.99.0
sass --version
```
`sass --version` must print `1.99.0`.

Then install the project's Bulma version from [package.json](/home/jdj/private/projecten/websites/beobgrp_new_site/package.json) in the project directory:
```bash
npm install
```

Then compile and compress the CSS/JS assets:
```bash
./manage.py compress
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

### VS Code Debugging

The repository contains a launch configuration, `Run Django Server`, in [.vscode/launch.json](/home/jdj/private/projecten/websites/beobgrp_new_site/.vscode/launch.json). It runs `manage.py runserver 8001` with `PRODUCTION_VERSION=false`, so breakpoints work and the server reloads on code changes.

1. Install the VS Code Python extension (`ms-python.python`), which includes the debugger.
2. Select the virtual environment interpreter: `Ctrl+Shift+P` → `Python: Select Interpreter` → `venv/bin/python`.
3. Make sure the environment variables are visible to VS Code. VS Code only inherits variables from the shell it was started in, so start it from a terminal where you exported them:
   ```bash
   export WAGTAIL_DB_PASSWORD="your_password"
   code /path/to/beobgrp_new_site
   ```
   The debugged server needs `WAGTAIL_DB_PASSWORD` to connect to PostgreSQL. Dart Sass must also be on the `PATH`, because the development SCSS compilation calls `sass`.
4. Open the Run and Debug view, choose `Run Django Server`, and press `F5`.

---

## Production Setup (Docker Compose)

Production runs via Docker Compose. Both development and production modes are supported with separate databases and configurations.

### Overview

The deployment system consists of:
- **VERSION file**: Central location for version management
- **build_and_push.sh**: Builds a single production Docker image and pushes it to a registry
- **start_website.sh**: Starts dev, prod, or both instances using the same image with different environment variables
- **docker-compose.yml**: Orchestrates containers with separate networks and volumes for dev/prod

The same Docker image is used for both development and production modes running in Docker. The difference is controlled by environment variables (PRODUCTION_VERSION flag and port settings). Real development with live code reloading uses `manage.py runserver` locally, not Docker.

### Environment Variables

Set the following required environment variables:
- `WAGTAIL_DB_PASSWORD`: Database password for the wagtail user
- `WAGTAIL_EMAIL_PASSWORD`: SMTP password for email notifications (the email address is configured in Django settings)
- `DJANGO_BACKUP_DIR`: Directory path for storing backups (optional, defaults to `../beobgrp_site_backup`)
- `DOCKER_REGISTRY`: Docker registry URL (optional, defaults to `localhost:5000`)

### Version Management

The `VERSION` file contains the single source of truth for image versions:

```
VERSION=1.2.2  # Example version
```

Both development and production builds use this same version. Update this file when you want to build and deploy new versions.

### Local Docker Registry (Optional)

A Docker registry is **only needed if building and running on different machines**. For single-machine development and testing, you don't need a registry - Docker uses locally built images automatically.

**When you need a registry:**
- Building images on one machine and running on another
- Sharing images across a team
- Production CI/CD pipelines that push to remote registries

**Optional local registry for testing multi-machine setups:**

Start a local registry:
```bash
./start_registry.sh
```

This starts:
- Docker registry at `http://127.0.0.1:5000`
- Web UI at `http://127.0.0.1:8080` (for browsing and deleting images)
- Persistent storage at `~/.docker-registry`

Build and push to local registry:
```bash
./build_and_push.sh -r 127.0.0.1:5000  # Build and push to local registry
./start_website.sh migrate              # Docker pulls from local registry
```

**Manage local registry:**
```bash
# Restart the registry
./start_registry.sh --restart

# Stop the registry
docker compose -f registry-docker-compose.yml down

# List images
curl -s http://127.0.0.1:5000/v2/_catalog | jq '.repositories'

# Delete an image tag
curl -X DELETE http://127.0.0.1:5000/v2/beobgrp_site/manifests/1.2.1.dev
```

### Building Images

The `build_and_push.sh` script builds a Docker image and optionally pushes it to a registry.

**Git Branch-Based Versioning:**
- **On `main` branch**: Builds version from VERSION file (e.g., `1.2.2`)
- **On feature branches**: Automatically appends `.dev` suffix (e.g., `1.2.2.dev`)

This ensures release versions can only be built from the main branch.

**For local development (build only, no registry needed):**
```bash
./build_and_push.sh        # Build image locally: beobgrp_site:1.2.2.dev
./start_website.sh --version 1.2.2.dev migrate  # Run on same machine
```

**For production or remote servers (push to registry):**
```bash
./build_and_push.sh -r registry.example.com           # Build and push
DOCKER_REGISTRY=registry.example.com ./start_website.sh migrate  # Pull and run on remote server
```

**Local registry (optional, for testing multi-machine setups):**
```bash
./start_registry.sh                     # Start local registry
./build_and_push.sh -r 127.0.0.1:5000  # Build and push locally
./start_website.sh migrate              # Run with local images
```

**Example builds:**
```bash
# On main branch - builds as 1.2.2
./build_and_push.sh  # Local: beobgrp_site:1.2.2
-r registry.example.com  # Push to registry

# On feature-xyz branch - builds as 1.2.2.dev
./build_and_push.sh  # Local: beobgrp_site:1.2.2.dev
```

### Starting Instances

The `start_website.sh` script intelligently defaults based on your git branch and whether a registry is configured.

**On main branch** (defaults to production):
```bash
./start_website.sh migrate                                    # Start production server
./start_website.sh --version 1.2.3 migrate                   # Specific version
./start_website.sh --dev --version 1.2.1.dev migrate         # Test dev server before deploying
```

**On feature branch** (defaults to development):
```bash
./start_website.sh --version 1.2.1.dev migrate   # Required: .dev suffix
./start_website.sh --version 1.2.1.dev           # Runs dev server on port 8001
```

**Important Constraints:**
- **--dev and --prod are mutually exclusive** - cannot use both together
- **Development version requires `.dev` suffix** (e.g., `1.2.1.dev`)
- **Production only available on main branch**
- On main: `--prod` is default, `--dev` lets you test a version before production
- On feature branch: `--dev` is default, `--prod` is not allowed

**Using images from a remote registry:**
```bash
export DOCKER_REGISTRY="registry.example.com"
./start_website.sh migrate      # Pulls image from registry and runs it
```

If `DOCKER_REGISTRY` is not set, Docker uses locally built images.

### Stopping Instances

The `stop_website.sh` script stops the running production or development server using the same profile system as `start_website.sh`.

**Stop production server** (main branch only):
```bash
./stop_website.sh --prod
```

**Stop development server:**
```bash
./stop_website.sh --dev
```

**Important Constraints:**
- **--dev and --prod are mutually exclusive** - cannot use both together
- **One flag is required** - must specify either `--dev` or `--prod`
- **Production only available on main branch** - attempting `--prod` on a feature branch will fail

The script uses Docker Compose's `down` command to cleanly stop the containers for the specified profile.

### Typical Development Workflow

**Local testing (simplest case):**

1. Create feature branch and make changes:
   ```bash
   git checkout -b feature-xyz
   ```

2. Build image locally:
   ```bash
   ./build_and_push.sh
   # Builds: beobgrp_site:1.2.2.dev
   ```

3. Test in development Docker container:
   ```bash
   ./start_website.sh --version 1.2.2.dev migrate
   # Runs on port 8001 with locally built image
   ```

4. Commit, test, merge to main:
   ```bash
   git checkout main
   git merge feature-xyz
   ```

5. Build production image:
   ```bash
   ./build_and_push.sh
   # Builds: beobgrp_site:1.2.2
   ```

6. Deploy to production:
   ```bash
   ./start_website.sh migrate
   # Runs on port 8000 with locally built image
   ```

**With remote registry (for multi-server setup):**

1. Build and push to registry:
   ```bash
   ./build_and_push.sh -r registry.example.com
   ```

2. On remote server, pull and run:
   ```bash
   export DOCKER_REGISTRY="registry.example.com"
   ./start_website.sh migrate
   # Docker pulls image from registry and runs it
   ```

### Docker Registry Setup

For a local development registry, see [REGISTRY_SETUP.md](REGISTRY_SETUP.md) for detailed setup instructions including:
- Quick local registry setup
- Persistent storage configuration
- SSL/TLS setup for production
- Troubleshooting

### Access URLs

Once started, the website is available at:
- **Production**: http://localhost:8000
- **Development**: http://localhost:8001 (if started with `--dev`)

### Database and Media

Each mode (dev/prod) has:
- Separate PostgreSQL database
- Separate media volume
- Separate network for isolation

You can safely run dev and prod simultaneously without any conflicts.

### Complete Workflow Example

1. **Update version:**
   ```bash
   echo "VERSION=1.2.3" > VERSION
   ```

2. **Build both dev and prod variants:**
   ```bash
   export DOCKER_REGISTRY="localhost:5000"
   ./build_and_push.sh
   ```

3. **Start production with migrations:**
   ```bash
   export WAGTAIL_DB_PASSWORD="your_password"
   ./start_website.sh migrate
   ```

4. **Start development for testing (in another terminal):**
   ```bash
   export WAGTAIL_DB_PASSWORD="your_password"
   ./start_website.sh --dev migrate
   ```

5. **Test development changes:**
   - Visit http://localhost:8001
   - Edit SCSS files - they recompile automatically
   - Make code changes and see them reflected

6. **When ready, stop and clean up:**
   ```bash
   docker compose --profile dev,prod down
   ```

### Backup and Restore Scripts

**For development (local):**
- `backup.sh`: Create database and media backups
- `restore.sh`: Restore database and media from backup, then run migrations

**For production (Docker):**
- `server_backup.sh`: Execute backup inside Docker container and clean up old backups (>3 days)

---

## Testing

This project includes **38 tests** covering all Wagtail page models and custom blocks. The tests:
- Validate model structure and configuration
- Protect against API changes in Wagtail and Django  
- Run quickly (~75ms) using simplified test approach
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

Run all tests (38 tests in ~75ms):
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

## Type Checking

This project uses **mypy** for static type checking to catch type errors before runtime and improve code quality.

### Setup

Type checking dependencies are separate from runtime dependencies. Install them with:

```bash
pip install -r mypy-requirements.txt
```

### Running Type Checks

Check all files:
```bash
mypy .
```

Check specific directory:
```bash
mypy home/
```

### Configuration

Type checking is configured in `mypy.ini`:
- Uses `django-stubs` plugin for Django type support
- Excludes migration files and virtual environment
- Ignores missing type stubs for Wagtail (not yet fully typed)
- Configured for Python 3.12

Dependencies for type checking are in `mypy-requirements.txt` (separate from runtime `requirements.txt`).

### Type Annotations

Model fields are annotated with their field types:
```python
class SingleEvent(Page):
    start_time: DateTimeField = DateTimeField()
    event_title: CharField = CharField(max_length=140, default="")
```

This helps IDEs provide better autocomplete and catches type errors early.

### Running All Quality Checks

You can run both tests and type checks with a single command:
```bash
./run_checks.sh
```

This will run:
1. All 23 unit tests
2. Type checking on the entire codebase

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

