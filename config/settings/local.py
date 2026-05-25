from .base import *  # noqa


DEBUG = True

TAILWIND_CLI_AUTOMATIC_DOWNLOAD = True

TAILWIND_CLI_DIST_CSS = "css/tailwind.css"

INSTALLED_APPS += [  # noqa
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE += [  # noqa
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
