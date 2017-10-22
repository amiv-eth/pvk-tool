"""Configuration."""

# AMIVAPI URL and Admin Group
AMIVAPI_URL = "https://amiv-api.ethz.ch"
ADMIN_GROUP_NAME = 'PVK Admins'

# DB
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = 'pvkuser'
MONGO_PASSWORD = 'pvkpass'
MONGO_DBNAME = 'pvk'


RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']


# ISO 8601 time format instead of rfc1123
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


# A schema for required start/end time tuple
TIMESPAN = {
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


# Resources
DOMAIN = {
    'lectures': {
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
        },
    },

    'assistants': {
        'schema': {
            'nethz': {
                'type': 'string',
                'maxlength': 10,
                'unique': True,
                'empty': False,
                'nullable': False,
                'required': True,
            },
            'name': {
                'type': 'string',
                'readonly': True,
            },
        },
    },
    'courses': {
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
                'type': 'objectid',
                'data_relation': {
                    'resource': 'assistants',
                    'field': '_id',
                    'embeddable': True
                },
            },

            'signup': TIMESPAN,

            'datetimes': {
                'type': 'list',
                'schema': TIMESPAN,
            },
            'room': {
                'type': 'string',
                'maxlength': 100,
                'unique': True,
                'required': True,
                'nullable': False,
                'empty': False,
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
            },
            'status': {
                'type': 'string',
                'allowed': ['waiting', 'accepted', 'accepted+paid'],
                'readonly': True,
            },
        },
    }
}
