"""Data Model and General Configuration of Eve.

Check out [the Eve docs for configuration](http://python-eve.org/config.html)
if you are unsure about some of the settings.

Our schema requires customized data validation. These validation rules are
implemented in `validation.py`.
Some validation rules are still missing, they are marked with TODO in the
schema directly.
"""

from os import environ

# prefix everything with /api
URL_PREFIX = 'api'

# CORS
X_DOMAINS = '*'
X_HEADERS = ['Authorization', 'If-Match', 'If-Modified-Since', 'Content-Type']

# AMIVAPI URL and Admin Group
AMIVAPI_URL = "https://amiv-api.ethz.ch"
ADMIN_GROUP_NAME = 'PVK Admins'

# DB
MONGO_HOST = environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = environ.get('MONGO_PORT', 27017)
MONGO_DBNAME = environ.get('MONGO_DBNAME', 'pvk')
MONGO_USERNAME = environ.get('MONGO_USERNAME', 'pvkuser')
MONGO_PASSWORD = environ.get('MONGO_PASSWORD', 'pvkpass')

# Only JSON, simplifies hooks
XML = False


RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']


# ISO 8601 time format instead of rfc1123
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


# More Feedback when creating something: Return all fields
BANDWIDTH_SAVER = False


# A schema for required start/end time tuple
TIMESPAN_SCHEMA = {
    'type': 'dict',
    'schema': {
        'start': {
            'type': 'datetime',
            'nullable': False,
            'required': True,
        },
        'end': {
            'type': 'datetime',
            'nullable': False,
            'required': True,
        },
    },
}


# Same as Eve, but include 403
STANDARD_ERRORS = [400, 401, 403, 404, 405, 406, 409, 410, 412, 422, 428]


# Resources
DOMAIN = {
    'lectures': {

        'user_methods': ['GET'],

        'schema': {
            'title': {
                'type': 'string',
                'maxlength': 100,
                'unique': True,
                'required': True,
                'nullable': False,
                'empty': False,
            },
            'department': {
                'type': 'string',
                'allowed': ['itet', 'mavt'],
                'required': True,
                'nullable': False,
            },
            'year': {
                'type': 'integer',
                'min': 1,
                'max': 3,
                'required': True
            },
            'assistants': {
                # List of nethz of assistants
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'maxlength': 10,
                    'empty': False,
                    'nullable': False,
                },
                # TODO: Not the same nethz twice
                # TODO: Is nethz enough here?
            }
        },
    },

    'courses': {

        'user_methods': ['GET'],

        'schema': {
            'lecture': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'lectures',
                    'field': '_id',
                    'embeddable': True
                },
                'not_patchable': True,  # Course is tied to lecture
            },
            'assistant': {
                'type': 'string',
                # TODO: Assistant needs to exist for lecture
            },

            'signup': TIMESPAN_SCHEMA,

            'datetimes': {
                'type': 'list',
                'schema': TIMESPAN_SCHEMA,
                # TODO: Timeslots must not overlap
            },
            'room': {
                'type': 'string',
                'maxlength': 100,
                'unique': True,
                'required': True,
                'nullable': False,
                'empty': False,
                # TODO: Room must be empty for time slot
            },
            'spots': {
                'type': 'integer',
                'min': 1,
                'required': True,
                'nullable': False
            }
        },
    },

    'signups': {
        # Signup for a user to a course

        'user_methods': ['GET', 'POST', 'PATCH', 'DELETE'],

        'schema': {
            'nethz': {
                'type': 'string',
                'maxlength': 10,
                'empty': False,
                'nullable': False,
                'required': True,
                'only_own_nethz': True,
                'not_patchable': True,  # Signup is tied to user
            },
            'course': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'courses',
                    'field': '_id',
                    'embeddable': True
                },
                'unique_combination': ['nethz'],
                'required': True,
                # TODO: No overlapping courses
            },
            'status': {
                'type': 'string',
                'allowed': ['waiting', 'reserved', 'accepted'],
                'readonly': True,
                'default': 'waiting',
            },
        },
    },

    'selections': {
        # Easy way for users to safe their selections before signup is open
        # List of selected courses per user

        'user_methods': ['GET', 'POST', 'PATCH', 'DELETE'],

        'schema': {
            'nethz': {
                'type': 'string',
                'maxlength': 10,
                'empty': False,
                'nullable': False,
                'required': True,
                'only_own_nethz': True,
                'unique': True,
            },
            'courses': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'courses',
                        'field': '_id',
                        'embeddable': True
                    },
                    # TODO: No duplicate entries
                    # TODO: No entries that are already reserved
                },
            },
        },
    },

    'payments': {
        # Dummy endpoint for payments.
        # TODO: Implement as soon as PSP is known.

        # Only admins can delete payments
        'user_methods': ['GET', 'POST', 'PATCH'],

        'schema': {
            'signups': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'signups',
                        'field': '_id',
                        'embeddable': True
                    },
                    # TODO: No duplicate entries
                    # TODO: No courses on waiting list
                },
                'required': True,
                'nullable': False,
            }
        }
    }
}
