"""Tests for authentication."""

import pytest

from flask import g


@pytest.mark.parametrize('resource',
                         ['lectures', 'assistants', 'courses', 'signups'])
@pytest.mark.parametrize('method', ['get', 'post'])
def test_auth_required_for_resource(app, resource, method):
    """Without auth header, we get get 401 for all methods."""
    getattr(app.client, method)('/' + resource, data={}, assert_status=401)


@pytest.mark.parametrize('resource',
                         ['lectures', 'assistants', 'courses', 'signups'])
@pytest.mark.parametrize('method', ['get', 'patch', 'delete'])
def test_auth_required_for_item(app, resource, method):
    """Without auth provided, we can access any item either."""
    # Bypass validation and put a empty item directly into db
    with app.app_context():
        _id = app.data.driver.db[resource].insert({})

    getattr(app.client, method)('/%s/%s' % (resource, _id),
                                data={},
                                assert_status=401)



@pytest.mark.parametrize('resource', ['lectures', 'assistants', 'courses'])
def test_user_can_read(app, resource):
    """Users should be able to to GET requests on resource and item.

    Not signups! There, users can only see their own items -> extra test
    This implies that admins can read, too, since every admin is a user.
    """
    with app.test_request_context():
        # Fake a user
        g.user = 'Not None :)'
        faketoken = {'Authorization': 'Token Trolololo'}

        # Read resource
        app.client.get('/' + resource, headers=faketoken, assert_status=200)

        # Create fake item and read item
        _id = app.data.driver.db[resource].insert({})
        app.client.get('/%s/%s' % (resource, _id),
                       headers=faketoken,
                       assert_status=200)


@pytest.mark.parametrize('resource', ['lectures', 'assistants', 'courses'])
def test_user_cannot_write(app, resource):
    """Users cannot create, modify or delete."""
    with app.test_request_context():
        # Fake a user, specify non-admin
        g.user = 'Not None :)'
        g.admin = False
        faketoken = {'Authorization': 'Token Trolololo'}
        data = {}

        # Post something
        app.client.post('/' + resource,
                        data=data,
                        headers=faketoken,
                        assert_status=401)

        # Create fake item, try to patch/delete it
        _id = app.data.driver.db[resource].insert({})
        app.client.patch('/%s/%s' % (resource, _id),
                         data=data,
                         headers=faketoken,
                         assert_status=401)
        app.client.delete('/%s/%s' % (resource, _id),
                          headers=faketoken,
                          assert_status=401)


def test_signup_with_own_nethz_only(app):
    """Users can only post singups with their own nethz."""
    with app.test_request_context():
        nethz = 'Something'
        # Fake a user, specify non-admin
        g.user = 'Not None :)'
        g.nethz = nethz
        g.admin = False
        faketoken = {'Authorization': 'Token Trolololo'}

        # Create fake course to sign up to
        course = str(app.data.driver.db['courses'].insert({}))

        # Try with other nethz
        bad_signup = {
            'nethz': 'Notthenethz',
            'course': course
        }
        app.client.post('/signups',
                        data=bad_signup,
                        headers=faketoken,
                        assert_status=422)

        # Try with own nethz
        good_signup = {
            'nethz': nethz,
            'course': course
        }
        app.client.post('/signups',
                        data=good_signup,
                        headers=faketoken,
                        assert_status=201)


def test_user_signup_visibility(app):
    """Test that we a user cannot see others' signups."""
    with app.test_request_context():
        # Fake a user, specify non-admin
        g.user = 'Not None :)'
        g.nethz = 'Something'
        g.admin = False
        token = {'Authorization': 'Token FakeeTrolololo', 'If-Match': 'Wrong'}

        # Create fake signup with different nethz
        own = str(app.data.driver.db['signups'].insert({'nethz': g.nethz}))
        other = str(app.data.driver.db['signups'].insert({'nethz': 'trolo'}))

        # Resource: Can only see own, not both signups
        response = app.client.get('/signups', headers=token, assert_status=200)
        assert len(response['_items']) == 1
        assert response['_items'][0]['nethz'] == g.nethz

        # Items
        own_url = '/signups/' + own
        other_url = '/signups/' + other

        # Get
        app.client.get(own_url, headers=token, assert_status=200)
        app.client.get(other_url, headers=token, assert_status=404)

        # Patch (if we can see item, we get 412 since etag is wrong)
        app.client.patch(own_url, headers=token, data={}, assert_status=412)
        app.client.patch(other_url, headers=token, data={}, assert_status=404)

        # Delete (etag missing again)
        app.client.delete(own_url, headers=token, assert_status=412)
        app.client.delete(other_url, headers=token, assert_status=404)

def test_admin_signup_visibility(app):
    """Test that we an admin can see others' signups."""
    with app.test_request_context():
        # Fake a user, specify admin
        g.user = 'Not None :)'
        g.nethz = 'Nothing special really'
        g.admin = True
        token = {'Authorization': 'Token FakeeTrolololo', 'If-Match': 'Wrong'}

        # Create fake signup with different nethz
        other = str(app.data.driver.db['signups'].insert({'nethz': 'trolo'}))

        # Resource: Can see signups
        response = app.client.get('/signups', headers=token, assert_status=200)
        assert len(response['_items']) == 1

        # Items
        url = '/signups/' + other

        # Get
        app.client.get(url, headers=token, assert_status=200)

        # Patch (if we can see item, we get 412 since etag is wrong)
        app.client.patch(url, headers=token, data={}, assert_status=412)

        # Delete (etag missing again)
        app.client.delete(url, headers=token, assert_status=412)
