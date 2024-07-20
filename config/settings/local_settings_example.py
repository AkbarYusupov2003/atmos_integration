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
