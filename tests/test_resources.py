"""Tests for basic requests to all resources."""


from flask import g


def test_create(app):
    """Test creating everything as an admin user."""
    with app.test_request_context():
        # Fake a admin user
        g.user = 'Not None :)'
        g.admin = True
        faketoken = {'Authorization': 'Token Trolololo'}

        lecture = {
            'title': "Awesome Lecture",
            'department': "itet",
            'year': 3,
        }
        lecture_response = app.client.post('lectures',
                                           data=lecture,
                                           headers=faketoken,
                                           assert_status=201)

        assistant = {'nethz': "Pablo"}
        assistant_response = app.client.post('assistants',
                                             data=assistant,
                                             headers=faketoken,
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
        course_response = app.client.post('courses',
                                          data=course,
                                          headers=faketoken,
                                          assert_status=201)

        signup = {
            'nethz': "Pablito",
            'course': course_response['_id']
        }
        app.client.post('signups',
                        data=signup,
                        headers=faketoken,
                        assert_status=201)

def test_no_double_signup(app):
    """Users can signup for several courses, but not for any course twice."""
    with app.test_request_context():
        # Fake a admin user
        g.user = 'Not None :)'
        g.admin = True
        faketoken = {'Authorization': 'Token Trolololo'}

        # Create two fake courses to sign up to
        first = str(app.data.driver.db['courses'].insert({}))
        second = str(app.data.driver.db['courses'].insert({}))

        def _signup(course, assert_status):
            signup = {
                'nethz': "Pablito",
                'course': course
            }
            app.client.post('signups',
                            data=signup,
                            headers=faketoken,
                            assert_status=assert_status)

        # No Double signup to same course
        _signup(first, 201)
        _signup(first, 422)
        # Sign up to other courses still fine
        _signup(second, 201)
