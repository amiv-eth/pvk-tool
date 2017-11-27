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
"""

from functools import wraps
import requests
from eve.auth import TokenAuth
from flask import g, current_app, abort


# Requests to AMIVAPI

def api_get(endpoint, **params):
    """Format and send a GET request to AMIVAPI. Return json data or None."""
    url = requests.compat.urljoin(current_app.config['AMIVAPI_URL'], endpoint)
    headers = {'Authorization': "Token %s" % g.token}

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
                print(key, getattr(g, key))
                return getattr(g, key)
            except AttributeError:
                setattr(g, key, function(*args, **kwargs))
                return getattr(g, key)
        return _wrapper
    return _decorator


@request_cache('user')
def get_user():
    """Return user id if the token is valid, None otherwise."""
    response = api_get(
        'sessions',
        where={'token': g.get('token', '')},
        projection={'user': 1}
    )
    if response:
        return response['_items'][0]['user']


@request_cache('nethz')
def get_nethz():
    """Return nethz of current user."""
    if get_user() is not None:
        response = api_get('users', projection={'nethz': 1})
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
        groups = api_get(
            'groups',
            where={'name': current_app.config['ADMIN_GROUP_NAME']},
            projection={'_id': 1}
        )
        if groups:
            print(groups)
            group_id = groups['_items'][0]['_id']

            membership = api_get(
                'groupmemberships',
                where={'user': user_id, 'group': group_id},
                projection={'_id': 1}
            )

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

        # Check permitted methods for users, return 403 if not permitted
        # Admins can do everything
        domain = current_app.config['DOMAIN']
        allowed_methods = domain[resource].get('user_methods', [])

        if method in allowed_methods or is_admin():
            return True
        else:
            abort(403)


# Dynamic Visibility Filter

def only_own_nethz(_, lookup):
    """Users can only see signups if their ID matches."""
    if not is_admin():
        # Add the additional lookup with an `$and` condition
        # or extend existing `$and`s
        lookup.setdefault('$and', []).append({'nethz': get_nethz()})
