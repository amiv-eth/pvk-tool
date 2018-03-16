"""Demo Data.

This script can be used to create demo data on the development server.

TODO: Accept user and password from command line, provide output
"""

import sys
from random import randint
from datetime import datetime as dt, timedelta
import requests

AMIVAPI_DEV_URL = "https://amiv-api.ethz.ch"
PVK_DEV_URL = 'http://localhost:8080'  # 'http://pvk-api-dev.amiv.ethz.ch'

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
ASSISTANTS = ['pablo', 'assi', 'anon', 'mongo']
MIN_SPOTS = 20
MAX_SPOTS = 40


def login(username, password):
    """Login user, return token."""
    data = {
        'username': username,
        'password': password,
    }
    return requests.post("%s/%s" % (AMIVAPI_DEV_URL, 'sessions'),
                         json=data).json()['token']


def post(resource, data, token):
    """Create something, ignoring auth."""
    response = requests.post('%s/%s' % (PVK_DEV_URL, resource),
                             json=data,
                             headers={'Authorization': token})
    data = response.json()

    if response.status_code != 201:
        status = data['_error']['code']
        message = str(data['_error'].get('message', ''))
        issues = str(data.get('_issues', ''))
        print('%s:' % status, issues or message)
        return {}

    return data


def create_lectures(department, token):
    """Create a few lectures, return names."""
    lectures = []
    for lecture in ['Some %s Lecture', 'Cool %s Lecture', 'Boring %s Lecture']:
        for year in range(1, 3):
            special_name = '%s Year %s' % (department.upper(), year)

            data = {
                'title': lecture % special_name,
                'year': year,
                'department': department,
                'assistants': ASSISTANTS,
            }
            response = post('lectures', data, token)
            if response:
                lectures.append(response['_id'])

    return lectures


def room_gen():
    """Produce rooms."""
    i = 0
    while True:
        yield "ETZ E %d" % i
        i += 1


def time_gen(starting_day):
    """Produce a stream of non-overlapping time ranges."""
    while True:
        year = starting_day.year
        month = starting_day.month
        day = starting_day.day

        # Random start and end time
        start = dt(year, month, day, randint(7, 10)).strftime(DATE_FORMAT)
        end = dt(year, month, day, randint(11, 14)).strftime(DATE_FORMAT)
        yield {'start': start, 'end': end}

        # Only one slot per day to avoid overlap
        starting_day += timedelta(days=1)


ROOM = room_gen()
TIME = time_gen(dt.now() + timedelta(days=90))  # Sometime in the future


def create_course(lecture, assistant, token, open_signup=True):
    """Create several course for each lecture."""
    signup_diff = timedelta(days=-5) if open_signup else timedelta(15)
    start = dt.utcnow() + signup_diff
    end = start + timedelta(days=15)

    data = {
        'lecture': lecture,
        'assistant': assistant,

        'signup': {
            'start': start.strftime(DATE_FORMAT),
            'end': end.strftime(DATE_FORMAT),
        },

        'datetimes': [next(TIME) for _ in range(randint(1, 3))],
        'room': next(ROOM),
        'spots': randint(MIN_SPOTS, MAX_SPOTS),
    }
    return post('courses', data, token)['_id']


def create_signups(course, token):
    """Create random number of signups to a course."""
    for ind in range(randint(0, 2*MAX_SPOTS)):
        data = {
            'nethz': 'student%d' % ind,
            'course': course
        }
        post('signups', data, token)


def main():
    """Login and create demo data."""
    if len(sys.argv) != 3:
        print('Usage: python %s USERNAME PASSWORD' % sys.argv[0])
        sys.exit(-1)

    print('Logging in...')
    token = login(sys.argv[1], sys.argv[2])

    # Create courses
    # (Repeat for itet and mavt)
    for department in ['itet', 'mavt']:
        print('Department: %s' % department)

        print('Creating lectures...')
        lectures = create_lectures(department, token)

        print('Creating courses with closed signup...')
        for lecture in lectures:
            for ind in range(randint(0, 2)):
                create_course(lecture, ASSISTANTS[ind],
                              token, open_signup=False)

        print('Creating courses with closed signup...')
        courses = []
        for lecture in lectures:
            for ind in range(randint(2, len(ASSISTANTS))):
                courses.append(create_course(lecture, token, ASSISTANTS[ind]))

        print('Creating signups...')
        for course in courses:
            create_signups(course, token)


if __name__ == '__main__':
    main()
