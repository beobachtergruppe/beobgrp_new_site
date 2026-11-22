import os

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site


class Command(BaseCommand):
    help = (
        "Set hostname and port of the default Wagtail Site from the SITE_HOSTNAME "
        "and SITE_PORT environment variables. Defaults are testwww.beobachtergruppe.de and port 443 (https)."
    )

    def handle(self, *args, **options):
        hostname = os.environ.get("SITE_HOSTNAME", "testwww.beobachtergruppe.de")
        port = int(os.environ.get("SITE_PORT", "443"))

        # Reuse an existing site with this hostname and port (hostname+port is unique),
        # otherwise repurpose the current default site.
        site = Site.objects.filter(hostname=hostname, port=port).first()
        if site is None:
            site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
            if site is None:
                raise CommandError("No Wagtail Site exists in the database to configure.")
            site.hostname = hostname
            site.port = port

        site.is_default_site = True
        site.save()
        Site.objects.exclude(pk=site.pk).update(is_default_site=False)
        self.stdout.write(f"Default site set to {site.hostname}:{site.port}")
