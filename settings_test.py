# Minimal settings for running tests without external service dependencies.
import os
import sys
import types


# ---------------------------------------------------------------------------
# Stub out third-party packages that are not installed in the test environment
# so that apps importing them can still be loaded.
# ---------------------------------------------------------------------------
def _install_stubs():
    stubs = [
        'challonge', 'challonge.tournaments', 'challonge.participants', 'challonge.matches',
        'celery', 'djcelery',
        'registration', 'registration.forms', 'registration.urls',
    ]
    for name in stubs:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    sys.modules['challonge'].set_credentials = lambda *a, **kw: None
    sys.modules['challonge'].tournaments = types.ModuleType('challonge.tournaments')
    sys.modules['challonge'].tournaments.create = lambda **kw: None
    sys.modules['challonge'].tournaments.destroy = lambda **kw: None
    sys.modules['challonge'].tournaments.publish = lambda **kw: None
    sys.modules['challonge'].tournaments.start = lambda **kw: None
    sys.modules['challonge'].participants = types.ModuleType('challonge.participants')
    sys.modules['challonge'].participants.create = lambda **kw: None
    sys.modules['challonge'].participants.destroy = lambda **kw: None
    sys.modules['challonge'].participants.index = lambda *a, **kw: []
    sys.modules['challonge'].matches = types.ModuleType('challonge.matches')
    sys.modules['challonge'].matches.index = lambda *a, **kw: []

    def _task(*args, **kwargs):
        def decorator(f):
            f.delay = f
            return f
        if args and callable(args[0]):
            return decorator(args[0])
        return decorator

    sys.modules['celery'].task = _task
    sys.modules['djcelery'].setup_loader = lambda: None

    # registration.forms must expose RegistrationFormUniqueEmail as a Form
    from django import forms as _forms
    class _RegistrationFormUniqueEmail(_forms.Form):
        pass
    sys.modules['registration.forms'].RegistrationFormUniqueEmail = _RegistrationFormUniqueEmail
    # registration.urls must expose urlpatterns
    sys.modules['registration.urls'].urlpatterns = []


_install_stubs()
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = False
SECRET_KEY = 'test-secret-key-for-tests-only'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'paypal.standard.ipn',
    'localflavor',
    'events',
    'sponsorship',
    'seatmap',
    'pages',
    'tournaments',
    'schedule',
)

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'urls_test'

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')
MEDIA_URL = '/media/'

# Authentication
AUTHENTICATION_BACKENDS = (
    'backends.CaseInsensitiveModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGIN_URL = '/accounts/login/'

# Stripe (test keys, never real values)
STRIPE_SECRET_KEY = 'sk_test_placeholder'
STRIPE_PUBLISHABLE_KEY = 'pk_test_placeholder'

# PayPal
PAYPAL_RECEIVER_EMAIL = 'test@example.com'

# Challonge
CHALLONGE_USERNAME = 'testuser'
CHALLONGE_API_KEY = 'testapikey'

# Mandrill / Email
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'test@example.com'

# recaptcha
RECAPTCHA_PUBLIC_KEY = 'test_public_key'
RECAPTCHA_PRIVATE_KEY = 'test_private_key'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Disable migrations during tests – build the schema directly from models
MIGRATION_MODULES = {
    'auth': None,
    'contenttypes': None,
    'sessions': None,
    'sites': None,
    'admin': None,
    'flatpages': None,
    'ipn': None,
    'events': None,
    'sponsorship': None,
    'seatmap': None,
    'pages': None,
    'tournaments': None,
    'schedule': None,
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
