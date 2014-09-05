# -*- coding: utf-8 -*-
import os.path
import sys
import re
import djcelery
djcelery.setup_loader()

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['.bigshotgaming.com']

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bigshotgaming',                      # Or path to database file if using sqlite3.
        'USER': 'bigshotgaming',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
BROKER_URL = 'redis://localhost:6379/0'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Detroit'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'France'),
    ('lt', 'Lithuanian'),
    ('pl', 'Polish'),
    ('ru', 'Russian'),
    ('zh_CN', 'Chinese'),
    ('de', 'German'),
    ('vi', 'Vietnamese'),
    ('it', 'Italian'),
    ('cs', 'Czech'),
    ('ca', 'Catalan'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/usr/share/nginx/www/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'https://www.bigshotgaming.com/media/'

STATIC_ROOT = '/usr/share/nginx/www/static/'
STATIC_URL = 'https://www.bigshotgaming.com/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL+'admin/'


# Make this unique, and don't share it with anybody.

if not hasattr(globals(), 'SECRET_KEY'):
    SECRET_FILE = os.path.join(PROJECT_ROOT, 'secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            from random import choice
            import string
            symbols = ''.join((string.lowercase, string.digits, string.punctuation ))
            SECRET_KEY = ''.join([choice(symbols) for i in range(50)])
            secret = file(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            raise Exception('Please create a %s file with random characters to generate your secret key!' % SECRET_FILE)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',

)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

ACCOUNT_ACTIVATION_DAYS = 7

AUTHENTICATION_BACKENDS = ('backends.CaseInsensitiveModelBackend',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'django_nvd3',
    'raven.contrib.django',
    'djcelery',
    'djrill',
    'gunicorn',
    'registration',
    'events',
    'sponsorship',
    'seatmap',
    'paypal.standard.ipn',
    'pages',
    'tournaments',
    'schedule',
)

EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'

try:
    import south
    INSTALLED_APPS += ('south',)
    SOUTH_TESTS_MIGRATE = False
except ImportError:
    pass

FORCE_SCRIPT_NAME = ''

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    'joomla_password_hasher.JoomlaPasswordHasher' 
)

# Account settings
ACCOUNT_ACTIVATION_DAYS = 10
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

#Cache settings
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

RECAPTCHA_PUBLIC_KEY = None
RECAPTCHA_PRIVATE_KEY = None
CHALLONGE_USERNAME = None
CHALLONGE_API_KEY = None

MANDRILL_API_KEY = None

SERVER_EMAIL = 'Big Shot Gaming <bigshot@bigshotgaming.com>'
DEFAULT_FROM_EMAIL = 'Big Shot Gaming <bigshot@bigshotgaming.com>'

try:
    from local_settings import *
except ImportError:
    pass
