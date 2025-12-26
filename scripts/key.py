#!/usr/bin/env python

"""Django's command-line utility for secret keys."""


def main() -> None:
    """Generate a secret key."""
    try:
        from django.core.management.utils import get_random_secret_key
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    print(get_random_secret_key())


if __name__ == "__main__":
    main()
