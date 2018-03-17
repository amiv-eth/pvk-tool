"""Data Model and General Configuration of Eve.

Check out [the Eve docs for configuration](http://python-eve.org/config.html)
if you are unsure about some of the settings.

Our schema requires customized data validation. These validation rules are
implemented in `validation.py`.
Some validation rules are still missing, they are marked with TODO in the
schema directly.
"""

from os import environ

# CORS
X_DOMAINS = '*'
X_HEADERS = ['Authorization', 'If-Match', 'If-Modified-Since', 'Content-Type']

# AMIVAPI URL and Admin Group
AMIVAPI_URL = 'https://amiv-api.ethz.ch'
ADMIN_GROUP_NAME = 'PVK Admins'

# DB (can be set by env for easier CI tests)
MONGO_HOST = environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = environ.get('MONGO_PORT', 27017)
MONGO_DBNAME = environ.get('MONGO_DBNAME', 'pvk')
MONGO_USERNAME = environ.get('MONGO_USERNAME', 'pvkuser')
MONGO_PASSWORD = environ.get('MONGO_PASSWORD', 'pvkpass')


# Only JSON, simplifies hooks
XML = False


RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']


# Stripe API Key
# TODO: Not a good idea to keep this in the repo
STRIPE_API_KEY = 'sk_test_KUiZO8E2VKGMmm94u4t5YPnL'


# Price per course in "rappen"
COURSE_PRICE = 1000


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
        # exactly like singups, but without status

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
        },
    },

    'payments': {
        # Endpoint for payments via Stripe.

        # charge_id is a unique identifier which allows us to track the payment with Stripe
        # Admins can however create payments without a charge_id

        # Only admins can delete payments
        # Also, there is no reason to ever change a payment.
        'user_methods': ['GET', 'POST'],

        # Bulk inserts don't make sense here, so we disallow them
        'bulk_enabled': False,

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
                    'no_waiting': True, # No signups on waiting list
                    'no_accepted': True, # No signups which have already been paid
                },
                'no_copies': True,
                'required': True,
                'nullable': False,
            },
            # Admins may leave this field empty
            # However, it still has to be sent, even if it contains an empty string / None
            'token': {
                'type': 'string',
                'unique': True,
                'required': True,
                'nullable': True,
                'only_admin_empty': True,
            },
            'charge_id': { # Set by backend
                'type': 'string',
                'unique': True,
                'required': False,
                'nullable': True,
            },
            'amount': { # Set by backend
                'type': 'integer',
                'required': False,
                'nullable': True,
            }
        }
    }
}
