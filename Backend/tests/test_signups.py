"""Test for signup processing, in particular waiting list."""

# Some pylint config:
# Because of fixtures we re-use the same name often
# And some tests need long names to be descriptive
# pylint: disable=redefined-outer-name, invalid-name

from datetime import datetime as dt

from unittest.mock import patch, call
import pytest

from backend.signups import update_signups


def test_success(app):
    """If there are enough spots, the status will be 'reserved'."""
    # Create fake courses to sign up to
    with app.admin():
        course_id = str(app.data.driver.db['courses'].insert({'spots': 10}))

    # Sign up as user
    with app.user(nethz='nethz'):
        signup = {
            'nethz': 'nethz',
            'course': course_id,
        }

        signup_response = app.client.post('/signups',
                                          data=signup,
                                          assert_status=201)

        assert signup_response['status'] == 'reserved'

        # Check signup
        updated_signup = app.client.get('/signups/' + signup_response['_id'],
                                        assert_status=200)

        assert updated_signup['status'] == 'reserved'


def test_zero_spots(app):
    """Setting spots to zero will just put everyone on the waiting list."""
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

        assert first_response['status'] == 'reserved'

        second = {
            'nethz': 'Otherthing',
            'course': course_id,
        }

        second_response = app.client.post('/signups',
                                          data=second,
                                          assert_status=201)

        assert second_response['status'] == 'waiting'


def test_course_independence(app):
    """Test that signups of one course don't influence another.

    There was a bug in the code that lead to counting any signup for any
    course. This test should ensure it doesn't happen again.
    """
    with app.admin():
        # Course with a free spot
        main_course = app.data.driver.db['courses'].insert({'spots': 1})

        # Other course that will get signups
        other_course = app.data.driver.db['courses'].insert({'spots': 5})
        for _ in range(5):
            app.data.driver.db['signups'].insert({'course': other_course})

        # Sign up to course
        signup = {
            'nethz': 'Something',
            'course': str(main_course),
        }

        response = app.client.post('/signups',
                                   data=signup,
                                   assert_status=201)

        # The other signups should have no influence
        assert response['status'] == 'reserved'


def test_update_spots(app):
    """Test the main update function.

    As a key for sorting, the _updated timestamp will be used, with
    nethz as a tie breaker
    """
    with app.admin():
        # Create a course with two spots
        test_course = app.data.driver.db['courses'].insert({'spots': 2})

        # Create four signups on waiting list
        # 1. Oldest _created timestamp, but recently modified (recent _updated)
        first_data = {
            'course': test_course,
            'status': 'waiting',
            '_created': dt(2020, 10, 10),
            '_updated': dt(2020, 10, 20),
        }
        first_id = str(app.data.driver.db['signups'].insert(first_data))

        # 3. oldest _updated
        second_data = {
            'course': test_course,
            'status': 'waiting',
            '_created': dt(2020, 10, 11),
            '_updated': dt(2020, 10, 11),
        }
        second_id = str(app.data.driver.db['signups'].insert(second_data))

        # 3. earlier _created, second oldest _updated
        third_data = {
            'course': test_course,
            'status': 'waiting',
            '_created': dt(2020, 10, 12),
            '_updated': dt(2020, 10, 15),
            'nethz': 'abc'
        }
        third_id = str(app.data.driver.db['signups'].insert(third_data))

        # 4. Same updated time as 3, but different id that will loose tie
        fourth_data = {
            'course': test_course,
            'status': 'waiting',
            '_created': dt(2020, 10, 13),
            '_updated': dt(2020, 10, 15),
            'nethz': 'bcd'
        }
        fourth_id = str(app.data.driver.db['signups'].insert(fourth_data))

        # Do the update!
        # We except 2 and 3 to get spots
        update_signups(str(test_course))

        def _status(_id):
            return app.client.get('/signups/' + _id,
                                  assert_status=200)['status']

        assert _status(first_id) == 'waiting'
        assert _status(second_id) == 'reserved'
        assert _status(third_id) == 'reserved'
        assert _status(fourth_id) == 'waiting'


@pytest.fixture
def course(app):
    """Create a fake course without any data for a test."""
    with app.admin():
        # Create a few courses to sign up to
        database = app.data.driver.db['courses']
        yield database.insert({'_etag': 'tag'})


@pytest.fixture
def mock_update():
    """Mock the actual updating of spots for a test."""
    with patch('backend.signups.update_signups', return_value=[]) as update:
        yield update


def test_post_signups_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    data = {
        'course': str(course),
        'nethz': 'bli'
    }
    app.client.post('signups', data=data, assert_status=201)

    # Note: With post, the course comes from the request, not the db,
    #       so the update will be called with a string
    mock_update.assert_called_with(str(course))


def test_patch_signup_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    fake = app.data.driver.db['signups'].insert({
        '_etag': 'tag',
        'nethz': 'lala',
        'course': 'oldcourse'
    })
    app.client.patch('/signups/%s' % fake,
                     data={'course': str(course)},
                     headers={'If-Match': 'tag'},
                     assert_status=200)

    # Both the signups of the old and new course are updated
    mock_update.assert_has_calls([call(course), call('oldcourse')])


def test_delete_signup_triggers_update(app, course, mock_update):
    """Test the the update of spots gets triggered correctly."""
    fake = app.data.driver.db['signups'].insert({
        'course': course,
        '_etag': 'tag'
    })
    app.client.delete('/signups/%s' % fake,
                      headers={'If-Match': 'tag'},
                      assert_status=204)
    mock_update.assert_called_with(course)


def test_patch_course_without_update(app, course, mock_update):
    """Update of spots gets only triggered if number of spots changes."""
    app.client.patch('/courses/%s' % course,
                     data={'room': 'Something'},
                     headers={'If-Match': 'tag'},
                     assert_status=200)
    mock_update.assert_not_called()


def test_patch_course_with_update(app, course, mock_update):
    """Update of spots gets only triggered if number of spots changes."""
    app.client.patch('/courses/%s' % course,
                     data={'spots': '10'},
                     headers={'If-Match': 'tag'},
                     assert_status=200)
    mock_update.assert_called_with(course)


def test_block_delete_ok(app, course):
    """If a course has no signups, it can be deleted."""
    app.client.delete('/courses/%s' % course,
                      headers={'If-Match': 'tag'},
                      assert_status=204)


def test_block_delete_blocked(app, course):
    """If a course has signups, it cannot be deleted."""
    app.data.driver.db['signups'].insert({'course': course})
    app.client.delete('/courses/%s' % course,
                      headers={'If-Match': 'tag'},
                      assert_status=409)


def test_embed_course(app, course):
    """Test that embedding course on POST to signups doesn't break anything."""
    data = {
        'course': str(course),
        'nethz': 'bli'
    }

    app.client.post('signups?embedded={"course": 1}',
                    data=data,
                    assert_status=201)
