"""The main app.

Check settings.py for the resource schema and API configuration.
"""

from os import getcwd
from eve import Eve
from flask import Config

from auth import APIAuth, APIValidator, only_own_signups


def create_app(settings=None):
    """Super simply bootstrapping for easier testing."""
    config = Config(getcwd())
    config.from_object('settings')
    if settings is not None:
        config.update(settings)
    application = Eve(auth=APIAuth, validator=APIValidator, settings=config)

    for method in ['GET', 'PATCH', 'DELETE']:
        event = getattr(application, 'on_pre_%s_signups' % method)
        event += only_own_signups

    return application


app = create_app()
