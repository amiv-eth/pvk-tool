"""PVK Tool Backend.

Here, the main app object is created.
The `create_app` function exists so that we can create apps with different
settings for tests (i.e. using a test database).

Next, you should check out the following files:

- `settings.py`:
  The data model and `Eve` configuration.

- `security.py`:
  Authentication is defined here, in particular the interaction with AMIVAPI.

- `signups.py`:
  Processing of signups: waiting list, payments, etc.

"""

from os import getcwd
from eve import Eve
from flask import Config

from security import APIAuth, only_own_nethz
from validation import APIValidator
from signups import (
    new_signups,
    deleted_signup,
    patched_signup,
    patched_course,
    block_course_deletion,
    mark_as_paid,
)


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

    # Also use hooks to add pre- and postprocessing to resources
    application.on_post_POST_signups += new_signups
    application.on_deleted_item_signups += deleted_signup
    application.on_updated_signups += patched_signup

    application.on_updated_courses += patched_course
    application.on_delete_item_courses += block_course_deletion

    application.on_inserted_payments += mark_as_paid

    return application


app = create_app()  # pylint: disable=C0103
