"""PVK Tool Backend.

Here, the main app object is created.
The `create_app` function exists so that we can create apps with different
settings for tests (i.e. using a test database).

Next, you should check out the following files:

- `settings.py`:
  The data model and `Eve` configuration.

- `security.py`:
  Authentication is defined here, in particular the interaction with AMIVAPI.
"""

from os import getcwd
from eve import Eve
from flask import Config

from security import APIAuth, only_own_nethz
from validation import APIValidator


def create_app(settings=None):
    """Super simply bootstrapping for easier testing.

    Initial settings are loaded from settings.py (the Flask `Config` object
    makes this easy) and updated settings from the function call, if provided.
    """
    config = Config(getcwd())
    config.from_object('settings')
    if settings is not None:
        config.update(settings)

    # Create the app object
    application = Eve(auth=APIAuth, validator=APIValidator, settings=config)

    # Eve provides hooks at several points of the request,
    # we use this do add dynamic filtering
    for resource in ['signups', 'selections']:
        for method in ['GET', 'PATCH', 'DELETE']:
            event = getattr(application,
                            'on_pre_%s_%s' % (method, resource))
            event += only_own_nethz

    return application


app = create_app()  # pylint: disable=C0103
