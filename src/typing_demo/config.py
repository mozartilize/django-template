import logging.config
import pathlib
import typing as t
from dataclasses import dataclass

from pydantic import BaseModel, Field
from django.conf import LazySettings
from django.core.management.utils import get_random_secret_key


@dataclass
class AppConfiguration:
    secret_key: str
    logconfig: str
    debug: bool
    django: LazySettings


class AppF(BaseModel):
    secret_key: str = Field(default_factory=get_random_secret_key)
    debug: t.Optional[bool] = None
    logconfig: t.Optional[str] = None


class DjangoF(BaseModel):
    pass


class AppConfigurationF(BaseModel):
    app: AppF = Field(default=AppF())
    django: DjangoF = Field(default=DjangoF())


def configure_logging(logconfig: str, debug: t.Optional[bool] = None):
    fp = pathlib.Path(logconfig).expanduser()
    logging.config.fileConfig(str(fp))

    if debug:
        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)


def configure(config_fo: t.Optional[t.TextIO] = None, debug: t.Optional[bool] = None, logconfig: t.Optional[str] = None):
    import toml
    from django import setup as setup_django
    from django.conf import settings as django_settings

    if config_fo:
        config_from_file_data = toml.load(config_fo)
        config_from_file = AppConfigurationF(**config_from_file_data)
    else:
        config_from_file = AppConfigurationF()

    if logconfig is not None:
        config_from_file.app.logconfig = logconfig

    if debug is not None:
        config_from_file.app.debug = debug

    if config_from_file.app.logconfig:
        configure_logging(config_from_file.app.logconfig, config_from_file.app.debug)

    DJANGO_DEFAULT: dict[str, t.Any] = {
        "ROOT_URLCONF": "typing_demo.web",
        "LOGGING_CONFIG": None,
        "LOGGING": None,
        "DEBUG": config_from_file.app.debug or False,
        "SECRET_KEY": config_from_file.app.secret_key,
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

    return AppConfiguration(**config_from_file.app.model_dump(), django=django_settings)
