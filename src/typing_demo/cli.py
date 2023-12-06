import pathlib
from functools import partial

import click


class Command(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.extend([
            click.Option(
                ("config_file_fp", "-c", "--config-file"),
                type=str,
                default="config.toml",
                help="Configuration file.",
            ),
            click.Option(
                ("logconfig", "--log-config"),
                type=str,
                default="logging.ini",
                help="Logging configuration file.",
            ),
            click.Option(
                ("--debug/--no-debug",),
                default=False,
                help="Enable debug mode."
            )
        ])

    def make_context(self, *args, **kwargs):
        ctx = super().make_context(*args, **kwargs)
        config_file_fp = ctx.params["config_file_fp"]
        config_file = pathlib.Path(config_file_fp).expanduser()
        if not config_file.exists():
            raise ValueError(f"Configuration file not found at {str(config_file)}.")

        from typing_demo.config import configure

        with open(config_file) as config_fo:
            config = configure(config_fo, debug=ctx.params['debug'], logconfig=ctx.params['logconfig'])
            ctx.obj = config

        return ctx


class Group(click.Group):
    command_class = Command


group = partial(click.group, cls=Group)
command = partial(click.command, cls=Command)


@group()
def cli():
    pass


@cli.command(
    add_help_option=False, context_settings=dict(ignore_unknown_options=True)
)
@click.argument("management_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def django(ctx, management_args, **options):
    """Execute Django subcommands."""

    from django.core.management import execute_from_command_line
    execute_from_command_line(argv=[ctx.command_path] + list(management_args))


def make_django_command(name, django_command=None, help=None):
    """A wrapper to convert a Django subcommand a Click command."""

    if django_command is None:
        django_command = name

    @command(
        name=name,
        help=help,
        add_help_option=False,
        context_settings=dict(ignore_unknown_options=True),
    )
    @click.argument("management_args", nargs=-1, type=click.UNPROCESSED)
    @click.pass_context
    def inner(ctx, management_args, **options):
        ctx.params["management_args"] = (django_command,) + management_args
        ctx.forward(django)

    return inner


cli.add_command(
    make_django_command("shell", help="Run a Python interactive interpreter.")
)


@cli.command(
    add_help_option=True,
    context_settings={"ignore_unknown_options": True},
    help="Start gunicorn web server.",
)
@click.argument("gunicorn_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def start_server(ctx, gunicorn_args, **options):
    """A workaround solution to run the server by ourselves.
    As we already configure the logging so we custom logger class which dont do any setup
    and gunicorn doesn't log any accesslog if non of the log config flag set.
    """
    import importlib
    import sys

    sys.argv = ["gunicorn", "__main__:webapp", *gunicorn_args, "--logger-class", "typing_demo.gunicorn.Logger", "--log-config", "/dev/null"]

    from typing_demo.web import WebApplication, AppData

    main_module = importlib.import_module("__main__")
    webapp = WebApplication().app_data(AppData(ctx.obj))
    main_module.webapp = webapp

    from gunicorn.app.wsgiapp import run
    run()
