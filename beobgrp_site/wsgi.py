"""
WSGI config for beobgrp_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Check for the PRODUCTION_VERSION environment variable
if os.environ.get("PRODUCTION_VERSION", "false").lower() == "true":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beobgrp_site.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beobgrp_site.settings.dev")

application = get_wsgi_application()
