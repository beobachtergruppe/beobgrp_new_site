# Website Beobachtergruppe

Dieses Project enhält die neue Website der Beobachtergruppe, welche auf wagtail
basiert is.

## Installation

Die Website kann einfach mit einem docker compose setup gestartet werden:

Definiere das Passwort in der folgenden Environment Variable:

```shell
export WAGTAIL_DB_PASSWORD="some_password"
```

Im Project Folder:

```shell
docker compose up -d
```

Dann ist die Site auf https://localhost:8000 erreichbar.

## Weitere Konfiguration

Mit `docker compose` Kommandozeilen kann man die Services 'wagtail' und 
'postgres' erreichen und z.B. wagtail Kommandos mit `docker compose exec` ausführen.

