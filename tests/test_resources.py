"""Tests for basic requests to all resources."""


def test_create(client):
    """Test creating everything."""
    lecture = {
        'title': "Awesome Lecture",
        'department': "itet",
        'year': 3,
    }
    lecture_response = client.post('lectures', data=lecture, assert_status=201)

    assistant = {'nethz': "Pablo"}
    assistant_response = client.post('assistants',
                                     data=assistant,
                                     assert_status=201)

    course = {
        'lecture': lecture_response['_id'],
        'assistant': assistant_response['_id'],
        'room': 'ETZ E 6',
        'spots': 30,
        'signup': {
            'start': '2020-05-01T10:00:00Z',
            'end': '2020-05-05T23:59:59Z',
        },
        'datetimes': [{
                'start': '2020-06-05T10:00:00Z',
                'end': '2020-06-05T12:00:00Z',
            }, {
                'start': '2020-06-06T10:00:00Z',
                'end': '2020-06-06T12:00:00Z',
            }],
    }
    course_response = client.post('courses', data=course, assert_status=201)

    signup = {
        'nethz': "Pablito",
        'course': course_response['_id']
    }
    client.post('signups', data=signup, assert_status=201)
