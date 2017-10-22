"""AMIVAPI Authentication.

We use the `g` globals as intermediate storage:
- g['user'] is the user_id if the token was valid, otherwise None
- g['admin'] is True if the user is an admin, False otherwise

(This allows easier testing since we can just modify g)
"""

from functools import wraps
import json
import requests
from eve.auth import TokenAuth
from eve.io.mongo import Validator
from flask import request, g, current_app


def request_cache(key):
    """User as decorator: safe the function return in g[key]."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return getattr(g, key)
            except KeyError:
                setattr(g, key, f(*args, **kwargs))
                return getattr(g, key)
        return wrapper
    return decorator


def api_get(resource, token, where, projection):
    """Format and send a GET request to AMIVAPI. Return json data or None."""
    url = requests.compat.urljoin(current_app.config['AMIVAPI_URL'], resource)
    headers = {'Authorization': "Token %s" % token}
    params = {
        'where': json.dumps(where),
        'projection': json.dumps(projection)
    }
    response = requests(url, params=params, headers=auth_header(token))
    if response.status_code == 200:
        return response.json()

@request_cache('user')
def get_user():
    """Return user id if the token is valid, None otherwise."""
    token = g.get(token, '')
    response = api_get('sessions', token, {'token': token}, {'user': 1})
    if response:
        return response['_items'][0]['user']


@request_cache('nethz')
def get_nethz():
    """Return nethz of current user."""
    if get_user() is not None:
        response = api_get('users/%s' % get_user(), token, {}, {'nethz': 1})
        return response.get('nethz')



@request_cache('admin')
def is_admin():
    """Return True if user is in the 'PVK Admins' Group, False otherwise.

    The result is saved in g, to avoid checking twice, so there is no
    performance loss if is_admin is called multiple times during a request.
    """
    token = g.get(token, '')
    user_id = get_user()
    if user_id is not None:
        # Find Group with correct name, return list of members
        groups = api_get('groups', token,
                         {'name': current_app.config['ADMIN_GROUP_NAME']},
                         {'_id': 1})
        if groups:
            group_id = groups['_items'][0]['_id']

            membership = api_get('groupmemberships', token,
                                 {'user': user_id, 'group': group_id},
                                 {'_id': 1})

            return bool(membership and len(membership['_items']) != 0)

    # In all other cases, user is not an admin.
    return False


class APIAuth(TokenAuth):
    """Verifies the presented with AMIVAPI."""

    def check_auth(self, token, allowed_roles, resource, method):
        """Allow request if token exists in AMIVAPI."""
        g.token = token  # Safe in g such that other methods can use it

        # Valid Login always required
        if get_user() is None:
            return False

        # Read always allowed
        # Write any resource but 'signups': you need to be an admin
        return method == 'GET' or (resource == 'signups') or is_admin()


# Hook to filter signups

def only_own_signups(request, lookup):
    """Users can only see signups if their ID matches."""
    if not is_admin():
        # Add the additional lookup with an `$and` condition
        # or extend existing `$and`s
        lookup.setdefault('$and', []).append({'nethz': get_nethz()})


# Validator that allows to check nethz

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

        if current_app.data.find_one(self.resource, None, **lookup) is not None:
            self._error(field, "value already exists in the database in " +
                        "combination with values for: %s" %
                        unique_combination)
