"""Test api connection functions.

These tests require command line options to run.

First, aquire a amivapi token (e.g. with curl) both for a user in the
admin group and for a user not in the admin group.

Then provide them to the tests with:

> py.test --usertoken <token> --admintoken <token>

(of course, replace `<token>` with the two respective values)

The basic idea is simple: all security related functions use the g object
for their in- and outputs.

So we just put the provided token into g and see if the functions work.
"""

from flask import g

from security import get_user, get_nethz, is_admin


def test_user_found(app, usertoken):
    """Test if a user can be found with an api token."""
    with app.app_context():
        g.token = usertoken
        assert get_user() is not None


def test_nethz_found(app, usertoken):
    """Test if a users nethz can be found with an api token."""
    with app.app_context():
        g.token = usertoken
        assert get_nethz() is not None


def test_user_not_found(app):
    """Without token, user cannot be found."""
    with app.app_context():
        assert get_user() is None


def test_nethz_not_found(app):
    """Without token, users nethz cannot be found."""
    with app.app_context():
        assert get_nethz() is None


def test_not_admin(app):
    """Without token, user does no get admin priviledges."""
    with app.app_context():
        assert is_admin() is False


def test_user_not_admin(app, usertoken):
    """Test if the user does not get admin priviledges."""
    with app.app_context():
        g.token = usertoken
        assert is_admin() is False


def test_admin(app, admintoken):
    """Test if admins get priviledges."""
    with app.app_context():
        g.token = admintoken
        assert is_admin() is True
