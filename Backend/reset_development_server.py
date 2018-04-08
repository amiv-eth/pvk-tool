"""Demo Data.

This script can be used to reset the demo data on the development server.
You need to have 'requests' installed!

CAREFUL: This script will delete everything existing!
"""

import sys
from random import randint, sample
from datetime import datetime as dt, timedelta
import requests


AMIVAPI_DEV_URL = "https://api-dev.amiv.ethz.ch"
PVK_DEV_URL = 'https://pvk-api-dev.amiv.ethz.ch'

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# Number of courses
MIN_CLOSED = 1
MAX_CLOSED = 3
MIN_OPEN = 2
MAX_OPEN = 4
# Spots per course
MIN_SPOTS = 20
MAX_SPOTS = 40
NUM_TIMESLOTS = 20  # limited number of unique timeslots to get overlap


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
            }
            response = post('lectures', data, token)
            if response:
                lectures.append(response['_id'])

    return lectures


def create_assistants(token):
    """Create a new assistant, yield _id."""
    i = 0
    while True:
        data = {
            'name': 'Pablo%s' % i,
            'email': 'pablo_%s@amiv.ethz.ch' % i,
        }
        response = post('assistants', data, token)
        yield response['_id']
        i += 1


def room_gen():
    """Produce rooms."""
    i = 0
    while True:
        yield "ETZ E %d" % i
        i += 1


def nethz_gen():
    """Produce nethz."""
    i = 0
    while True:
        yield "s%d" % i
        i += 1


def timeslots(starting_day):
    """Produce a stream of non-overlapping time ranges."""
    result = [];
    for _ in range(0, NUM_TIMESLOTS):
        year = starting_day.year
        month = starting_day.month
        day = starting_day.day

        # Random start and end time
        start = dt(year, month, day, randint(7, 10)).strftime(DATE_FORMAT)
        end = dt(year, month, day, randint(11, 14)).strftime(DATE_FORMAT)
        result.append({'start': start, 'end': end})

        # Only one slot per day to avoid overlap
        starting_day += timedelta(days=1)

    return result


ROOM = room_gen()
NETHZ = nethz_gen()
TIMESLOTS = timeslots(dt.now() + timedelta(days=90))  # Some time in the future


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

        'datetimes': sample(TIMESLOTS, randint(1, 3)),
        'room': next(ROOM),
        'spots': randint(MIN_SPOTS, MAX_SPOTS),
    }
    response = post('courses', data, token)

    return response


def create_signups(course, token):
    """Create random number of signups to a course."""
    for _ in range(randint(0, 2*MAX_SPOTS)):
        data = {
            'nethz': next(NETHZ),  # All different nethz to avoid overlap
            'course': course['_id'],
        }
        post('signups', data, token)


def clear(resource, token):
    """ Remove every item."""
    while True:
        items = requests.get('%s/%s' % (PVK_DEV_URL, resource),
                             headers={'Authorization': token}).json()['_items']

        if not items:
            return  # Done!

        for item in items:
            item_url = '%s/%s/%s' % (PVK_DEV_URL, resource, item['_id'])
            res = requests.delete(item_url,
                                  headers={'Authorization': token,
                                           'If-Match': item['_etag']})
            if res.status_code != 204:
                print(res.json())


def main():
    """Login and create demo data."""
    if len(sys.argv) != 3:
        print('Usage: python %s USERNAME PASSWORD' % sys.argv[0])
        sys.exit(-1)

    print('Logging in...')
    token = login(sys.argv[1], sys.argv[2])

    # Order is important! some things can't be deleted before others
    print('Clearing existing data...')
    for res in ['payments', 'signups', 'courses', 'selections', 'lectures',
                'assistants']:
        print('Removing %s...' % res)
        clear(res, token)

    # Init generator for assistants
    assistants = create_assistants(token)

    # Create data
    # (Repeat for itet and mavt)
    for department in ['itet', 'mavt']:
        print('Department: %s' % department)

        print('Creating lectures...')
        lectures = create_lectures(department, token)

        print('Creating courses with closed signup...')
        for lecture in lectures:
            for _ in range(randint(MIN_CLOSED, MAX_CLOSED)):
                create_course(lecture, next(assistants),
                              token, open_signup=False)

        print('Creating courses with open signup...')
        courses = []
        for lecture in lectures:
            for _ in range(randint(MIN_OPEN, MAX_OPEN)):
                courses.append(create_course(lecture, next(assistants), token))

        print('Creating signups...')
        for course in courses:
            create_signups(course, token)


if __name__ == '__main__':
    main()
