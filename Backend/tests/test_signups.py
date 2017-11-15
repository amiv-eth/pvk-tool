"""Test for signup processing, in particular waiting list."""

from unittest.mock import patch, call
import pytest

from datetime import datetime as dt

from signups import update_signups


def test_success(app):
    """If there are enough spots, the status will be 'reserved'."""
    with app.admin():  # Admin so we don't need to care about nethz
        # Create fake courses to sign up to
        course_id = str(app.data.driver.db['courses'].insert({'spots': 10}))

        signup = {
            'nethz': 'Something',
            'course': course_id,
        }

        signup_response = app.client.post('/signups',
                                          data=signup,
                                          assert_status=201)

        assert signup_response['status'] == 'reserved'

        # Now pay
        payment = {
            'signups': [signup_response['_id']]
        }
        app.client.post('/payments',
                        data=payment,
                        assert_status=201)

        # Check signup
        updated_signup = app.client.get('/signups/' + signup_response['_id'],
                                        assert_status=200)

        assert updated_signup['status'] == 'accepted'


def test_zero_spots(app):
    """Settings spots to zero will just put everyone on the waiting list."""
    with app.admin():
        # Create fake courses to sign up to
        course_id = str(app.data.driver.db['courses'].insert({'spots': 0}))

        signup = {
            'nethz': 'Something',
            'course': course_id,
        }

        signup_response = app.client.post('/signups',
                                          data=signup,
                                          assert_status=201)

        assert signup_response['status'] == 'waiting'


def test_not_enough_spots(app):
    """If there are not enough spots, signups go to waiting list."""
    with app.admin():
        # Create fake courses to sign up to
        course_id = str(app.data.driver.db['courses'].insert({'spots': 1}))

        first = {
            'nethz': 'Something',
            'course': course_id,
        }

        first_response = app.client.post('/signups',
                                         data=first,
                                         assert_status=201)

        print(first_response['_updated'])

        assert first_response['status'] == 'reserved'

        second = {
            'nethz': 'Otherthing',
            'course': course_id,
        }

        second_response = app.client.post('/signups',
                                          data=second,
                                          assert_status=201)

        print(second_response['_updated'])

        assert second_response['status'] == 'waiting'


def test_update_spots(app):
    """Test the main update function.

    As a key for sorting the _updated timestamp will be used, with
    nethz as a tie breaker
    """
    with app.admin():
        # Create a course with two spots
        course = app.data.driver.db['courses'].insert({'spots': 2})

        # Create four signups on waiting list
        # 1. Oldest _created timestamp, but recently modified (recent _updated)
        first_data = {
            'course': course,
            'status': 'waiting',
            '_created': dt(2020, 10, 10),
            '_updated': dt(2020, 10, 20),
        }
        first_id = str(app.data.driver.db['signups'].insert(first_data))

        # 3. oldest _updated
        second_data = {
            'course': course,
            'status': 'waiting',
            '_created': dt(2020, 10, 11),
            '_updated': dt(2020, 10, 11),
        }
        second_id = str(app.data.driver.db['signups'].insert(second_data))

        # 3. earlier _created, second oldest _updated
        third_data = {
            'course': course,
            'status': 'waiting',
            '_created': dt(2020, 10, 12),
            '_updated': dt(2020, 10, 15),
            'nethz': 'abc'
        }
        third_id = str(app.data.driver.db['signups'].insert(third_data))

        # 4. Same updated time as 3, but different id that will loose tie
        fourth_data = {
            'course': course,
            'status': 'waiting',
            '_created': dt(2020, 10, 13),
            '_updated': dt(2020, 10, 15),
            'nethz': 'bcd'
        }
        fourth_id = str(app.data.driver.db['signups'].insert(fourth_data))

        # Do the update!
        # We except 2 and 3 to get spots
        update_signups(str(course))

        def status(_id):
            return app.client.get('/signups/' + _id,
                                  assert_status=200)['status']

        assert status(first_id) == 'waiting'
        assert status(second_id) == 'reserved'
        assert status(third_id) == 'reserved'
        assert status(fourth_id) == 'waiting'


@pytest.fixture
def course(app):
    """Create a fake course without any data for a test."""
    with app.admin():
        # Create a few courses to sign up to
        db = app.data.driver.db['courses']
        yield str(db.insert({'_etag': 'tag'}))


@pytest.fixture
def mock_update():
    """Mock the actual updating of spots for a test."""
    with patch('signups.update_signups', return_value=[]) as update:
        yield update


def test_post_signups_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    data = {
        'course': course,
        'nethz': 'bli'
    }
    app.client.post('signups', data=data, assert_status=201)
    mock_update.assert_called_with(course)


def test_batch_post_signups_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    # We need a second course to test everything
    other_course = str(app.data.driver.db['courses'].insert({}))

    batch = [{
        'course': course,
        'nethz': 'bla'
    }, {
        'course': course,
        'nethz': 'bli'
    }, {
        'course': other_course,
        'nethz': 'bli'
    }]
    app.client.post('/signups', data=batch, assert_status=201)
    # Same course doesn't get updated twice per request
    mock_update.assert_has_calls([call(course), call(other_course)],
                                 any_order=True)


def test_patch_signup_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    fake = str(app.data.driver.db['signups'].insert({
        '_etag': 'tag',
        'nethz': 'lala',
    }))
    app.client.patch('/signups/' + fake,
                     data={'course': course},
                     headers={'If-Match': 'tag'},
                     assert_status=200)
    mock_update.assert_called_with(course)


def test_delete_signup_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    fake = str(app.data.driver.db['signups'].insert({
        'course': course,
        '_etag': 'tag'
    }))
    app.client.delete('/signups/' + fake,
                      headers={'If-Match': 'tag'},
                      assert_status=204)
    mock_update.assert_called_with(course)


def test_patch_course_without_update(app, course, mock_update):
    """Update of spots gets only triggered if number of spots changes."""
    app.client.patch('/courses/' + course,
                     data={'room': 'Something'},
                     headers={'If-Match': 'tag'},
                     assert_status=200)
    mock_update.assert_not_called()


def test_patch_course_with_update(app, course, mock_update):
    """Update of spots gets only triggered if number of spots changes."""
    app.client.patch('/courses/' + course,
                     data={'spots': '10'},
                     headers={'If-Match': 'tag'},
                     assert_status=200)
    mock_update.assert_called_with(course)


def test_block_delete_ok(app, course):
    """If a course has no signups, it can be deleted."""
    app.client.delete('/courses/' + course,
                      headers={'If-Match': 'tag'},
                      assert_status=204)


def test_block_delete_blocked(app, course):
    """If a course has signups, it cannot be deleted."""
    str(app.data.driver.db['signups'].insert({'course': course}))
    app.client.delete('/courses/' + course,
                      headers={'If-Match': 'tag'},
                      assert_status=409)
