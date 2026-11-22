from django.conf import settings


def development_build(request):
    is_development = not settings.IS_PRODUCTION_VERSION or settings.APP_VERSION.endswith(".dev")
    return {
        "show_development_banner": is_development,
        "app_version": settings.APP_VERSION,
    }
