"""Tests for all security function."""

import pytest


ALL_RESOURCES = ['lectures', 'courses', 'signups', 'selections', 'payments']
ADMIN_RESOURCES = ['lectures', 'courses']  # only admin can write
PERSONAL_RESOURCES = ['signups', 'selections']  # users can only see their own


@pytest.mark.parametrize('resource', ALL_RESOURCES)
@pytest.mark.parametrize('method', ['get', 'post'])
def test_auth_required_for_resource(app, resource, method):
    """Without auth header, we get get 401 for all methods."""
    getattr(app.client, method)('/' + resource, data={}, assert_status=401)


@pytest.mark.parametrize('resource', ALL_RESOURCES)
@pytest.mark.parametrize('method', ['get', 'patch', 'delete'])
def test_auth_required_for_item(app, resource, method):
    """Without auth provided, we can access any item either."""
    # Bypass validation and put a empty item directly into db
    with app.app_context():
        _id = app.data.driver.db[resource].insert({})

    getattr(app.client, method)('/%s/%s' % (resource, _id),
                                data={},
                                assert_status=401)


@pytest.mark.parametrize('resource', ADMIN_RESOURCES)
def test_user_can_read(app, resource):
    """Users should be able to to GET requests on resource and item.

    Not signups! There, users can only see their own items -> extra test
    This implies that admins can read, too, since every admin is a user.
    """
    with app.user():
        # Read resource
        app.client.get('/' + resource, assert_status=200)

        # Create fake item and read item
        _id = app.data.driver.db[resource].insert({})
        app.client.get('/%s/%s' % (resource, _id),
                       assert_status=200)


@pytest.mark.parametrize('resource', ADMIN_RESOURCES)
def test_user_cannot_write(app, resource):
    """Users cannot create, modify or delete."""
    with app.user():
        data = {}

        # Try to post something
        app.client.post('/' + resource,
                        data=data,
                        assert_status=403)

        # Create fake item, try to patch/delete it
        _id = app.data.driver.db[resource].insert({})
        app.client.patch('/%s/%s' % (resource, _id),
                         data=data,
                         assert_status=403)
        app.client.delete('/%s/%s' % (resource, _id),
                          assert_status=403)


def test_signup_with_own_nethz_only(app):
    """Users can only post singups with their own nethz."""
    nethz = 'Something'
    with app.user(nethz=nethz):
        # Create fake course to sign up to
        course = str(app.data.driver.db['courses'].insert({}))

        # Try with other nethz
        bad_signup = {
            'nethz': 'Notthenethz',
            'course': course
        }
        app.client.post('/signups',
                        data=bad_signup,
                        assert_status=422)

        # Try with own nethz
        good_signup = {
            'nethz': nethz,
            'course': course
        }
        app.client.post('/signups',
                        data=good_signup,
                        assert_status=201)


def test_selection_own_nethz(app):
    """Users can only select courses for themselves."""
    nethz = 'Something'
    with app.user(nethz=nethz):
        # Create fake course to select
        course = str(app.data.driver.db['courses'].insert({}))

        # Try with other nethz
        bad_selection = {
            'nethz': 'Notthenethz',
            'course': course,
        }
        app.client.post('/selections',
                        data=bad_selection,
                        assert_status=422)

        # Try with own nethz
        good_selection = {
            'nethz': nethz,
            'course': course,
        }
        app.client.post('/selections',
                        data=good_selection,
                        assert_status=201)


@pytest.mark.parametrize('resource', PERSONAL_RESOURCES)
def test_user_visibility(app, resource):
    """Test that a user cannot see others' signups or selections."""
    nethz = 'Something'
    with app.user(nethz=nethz):
        # Create fake signup with different nethz
        own = str(app.data.driver.db[resource].insert({'nethz': nethz}))
        other = str(app.data.driver.db[resource].insert({'nethz': 'trolo'}))

        # Resource: Can only see own, not both signups
        response = app.client.get('/' + resource, assert_status=200)
        assert len(response['_items']) == 1
        assert response['_items'][0]['nethz'] == nethz

        # Items
        own_url = '/%s/%s' % (resource, own)
        other_url = '/%s/%s' % (resource, other)

        # Get
        app.client.get(own_url, assert_status=200)
        app.client.get(other_url, assert_status=404)

        # Patch (if we can see item, we get 428 since etag is missing)
        app.client.patch(own_url, data={}, assert_status=428)
        app.client.patch(other_url, data={}, assert_status=404)

        # Delete (etag missing again)
        app.client.delete(own_url, assert_status=428)
        app.client.delete(other_url, assert_status=404)


@pytest.mark.parametrize('resource', PERSONAL_RESOURCES)
def test_admin_signup_visibility(app, resource):
    """Test that we an admin can see others' signups and selections."""
    with app.admin(nethz='somethingsomething'):
        headers = {'If-Match': 'Wrong'}

        # Create fake signup with different nethz
        other = str(app.data.driver.db[resource].insert({'nethz': 'trolo'}))

        # Resource: Can see signups
        response = app.client.get('/' + resource,
                                  headers=headers,
                                  assert_status=200)
        assert len(response['_items']) == 1

        # Items
        url = '/%s/%s' % (resource, other)

        # Get
        app.client.get(url, headers=headers, assert_status=200)

        # Patch (if we can see item, we get 412 since etag is wrong)
        app.client.patch(url, headers=headers, data={}, assert_status=412)

        # Delete (etag missing again)
        app.client.delete(url, headers=headers, assert_status=412)
