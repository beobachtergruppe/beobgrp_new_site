

# Website Beobachtergruppe

This repository contains the source code for the new website of [beobachtergruppe.de](https://www.beobachtergruppe.de).

## About This Project

This is a Wagtail-based web application. Wagtail is an open source CMS built on Django. For a list of features, see the [Wagtail features page](https://wagtail.org/features/).

A good entrypoint for getting to know wagtail better is this page: [Wagtail getting started](https://docs.wagtail.org/en/stable/getting_started/index.html)

## Table of Contents
- [Development Setup (Linux)](#development-setup-linux)
- [Production Setup (Docker Compose)](#production-setup-docker-compose)
- [Testing](#testing)
- [Type Checking](#type-checking)
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
- `DJANGO_BACKUP_DIR`: Directory path for storing backups (optional, defaults to `../beobgrp_site_backup`)
- `DOCKER_REGISTRY`: Docker registry URL (optional, defaults to `localhost:5000`)

### Version Management

The `VERSION` file contains the single source of truth for image versions:

```
VERSION=1.2.2  # Example version
```

Both development and production builds use this same version. Update this file when you want to build and deploy new versions.

### Local Docker Registry

For local development, use a persistent Docker registry to store built images.

**Start the registry:**
```bash
./start_registry.sh
```

This starts:
- Docker registry at `http://localhost:5000`
- Web UI at `http://localhost:8080` (for browsing and deleting images)
- Persistent storage at `~/.docker-registry`

**Restart the registry:**
```bash
./start_registry.sh --restart
```

**Stop the registry:**
```bash
docker compose -f registry-docker-compose.yml down
```

**Manage images via CLI:**
```bash
# List all images
curl -s http://localhost:5000/v2/_catalog | jq '.repositories'

# List all tags for an image
curl -s http://localhost:5000/v2/beobgrp_site/tags/list | jq '.tags'

# Delete an image tag
curl -X DELETE http://localhost:5000/v2/beobgrp_site/manifests/1.2.1.dev
```

### Building Images

The `build_and_push.sh` script builds a Docker image and pushes it to a registry.

**Prerequisites:**
- Docker daemon running
- Local registry running (`./start_registry.sh` for local development)
- Git repository initialized

**Git Branch-Based Versioning:**
- **On `main` branch**: Builds version from VERSION file (e.g., `1.2.2`)
- **On feature branches**: Automatically appends `.dev` suffix (e.g., `1.2.2.dev`)

This ensures release versions can only be built from the main branch.

**Building with local registry:**
```bash
./start_registry.sh        # Start registry first (if not running)
./build_and_push.sh        # Build and push to localhost:5000
```

**Building for a remote registry:**
```bash
./build_and_push.sh -r registry.example.com
```

**Example builds:**
```bash
# On main branch
./build_and_push.sh  # Builds: beobgrp_site:1.2.2

# On feature-xyz branch
./build_and_push.sh  # Builds: beobgrp_site:1.2.2.dev
```

### Starting Instances

The `start_website.sh` script intelligently defaults based on your git branch:

**On main branch** (defaults to production):
```bash
./start_website.sh migrate              # Start production server (port 8000)
./start_website.sh --version 1.2.3      # Specific version
./start_website.sh --dev --version 1.2.1.dev migrate  # Test dev server before deploying
```

**On feature branch** (defaults to development):
```bash
./start_website.sh --version 1.2.1.dev migrate  # Required: .dev suffix
./start_website.sh --version 1.2.1.dev         # Runs dev server on port 8001
```

**Important Constraints:**
- **--dev and --prod are mutually exclusive** - cannot use both together
- **Development version requires `.dev` suffix** (e.g., `1.2.1.dev`)
- **Production only available on main branch**
- On main: `--prod` is default, `--dev` lets you test a version before production
- On feature branch: `--dev` is default, `--prod` is not allowed

**Setting custom registry:**
```bash
export DOCKER_REGISTRY="registry.example.com"
./start_website.sh migrate
```

### Typical Development Workflow

1. Create feature branch and make changes:
   ```bash
   git checkout -b feature-xyz
   ```

2. Build dev image with `.dev` suffix (automatic):
   ```bash
   ./build_and_push.sh
   # Builds: beobgrp_site:1.2.2.dev
   ```

3. Test in development Docker container (defaults to dev on feature branch):
   ```bash
   ./start_website.sh --version 1.2.2.dev migrate
   # Runs on port 8001
   ```

4. Commit, test, merge to main:
   ```bash
   git checkout main
   git merge feature-xyz
   ```

5. Build release image (no `.dev` suffix):
   ```bash
   ./build_and_push.sh
   # Builds: beobgrp_site:1.2.2
   ```

6. Deploy to production (defaults to prod on main branch):
   ```bash
   ./start_website.sh migrate
   # Runs on port 8000
   ```

**Optional: Test a version in dev mode before production**

If you want to test a production version in the dev server before deploying:
```bash
git checkout main
./build_and_push.sh           # Build version 1.2.2
./start_website.sh --dev --version 1.2.2.dev migrate  # Test in dev mode
./start_website.sh migrate    # Deploy to production when satisfied
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

