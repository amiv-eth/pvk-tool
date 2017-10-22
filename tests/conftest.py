"""Test fixtures."""

import json

import pytest

from pymongo import MongoClient
from flask.testing import FlaskClient
from app import create_app


TEST_SETTINGS = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'pvk_test',
    'MONGO_USERNAME': 'pvkuser',
    'MONGO_PASSWORD': 'pvkpass',
}


class TestClient(FlaskClient):
    """Custom test client for easier json handling."""

    def open(self, *args, assert_status=None, **kwargs):
        """Built-in status_code assertion and send/return json."""
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


