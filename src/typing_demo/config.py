import typing as t
from dataclasses import dataclass

from django.conf import LazySettings


@dataclass
class AppConfiguration:
    secret_key: str
    django: LazySettings


def configure(config_fo: t.Optional[t.TextIO] = None):
    import toml
    from django import setup as setup_django
    from django.conf import settings as django_settings

    # config_from_file = toml.load(config_fo)

    DJANGO_DEFAULT: dict[str, t.Any] = {
        "ROOT_URLCONF": "typing_demo.web",
        "LOGGING_CONFIG": None,
        "LOGGING": None,
        "DEBUG": False,
        "SECRET_KEY": 'hmm',
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "db.sqlite3"
            }
        },
        "INSTALLED_APPS": [
            "django_extensions",
            "typing_demo",
        ]
    }
    django_settings.configure(**DJANGO_DEFAULT)
    setup_django(set_prefix=False)

    return AppConfiguration(secret_key='hmm', django=django_settings)
