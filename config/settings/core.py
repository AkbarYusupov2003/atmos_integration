from pathlib import Path
from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from .local_settings import *
except ImportError:
    SECRET_KEY = "123"
    DEBUG = True
    ALLOWED_HOSTS = []
    # Atmos
    ATMOS_STORE_ID = 1
    ATMOS_CONSUMER_KEY = ""
    ATMOS_CONSUMER_SECRET = ""
    #
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "atmos_integration",
            "USER": "postgres",
            "PASSWORD": "123456",
            "HOST": "localhost",
            "PORT": "5432",
        },
    }

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "rest_framework",
    "drf_yasg",
    # my apps
    "payment",
]

MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru"

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ("ru", _("Русский")),
    ("en", _("English")),
    ("oz", _("Uzbek (Latin)")),
    ("uz", _("Uzbek (Cyrillic)")),
)

LOCALES = {
    "ru": "Russian",
    "en": "English",
    "oz": "Uzbek (Latin)",
    "uz": "Uzbek (Cyrillic)",
}

LOCALE_PATHS = (str(BASE_DIR / "locales"),)

STATIC_URL = "static/"
STATIC_DIR = BASE_DIR / "static_dev"
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

SWAGGER_SETTINGS = {"USE_SESSION_AUTH": False}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    )
}
