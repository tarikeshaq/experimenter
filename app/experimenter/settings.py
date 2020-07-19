"""
Django settings for experimenter.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from decouple import config
from urllib.parse import urljoin
from celery.schedules import crontab


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

DEV_USER_EMAIL = "dev@example.com"

NORMANDY_DEFAULT_CHANGELOG_USER = "unknown-user@normandy.mozilla.com"

KINTO_DEFAULT_CHANGELOG_USER = "experimenter@experimenter.services.mozilla.com"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

HOSTNAME = config("HOSTNAME")

ALLOWED_HOSTS = [HOSTNAME]

if DEBUG:
    ALLOWED_HOSTS += ["localhost", "nginx"]  # pragma: no cover

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.forms",
    # Libraries
    "corsheaders",
    "django_markdown2",
    "raven.contrib.django.raven_compat",
    "rest_framework",
    "widget_tweaks",
    # Experimenter
    "experimenter.base",
    "experimenter.experiments",
    "experimenter.kinto",
    "experimenter.normandy",
    "experimenter.notifications",
    "experimenter.openidc",
    "experimenter.projects",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dockerflow.django.middleware.DockerflowMiddleware",
    "experimenter.openidc.middleware.OpenIDCAuthMiddleware",
]

ROOT_URLCONF = "experimenter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"), os.path.join(BASE_DIR, "docs")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "experimenter.base.context_processors.google_analytics",
                "experimenter.base.context_processors.features",
            ],
            "debug": DEBUG,
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "experimenter.wsgi.application"

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASS"),
        "HOST": config("DB_HOST"),
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

OPENIDC_EMAIL_HEADER = config("OPENIDC_HEADER")
OPENIDC_AUTH_WHITELIST = (
    "experiments-api-list",
    "experiments-api-recipe",
    "experiments-api-detail",
)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(os.path.join(BASE_DIR, "served"), "static")

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


LOGGING_CONSOLE_LEVEL = config("LOGGING_CONSOLE_LEVEL", default="DEBUG")

# Logging

LOGGING_USE_JSON = config("LOGGING_USE_JSON", cast=bool, default=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "mozlog": {
            "()": "dockerflow.logging.JsonLogFormatter",
            "logger_name": "experimenter",
        },
        "verbose": {"format": "%(levelname)s %(asctime)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": LOGGING_CONSOLE_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "mozlog" if LOGGING_USE_JSON else "verbose",
        }
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"] if DEBUG else [],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}


# Sentry configuration
if not DEBUG:
    RAVEN_CONFIG = {
        "dsn": config("SENTRY_DSN"),
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        # 'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }


# Django Rest Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "experimenter.openidc.middleware.OpenIDCRestFrameworkAuthenticator",
    ),
}

# CORS Security Header Config
CORS_ORIGIN_ALLOW_ALL = True

# reDash Rate Limit
# Number of dashboards to deploy per hour
DASHBOARD_RATE_LIMIT = 2

# Experiments list pagination
EXPERIMENTS_PAGINATE_BY = config("EXPERIMENTS_PAGINATE_BY", default=10, cast=int)

USE_GOOGLE_ANALYTICS = config("USE_GOOGLE_ANALYTICS", default=True, cast=bool)

# Automated email destinations

# Email configuration
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_SENDER = config("EMAIL_SENDER")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = not DEBUG
EMAIL_USE_SSL = False

# Email to send to when an experiment is ready for review
EMAIL_REVIEW = config("EMAIL_REVIEW")

# Email to send to when an experiment is ready to ship
EMAIL_SHIP = config("EMAIL_SHIP")

# Email to send to when an experiment is being signed-off
EMAIL_RELEASE_DRIVERS = config("EMAIL_RELEASE_DRIVERS")

# Bugzilla API Integration
BUGZILLA_HOST = config("BUGZILLA_HOST")
BUGZILLA_API_KEY = config("BUGZILLA_API_KEY")
BUGZILLA_CC_LIST = config("BUGZILLA_CC_LIST")
BUGZILLA_CREATE_PATH = "/rest/bug"
BUGZILLA_CREATE_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, BUGZILLA_CREATE_PATH), api_key=BUGZILLA_API_KEY
)
BUGZILLA_DETAIL_URL = urljoin(BUGZILLA_HOST, "/show_bug.cgi?id={id}")
BUGZILLA_UPDATE_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, "/rest/bug/{id}"), api_key=BUGZILLA_API_KEY
)

BUGZILLA_USER_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, "/rest/user/{email}"), api_key=BUGZILLA_API_KEY
)

BUGZILLA_BUG_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, "/rest/bug?id={bug_id}"), api_key=BUGZILLA_API_KEY
)
BUGZILLA_COMMENT_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, "/rest/bug/{id}/comment"), api_key=BUGZILLA_API_KEY
)

# DS Issue URL
DS_ISSUE_HOST = config("DS_ISSUE_HOST")

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")
REDIS_DB = config("REDIS_DB")

# Celery
CELERY_BROKER_URL = "redis://{host}:{port}/{db}".format(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB
)
CELERY_BEAT_SCHEDULE = {
    "experiment_status_ready_to_ship_task": {
        "task": "experimenter.normandy.tasks.update_recipe_ids_to_experiments",
        "schedule": config("CELERY_SCHEDULE_INTERVAL", default=300, cast=int),
    },
    "experiment_status_launched_task": {
        "task": "experimenter.normandy.tasks.update_launched_experiments",
        "schedule": config("CELERY_SCHEDULE_INTERVAL", default=300, cast=int),
    },
    "check_kinto_push_queue_task": {
        "task": "experimenter.kinto.tasks.check_kinto_push_queue",
        "schedule": config("CELERY_SCHEDULE_INTERVAL", default=300, cast=int),
    },
}

# Normandy Configuration
NORMANDY_SLUG_MAX_LEN = 80

# Monitoring
MONITORING_URL = (
    "https://grafana.telemetry.mozilla.org/d/XspgvdxZz/"
    "experiment-enrollment?orgId=1&var-experiment_id={slug}"
    "&from={from_date}&to={to_date}"
)

# Statsd via Markus
STATSD_BACKEND = config(
    "STATSD_BACKEND", default="markus.backends.datadog.DatadogMetrics"
)
STATSD_HOST = config("STATSD_HOST")
STATSD_PORT = config("STATSD_PORT")
STATSD_PREFIX = config("STATSD_PREFIX")

MARKUS_BACKEND = [
    {
        "class": STATSD_BACKEND,
        "options": {
            "statsd_host": STATSD_HOST,
            "statsd_port": STATSD_PORT,
            "statsd_namespace": STATSD_PREFIX,
        },
    }
]

# Normandy URLs
DELIVERY_CONSOLE_HOST = config("DELIVERY_CONSOLE_HOST")
DELIVERY_CONSOLE_NEW_RECIPE_URL = urljoin(DELIVERY_CONSOLE_HOST, "/recipe/new/")
DELIVERY_CONSOLE_RECIPE_URL = urljoin(DELIVERY_CONSOLE_HOST, "/recipe/{id}/")
DELIVERY_CONSOLE_EXPERIMENT_IMPORT_URL = urljoin(
    DELIVERY_CONSOLE_HOST, "/recipe/import/{slug}/"
)
NORMANDY_API_HOST = config("NORMANDY_API_HOST")
NORMANDY_API_RECIPE_URL = urljoin(NORMANDY_API_HOST, "/api/v3/recipe/{id}/")
NORMANDY_API_RECIPES_LIST_URL = urljoin(NORMANDY_API_HOST, "/api/v3/recipe/")

# Jira URL
JIRA_URL = config(
    "JIRA_URL",
    default="https://moz-pi-test.atlassian.net/servicedesk/customer/portal/9",
)


SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)
SECURE_REFERRER_POLICY = config("SECURE_REFERRER_POLICY", default="origin")

# Silenced ssl_redirect and sts checks
SILENCED_SYSTEM_CHECKS = ["security.W008", "security.W004"]

# Feature Flags
FEATURE_MESSAGE_TYPE = config("FEATURE_MESSAGE_TYPE", default=False, cast=bool)

# Kinto settings
KINTO_HOST = config("KINTO_HOST")
KINTO_USER = config("KINTO_USER")
KINTO_PASS = config("KINTO_PASS")
KINTO_BUCKET = config("KINTO_BUCKET")
KINTO_COLLECTION = config("KINTO_COLLECTION")
