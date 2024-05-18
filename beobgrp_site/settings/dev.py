from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-!u_@xog2y_uyogb5kr699n4pa2i^ls-guaj-m#(b_@xcmqp$io"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = [".beobachtergruppe.de"]
CSRF_TRUSTED_ORIGINS = ["https://testwww.beobachtergruppe.de"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
