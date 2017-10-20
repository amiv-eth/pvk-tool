"""The main app."""

from os import getcwd
from eve import Eve
from flask import Config


def create_app(settings=None):
    """Super simply bootstrapping for easier testing."""
    config = Config(getcwd())
    config.from_object('settings')
    if settings is not None:
        config.update(settings)
    return Eve(settings=config)


app = create_app()
