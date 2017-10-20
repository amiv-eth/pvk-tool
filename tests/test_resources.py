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
            'start': 'Mon, 01 Jun 2020 01:15:00 GMT',
            'end': 'Mon, 01 Jun 2020 04:15:00 GMT',
        },
        'datetimes': [{
            'start': 'Mon, 01 Jun 2020 08:15:00 GMT',
            'end': 'Mon, 01 Jun 2020 08:15:00 GMT',
            }, {
            'start': 'Tue, 02 Jun 2020 08:15:00 GMT',
            'end': 'Tue, 02 Jun 2020 08:15:00 GMT',
            }],
    }
    course_response = client.post('courses', data=course, assert_status=201)

    signup = {
        'nethz': "Pablito",
        'course': course_response['_id']
    }
    client.post('signups', data=signup, assert_status=201)
