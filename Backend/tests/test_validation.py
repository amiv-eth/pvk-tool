"""Test special validators, e.g. for time overlap."""
# pylint: disable=redefined-outer-name

import pytest


@pytest.fixture
def lecture(app):
    """Create a lecture, return its id."""
    with app.admin():
        lecture = {
            'title': "Time and Space",
            'department': "itet",
            'year': 2,
            'assistants': ['pablo'],
        }
        return app.client.post('lectures',
                               data=lecture,
                               assert_status=201)['_id']


def test_start_time_before_end(app, lecture):
    """Test that any start time must come before end time."""
    correct = {
        'lecture': lecture,
        'assistant': 'pablo',
        'spots': 10,
        'datetimes': [{
            'start': '2019-01-09T10:00:00Z',
            'end': '2019-01-09T13:00:00Z',
        }],
    }

    wrong = {
        'lecture': lecture,
        'assistant': 'pablo',
        'spots': 10,
        'datetimes': [{
            'start': '2019-02-09T13:00:00Z',
            'end': '2019-02-09T10:00:00Z',
        }],
    }

    with app.admin():
        app.client.post('courses', data=correct, assert_status=201)
        app.client.post('courses', data=wrong, assert_status=422)


@pytest.fixture
def courses(app, lecture):
    """Return data for courses that overlap. (And a control course)"""
    with app.admin():

        same_time = {
            'lecture': lecture,
            'assistant': 'pablo',
            'spots': 10,
            'datetimes': [{
                'start': '2019-01-09T10:00:00Z',
                'end': '2019-01-09T13:00:00Z',
            }]
        }
        first = {'room': 'ETZ E 6'}
        first.update(same_time)
        first_id = app.client.post('courses',
                                   data=first,
                                   assert_status=201)['_id']
        second = {'room': 'ETZ E 8'}
        second.update(same_time)
        second_id = app.client.post('courses',
                                    data=second,
                                    assert_status=201)['_id']

        # Now a third course without overlap
        control = {
            'lecture': lecture,
            'spots': 10,
            'datetimes': [{
                'start': '2019-02-10T10:00:00Z',
                'end': '2019-02-10T13:00:00Z',
            }],
            'room': 'ETZ E 9'
        }
        control_id = app.client.post('courses',
                                     data=control,
                                     assert_status=201)['_id']

        return (first_id, second_id, control_id)


# The base timeslot will be from 10:00 to 13:00,
@pytest.mark.parametrize("start_hour,end_hour", [
    (7, 9),    # before
    (7, 10),   # direcly before, but no overlap
    (14, 17),  # after
    (13, 17),  # directly after
])
def test_no_timeslot_overlap(app, lecture, start_hour, end_hour):
    """The timeslots for a given course must not overlap."""
    with app.admin():
        data = {
            'lecture': lecture,
            'room': 'someroom',
            'spots': 10,
            'datetimes': [{
                'start': '2015-06-05T10:00:00Z',
                'end': '2015-06-05T13:00:00Z',
            }, {
                'start': '2015-06-05T%s:00:00Z' % start_hour,
                'end': '2015-06-05T%s:00:00Z' % end_hour,
            }],
        }
        app.client.post('courses', data=data, assert_status=201)


# The base timeslot will be from 10:00 to 13:00,
@pytest.mark.parametrize("start_hour,end_hour", [
    (9, 11),   # end overlaps with base
    (12, 14),  # start overlaps
    (9, 14),   # contains other timeslot
    (11, 12),  # contained by other timeslot
    (10, 13),  # same timeslot
])
def test_timeslot_overlap(app, lecture, start_hour, end_hour):
    """Test different ways of overlapping timeslots."""
    with app.admin():
        data = {
            'lecture': lecture,
            'room': 'someroom',
            'spots': 10,
            'datetimes': [{
                'start': '2015-06-05T10:00:00Z',
                'end': '2015-06-05T13:00:00Z',
            }, {
                'start': '2015-06-05T%s:00:00Z' % start_hour,
                'end': '2015-06-05T%s:00:00Z' % end_hour,
            }],
        }
        app.client.post('courses', data=data, assert_status=422)


def test_no_double_booking_of_room(app, lecture):
    """Any given room can not be assigned to two courses at the same time."""
    with app.admin():
        room = 'LEE E 12'
        first = {
            'lecture': lecture,
            'assistant': 'pablo',
            'room': room,
            'spots': 10,
            'datetimes': [{
                'start': '2018-12-06T10:00:00Z',
                'end': '2018-12-06T13:00:00Z',
            }],
        }

        second = {
            'lecture': lecture,
            'assistant': 'pablo',
            'room': room,
            'spots': 20,
            'datetimes': [{
                # Contains the first course
                'start': '2018-12-06T9:00:00Z',
                'end': '2018-12-06T15:00:00Z',
            }, {
                'start': '2018-12-10T13:00:00Z',
                'end': '2018-12-10T14:00:00Z',
            }, {
                'start': '2018-12-10T15:00:00Z',
                'end': '2018-12-10T16:00:00Z',
            }],
        }

        # Posting only one is ok, but the second one will fail
        app.client.post('courses', data=first, assert_status=201)
        print("NOW")
        app.client.post('courses', data=second, assert_status=422)

        # Posting the second course with a different room is ok
        second['room'] = 'other %s' % room
        response = app.client.post('courses', data=second, assert_status=201)

        # Patching the time or room without overlap is ok:
        url = 'courses/%s' % response['_id']
        separate_room = {'room': 'another different %s' % room}
        response = app.client.patch(url, data=separate_room,
                                    headers={'If-Match': response['_etag']},
                                    assert_status=200)


