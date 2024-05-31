# Website Beobachtergruppe

Dieses Project enthält die neue Website der Beobachtergruppe, welche auf wagtail
basiert is.

## Installation

Die Website kann einfach mit einem docker compose setup gestartet werden:

Definiere das Passwort in der folgenden Environment Variable:

```shell
export WAGTAIL_DB_PASSWORD="some_password"
```

Im Project Folder:

```shell
docker compose up -d --build
```

Dann ist die Site auf https://localhost:8000 erreichbar. 

Mit unserem Apache Server kann die Site Live geschaltet werden.

## Entwickler Information

### docker compose 

Mit `docker compose` Kommandozeilen kann man die Services 'wagtail' und 
'postgres' erreichen und z.B. wagtail Kommandos mit `docker compose -p beobgrp_site exec` ausführen.

### Backup/Restore Database

Auf dem Server kann man den Database mit dieser Kommandozeile speichern:
```shell
docker compose -p beobgrp_site exec postgres pg_dump --create -U wagtail beobgrp_site > beobgrp_site.sql
```

Mit diesem Kommando kann man den auf einem anderen Computer wieder restoren (sollte wagtail user haben):

```shell
psql -U postgres < beobgrp_site.sql
```

Hier ist angenommen, dass einen Postgres mit lokalen Rechten ohne Authentifizierung auf allen Datenbanken 
installiert ist. Das ist völlig in Ordnung für Entwicklung, wenn der Datenbank nur Lokal erreichbar ist.

### Entwicklungsumgebung Linux

Wenn man die Website entwickelt, dann möchte man alles einfach lokal testen. Dafür braucht man:

- Eine lokale Postgresql Installation (Version 14), am einfachsten
ohne Authentifizierung (siehe z.B. https://wiki.ubuntuusers.de/PostgreSQL/).
  - Installiere Postgresql mit Ubuntu/Debian als folgt:
    ```shell
    apt install postgresql-14
    ```
  - Man kann die Authentifizierung in Linux ausschalten, wenn man
  in `/etc/postgresql/14/main/pg_hba.conf` alle lokale Verbindungen
  auf 'trust' setzt und alle anderen auf 'reject'. Siehe Konfigdatei [development_files/pg_hba.conf]()
- Der beobgrp_site Datenbank restored (siehe oben).
- Der User 'wagtail' existiert: `createuser -U postgres wagtail`.

Dann kann man Wagtail im Entwicklermodus starten mit der folgenden Kommandozeile
im project folder:

```shell
python manage.py runserver 8001
```

und die Website auf http://localhost:8001 erreichen. 
Nach jeder Änderung wird die Site neu geladen.