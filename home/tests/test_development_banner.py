from django.test import RequestFactory, SimpleTestCase, override_settings

from beobgrp_site.context_processors.development_build import development_build


class DevelopmentBuildBannerTest(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")

    @override_settings(IS_PRODUCTION_VERSION=True, APP_VERSION="1.7.1")
    def test_banner_hidden_for_production_build(self):
        context = development_build(self.request)
        self.assertFalse(context["show_development_banner"])

    @override_settings(IS_PRODUCTION_VERSION=True, APP_VERSION="1.7.1.dev")
    def test_banner_shown_for_dev_build_in_production_mode(self):
        context = development_build(self.request)
        self.assertTrue(context["show_development_banner"])
        self.assertEqual(context["app_version"], "1.7.1.dev")

    @override_settings(IS_PRODUCTION_VERSION=False, APP_VERSION="1.7.1")
    def test_banner_shown_outside_production_mode(self):
        context = development_build(self.request)
        self.assertTrue(context["show_development_banner"])