@pytest.fixture
def patch_courses(app, lecture):
    """Courses that nearly overlap."""
    first = {
        'lecture': lecture,
        'assistant': 'pablo',
        'room': 'ETZ E 1',
        'spots': 10,
        'datetimes': [{
            'start': '2018-12-06T10:00:00Z',
            'end': '2018-12-06T13:00:00Z',
        }],
    }
    # Second course has same room but different time
    second = {
        'lecture': lecture,
        'assistant': 'pablo',
        'room': 'ETZ E 1',
        'spots': 10,
        'datetimes': [{
            'start': '2018-11-06T10:00:00Z',
            'end': '2018-11-06T13:00:00Z',
        }],
    }
    # Third course has different room but same time
    third = {
        'lecture': lecture,
        'assistant': 'pablo',
        'room': 'ETZ E 2',
        'spots': 10,
        'datetimes': [{
            'start': '2018-12-06T10:00:00Z',
            'end': '2018-12-06T13:00:00Z',
        }],
    }
    # Control course has different room and time
    control = {
        'lecture': lecture,
        'assistant': 'pablo',
        'room': 'ETZ E 3',
        'spots': 10,
        'datetimes': [{
            'start': '2018-01-06T10:00:00Z',
            'end': '2018-01-06T13:00:00Z',
        }],
    }

    def _create(data):
        with app.admin():
            return app.client.post('courses', data=data, assert_status=201)

    # Return data of created courses
    return tuple(_create(data) for data in (first, second, third, control))


def test_patch_time_different_room(app, patch_courses):
    """If the course have different rooms, patching to same time is ok."""
    with app.admin():
        app.client.patch('courses/%s' % patch_courses[2]['_id'],
                         headers={'If-Match': patch_courses[2]['_etag']},
                         data={'datetimes': patch_courses[0]['datetimes']},
                         assert_status=200)


def test_patch_time_same_room(app, patch_courses):
    """If the course have the same room, patching to same time is not ok."""
    with app.admin():
        app.client.patch('courses/%s' % patch_courses[1]['_id'],
                         headers={'If-Match': patch_courses[1]['_etag']},
                         data={'datetimes': patch_courses[0]['datetimes']},
                         assert_status=422)


def test_patch_room_different_time(app, patch_courses):
    """If the course have different times, patching to same room is ok."""
    with app.admin():
        app.client.patch('courses/%s' % patch_courses[1]['_id'],
                         headers={'If-Match': patch_courses[1]['_etag']},
                         data={'room': patch_courses[0]['room']},
                         assert_status=200)


def test_patch_room_same_time(app, patch_courses):
    """If the course have the same times, patching to same room is not ok."""
    with app.admin():
        app.client.patch('courses/%s' % patch_courses[2]['_id'],
                         headers={'If-Match': patch_courses[2]['_etag']},
                         data={'room': patch_courses[0]['room']},
                         assert_status=422)


def test_patch_both(app, patch_courses):
    """Patching both at the same time causes overlap."""
    with app.admin():
        app.client.patch('courses/%s' % patch_courses[3]['_id'],
                         headers={'If-Match': patch_courses[3]['_etag']},
                         data={'room': patch_courses[0]['room'],
                               'datetimes': patch_courses[0]['datetimes']},
                         assert_status=422)


def test_patch_self_overlap(app, lecture):
    """Patch the course such that it would overlap with its old version."""
    time_1 = {
        'start': '2018-01-06T10:00:00Z',
        'end': '2018-01-06T13:00:00Z',
    }
    time_2 = {
        'start': '2018-01-06T14:00:00Z',
        'end': '2018-01-06T18:00:00Z',
    }
    time_3 = {
        'start': '2018-01-06T18:00:00Z',
        'end': '2018-01-06T19:00:00Z',
    }
    data = {
        'lecture': lecture,
        'assistant': 'pablo',
        'room': 'someroom',
        'spots': 10,
        'datetimes': [time_1, time_2],
    }
    overlapping_span = {
        'datetimes': [time_2, time_3],
    }

    with app.admin():
        course = app.client.post('courses', data=data, assert_status=201)
        app.client.patch('courses/%s' % course['_id'],
                         headers={'If-Match': course['_etag']},
                         data=overlapping_span,
                         assert_status=200)


# We can use the same test for selection and signup (same data structure)
@pytest.mark.parametrize('resource', ['signups', 'selections'])
def test_no_overlap_for_user(app, resource, courses):
    """A user can not sign up for two courses that happen at the same time."""
    with app.admin():
        signup = {
            'nethz': 'pablito',
            'course': courses[0]
        }
        parallel = {
            'nethz': 'pablito',
            'course': courses[1]
        }

        control = {
            'nethz': 'anon',
            'course': courses[1]
        }

        # Posting only one is ok, but the second one will fail
        app.client.post(resource, data=signup, assert_status=201)
        app.client.post(resource, data=parallel, assert_status=422)

        # Other users are not influenced
        app.client.post(resource, data=control, assert_status=201)


@pytest.mark.parametrize('resource', ['signups', 'selections'])
def test_no_patch_overlap(app, resource, courses):
    """A user can change the course of a singup/selection to cause overlap."""
    with app.admin():
        signup = {
            'nethz': 'pablito',
            'course': courses[0]
        }
        separate = {
            'nethz': 'pablito',
            'course': courses[2]
        }

        # Both singups can be created since the course do not overlap
        app.client.post(resource, data=signup, assert_status=201)
        response = app.client.post(resource, data=separate, assert_status=201)

        print('User has course', courses[0])
        print('User wants course', courses[1])

        # Patching a signup to an overlapping course does not work
        app.client.patch('%s/%s' % (resource, response['_id']),
                         data={'course': courses[1]},
                         headers={'If-Match': response['_etag']},
                         assert_status=422)
