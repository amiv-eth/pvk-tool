"""Test Helpers.

Most importantly, set the test db credentials and provide an `app` fixture
which tests can use to get an app object with test client.

This fixture automatically ensures that the database is dropped after the test.

Furthermore the test client is modified a bit compared to the default client
to allow easier assertion of status_codes and make json handling easier.
"""

import json

import pytest

from pymongo import MongoClient
from flask.testing import FlaskClient
from app import create_app


TEST_SETTINGS = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'pvk_test',
    'MONGO_USERNAME': 'pvk_user',
    'MONGO_PASSWORD': 'pvk_pass',
}


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

        response = super(TestClient, self).open(*args, **kwargs)

        if assert_status is not None:
            assert response.status_code == assert_status, \
                response.get_data(as_text=True)

        return json.loads(response.get_data(as_text=True))


def drop_database(application):
    """Drop drop drop!"""
    connection = MongoClient(application.config['MONGO_HOST'],
                             application.config['MONGO_PORT'])
    connection.drop_database(application.config['MONGO_DBNAME'])
    connection.close()


@pytest.fixture
def app():
    """Create app, instantiate test client, drop DB after use."""
    application = create_app(settings=TEST_SETTINGS)
    application.test_client_class = TestClient
    application.client = application.test_client()
    yield application
    drop_database(application)
