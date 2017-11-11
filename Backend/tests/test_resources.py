"""Tests for basic requests to all resources as admin."""


def test_create(app):
    """Test creating everything as an admin user."""
    with app.admin():
        lecture = {
            'title': "Awesome Lecture",
            'department': "itet",
            'year': 3,
            'assistants': ['pablo', 'pablone'],
        }
        lecture_response = app.client.post('lectures',
                                           data=lecture,
                                           assert_status=201)

        course = {
            'lecture': lecture_response['_id'],
            'assistant': 'pablo',
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
                                          assert_status=201)

        selection = {
            'nethz': 'Pablito',
            'courses': [course_response['_id']]
        }
        app.client.post('selections', data=selection, assert_status=201)

        signup = {
            'nethz': "Pablito",
            'course': course_response['_id']
        }
        signup_response = app.client.post('signups',
                                          data=signup,
                                          assert_status=201)

        payment = {'signups': [signup_response['_id']]}
        app.client.post('payments', data=payment, assert_status=201)


def test_no_double_signup(app):
    """Users can signup for several courses, but not for any course twice."""
    with app.admin():
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
                            assert_status=assert_status)

        # No Double signup to same course
        _signup(first, 201)
        _signup(first, 422)
        # Sign up to other courses still fine
        _signup(second, 201)


def test_no_patch(app):
    """Test that certain fields cannot be changed.

    These are: Course->lecture and signup->nethz
    """
    no_patch_error = "this field can not be changed with PATCH"
    with app.admin():
        headers = {'If-Match': 'tag'}

        # Create fake resources, make sure to set _etag so we can patch
        course = str(app.data.driver.db['courses'].insert({'_etag': 'tag'}))
        signup = str(app.data.driver.db['signups'].insert({'_etag': 'tag'}))
        # Make sure that the objectid of patch data is valid
        new_lecture = str(app.data.driver.db['lectures'].insert({}))

        course_url = '/courses/' + course
        signup_url = '/signups/' + signup

        response = app.client.patch(course_url, headers=headers,
                                    data={'lecture': new_lecture},
                                    assert_status=422)
        assert response["_issues"]["lecture"] == no_patch_error
        response = app.client.patch(signup_url, headers=headers,
                                    data={'nethz': 'lalala'},
                                    assert_status=422)
        assert response["_issues"]["nethz"] == no_patch_error
