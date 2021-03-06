"""Test Helpers.

Most importantly, set the test db credentials and provide an `app` fixture
which tests can use to get an app object with test client.

This fixture automatically ensures that the database is dropped after the test.

Furthermore the test client is modified a bit compared to the default client
to allow easier assertion of status_codes and make json handling easier.
"""

import json
from contextlib import contextmanager

import pytest

from flask import g
from flask.testing import FlaskClient
from backend.app import create_app


TEST_SETTINGS = {
    'URL_PREFIX': '',  # remove prefix to avoid typing /api/ everywhere
    'MONGO_DBNAME': 'pvk_test',
    'MONGO_USERNAME': 'pvk_user',
    'MONGO_PASSWORD': 'pvk_pass',
}


# Check command line options for API token
# This way we can conveniently skip integration tests per default,
# but still provide a convenient interface to run them

def pytest_addoption(parser):
    """Add options to get tokens from command line."""
    parser.addoption("--usertoken",
                     action="store",
                     help="amivapi user token")
    parser.addoption("--admintoken",
                     action="store",
                     help="amivapi pvk admin token")


@pytest.fixture
def admintoken(request):
    """Fixture to provide admin token or skip test if its not available."""
    token = request.config.getoption('--admintoken')
    if token is None:
        pytest.skip("need api admin token to run")
    return token


@pytest.fixture
def usertoken(request):
    """Fixture to provide user token or skip test if its not available."""
    token = request.config.getoption('--usertoken')
    if token is None:
        pytest.skip("need api user token to run")
    return token


class TestClient(FlaskClient):
    """Custom test client for easier json handling."""

    def open(self, *args, **kwargs):
        """Built-in status_code assertion and send/return json."""
        assert_status = kwargs.pop('assert_status', None)

        if "data" in kwargs:
            # Parse data
            kwargs['data'] = json.dumps(kwargs['data'])
            # Set header
            kwargs['content_type'] = "application/json"

        # Add Fake Header if specified in context
        try:
            auth = g.fake_token
            kwargs.setdefault('headers', {})['Authorization'] = auth
        except (RuntimeError, AttributeError):
            # RuntimeError: No g, AttributeError: key in g is missing
            pass  # No fake token to set

        # Send the actual request
        response = super(TestClient, self).open(*args, **kwargs)

        if assert_status is not None:
            assert response.status_code == assert_status, \
                response.get_data(as_text=True)

        return json.loads(response.get_data(as_text=True) or '{}')


def drop_database(application):
    """Drop drop drop!"""
    with application.app_context():
        database = application.data.driver.db
        for collection in database.collection_names():
            database.drop_collection(collection)


@contextmanager
def user(self, nethz=None, membership=None, **kwargs):
    """Additional context to fake a user."""
    with self.test_request_context():
        g.apiuser = {
            'nethz': nethz or 'nethz',
            'membership': membership or 'regular',
        }
        g.admin = False

        # The test requests will use this header
        g.fake_token = 'Token Trolololo'

        # Allow to overwrite settings
        for key, value in kwargs.items():
            setattr(g, key, value)

        yield


@contextmanager
def admin(self, **kwargs):
    """Additional context to fake a user."""
    with self.user(**kwargs):
        g.admin = True
        yield


@pytest.fixture
def app():
    """Create app, instantiate test client, drop DB after use."""
    application = create_app(**TEST_SETTINGS)
    application.test_client_class = TestClient
    application.client = application.test_client()

    # Using __get__ binds the function to the application instance
    application.user = user.__get__(application)  # pylint: disable=E1121
    application.admin = admin.__get__(application)  # pylint: disable=E1121

    yield application
    drop_database(application)
