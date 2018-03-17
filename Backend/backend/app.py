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

from os import getcwd, getenv
from os.path import abspath
from eve import Eve
from flask import Config

from backend.security import APIAuth, only_own_nethz
from backend.validation import APIValidator
from backend.signups import (
    new_signups,
    deleted_signup,
    patched_signup,
    patched_course,
    block_course_deletion,
    mark_as_paid,
)


def create_app(config_file=None, **kwargs):
    """Create a new eve app object and initialize everything.

    User configuration can be loaded in the following order:

    1. Use the `config_file` arg to specify a file
    2. If `config_file` is `None`, you set the environment variable
       `PVK_CONFIG` to the path of your config file
    3. If no environment variable is set either, `config.py` in the current
       working directory is used

    Args:
        config (path): Specify config file to use.
        kwargs: All other key-value arguments will be used to update the config
    Returns:
        (Eve): The Eve application
    """
    # Load config
    config = Config(getcwd())
    config.from_object("backend.settings")

    # Specified path > environment var > default path; abspath for better log
    user_config = abspath(config_file or getenv('PVK_CONFIG', 'config.py'))
    try:
        config.from_pyfile(user_config)
        config_status = "Config loaded: %s" % user_config
    except IOError:
        config_status = "No config found."

    config.update(kwargs)

    # Create the app object
    application = Eve(auth=APIAuth, validator=APIValidator, settings=config)
    application.logger.info(config_status)

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
