"""
Conftest-equivalent: mock out third-party modules that are not installed in the
test environment (challonge, celery) before Django starts, so that the apps
that import them can still be loaded and tested.

This file is imported automatically by Django's test runner because it lives
in the project root and is listed as a conftest-style helper that the test
settings can reference.  For the actual entry-point we rely on settings_test.py
setting DJANGO_SETTINGS_MODULE before Django starts.
"""
import sys
import types


def _install_mocks():
    """Install lightweight stubs for unavailable third-party packages."""
    stubs = [
        'challonge',
        'challonge.tournaments',
        'challonge.participants',
        'challonge.matches',
        'celery',
    ]
    for name in stubs:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    # challonge.set_credentials must be callable
    sys.modules['challonge'].set_credentials = lambda *a, **kw: None

    # celery.task must work as a decorator (with and without arguments)
    def _task(*args, **kwargs):
        def decorator(f):
            f.delay = f
            return f
        if args and callable(args[0]):
            return decorator(args[0])
        return decorator

    sys.modules['celery'].task = _task


_install_mocks()
