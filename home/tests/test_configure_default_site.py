import os
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, Site


class ConfigureDefaultSiteTest(TestCase):
    def test_sets_default_site_from_environment(self):
        with mock.patch.dict(os.environ, {"SITE_HOSTNAME": "localhost", "SITE_PORT": "8001"}):
            call_command("configure_default_site", stdout=StringIO())

        default_site = Site.objects.get(is_default_site=True)
        self.assertEqual(default_site.hostname, "localhost")
        self.assertEqual(default_site.port, 8001)
        self.assertEqual(Site.objects.filter(is_default_site=True).count(), 1)

    def test_reuses_existing_site_with_same_hostname_and_port(self):
        root = Page.get_first_root_node()
        other = Site.objects.create(hostname="localhost", port=8001, root_page=root)
        with mock.patch.dict(os.environ, {"SITE_HOSTNAME": "localhost", "SITE_PORT": "8001"}):
            call_command("configure_default_site", stdout=StringIO())

        other.refresh_from_db()
        self.assertTrue(other.is_default_site)
        self.assertEqual(Site.objects.filter(is_default_site=True).count(), 1)

    def test_leaves_default_site_on_testwww_without_hostname(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            call_command("configure_default_site", stdout=StringIO())

        default_site = Site.objects.get(is_default_site=True)
        self.assertEqual(default_site.hostname, "testwww.beobachtergruppe.de")
