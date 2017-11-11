"""AMIVAPI Authentication, Validation and Filtering.

All functions in here implement additional restrictions for security,
e.g. that users can only see/modify their own signups.

The important bits are:

- Several functions to access AMIVAPI

  We use the Flask `g` request globals to store results. This way, we don't
  need to worry about sending a request twice. Furthermore, we can directly set
  the values in `g` to avoid API requests during unittests.

- Authentication class working with tokens.

  Take a look at the [Eve docs](http://python-eve.org/authentication.html) for
  more info.

- Additional Validation rules

  More info [here](http://python-eve.org/validation.html).

"""

from functools import wraps
import json
import requests
from eve.auth import TokenAuth
from eve.io.mongo import Validator
from flask import request, g, current_app, abort


# Requests to AMIVAPI

def api_get(resource, where, projection):
    """Format and send a GET request to AMIVAPI. Return json data or None."""
    url = requests.compat.urljoin(current_app.config['AMIVAPI_URL'], resource)
    headers = {'Authorization': "Token %s" % g.token}
    params = {
        'where': json.dumps(where),
        'projection': json.dumps(projection)
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()


def request_cache(key):
    """Use as decorator: Cache the function return in g.key."""
    def _decorator(function):
        @wraps(function)
        def _wrapper(*args, **kwargs):
            try:
                # If the value is already in g, don't call function
                return getattr(g, key)
            except KeyError:
                setattr(g, key, function(*args, **kwargs))
                return getattr(g, key)
        return _wrapper
    return _decorator


@request_cache('user')
def get_user():
    """Return user id if the token is valid, None otherwise."""
    response = api_get('sessions', {'token': g.get('token', '')}, {'user': 1})
    if response:
        return response['_items'][0]['user']


@request_cache('nethz')
def get_nethz():
    """Return nethz of current user."""
    if get_user() is not None:
        response = api_get('users/%s' % get_user(), {}, {'nethz': 1})
        return response.get('nethz')


@request_cache('admin')
def is_admin():
    """Return True if user is in the 'PVK Admins' Group, False otherwise.

    The result is saved in g, to avoid checking twice, so there is no
    performance loss if is_admin is called multiple times during a request.
    """
    user_id = get_user()
    if user_id is not None:
        # Find Group with correct name, return list of members
        groups = api_get('groups',
                         {'name': current_app.config['ADMIN_GROUP_NAME']},
                         {'_id': 1})
        if groups:
            group_id = groups['_items'][0]['_id']

            membership = api_get('groupmemberships',
                                 {'user': user_id, 'group': group_id},
                                 {'_id': 1})

            return bool(membership and membership['_items'])

    # In all other cases, user is not an admin.
    return False


# Auth

class APIAuth(TokenAuth):
    """Verifies the request token with AMIVAPI."""

    def check_auth(self, token, allowed_roles, resource, method):
        """Allow request if token exists in AMIVAPI.

        Furthermore, grant admin rights if the user is member of the
        admin group.

        By default, Eve only returns 401, we refine this a little:
        - 401 if token missing (eve default already) or not found in AMIVAPI
        - 403 if not permitted

        """
        g.token = token  # Safe in g such that other methods can use it

        # Return 401 if token not recognized by AMIVAPI
        if get_user() is None:
            return False

        # Check Permissions, return 403 if not permitted
        # Users: Read always allowed, write only on specific resources
        # Admins: Can do all
        user_writable = ['signups', 'selections', 'payments']
        if (method == 'GET' or (resource in user_writable) or is_admin()):
            return True
        else:
            abort(403)


# Dynamic Filter

def only_own_signups(_, lookup):
    """Users can only see signups if their ID matches."""
    if not is_admin():
        # Add the additional lookup with an `$and` condition
        # or extend existing `$and`s
        lookup.setdefault('$and', []).append({'nethz': get_nethz()})


# Validation

class APIValidator(Validator):
    """Provide a rule to check nethz of current user."""

    def _validate_only_own_nethz(self, enabled, field, value):
        """If the user is no admin, only own nethz is allowed for singup."""
        if enabled and not is_admin():
            if value != get_nethz():
                self._error(field,
                            "You can only use your own nethz to sign up.")

    def _validate_unique_combination(self, unique_combination, field, value):
        """Validate that a combination of fields is unique.

        Code is copy-pasted from amivapi, see there for more explanation.
        https://github.com/amiv-eth/amivapi/blob/master/amivapi/utils.py
        """
        lookup = {field: value}  # self
        for other_field in unique_combination:
            lookup[other_field] = self.document.get(other_field)

        if request.method == 'PATCH':
            original = self._original_document
            for key in unique_combination:
                if key not in self.document.keys():
                    lookup[key] = original[key]

        resource = self.resource
        if current_app.data.find_one(resource, None, **lookup) is not None:
            self._error(field, "value already exists in the database in " +
                        "combination with values for: %s" %
                        unique_combination)

    def _validate_not_patchable(self, enabled, field, _):
        """Inhibit patching of the field, also copied from AMIVAPI."""
        if enabled and (request.method == 'PATCH'):
            self._error(field, "this field can not be changed with PATCH")
