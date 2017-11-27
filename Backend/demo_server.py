"""Demo Server.

Add some demo data to the database and run the app.
"""

from os import getenv
from random import randint
from datetime import datetime as dt, timedelta
import json

from flask import g

from app import create_app


HOST = getenv('PVK_HOST', '0.0.0.0')
PORT = getenv('PVK_PORT', '80')

APP = create_app()
CLIENT = APP.test_client()
DATE_FORMAT = APP.config['DATE_FORMAT']
ASSISTANTS = ['pablo', 'assi', 'anon', 'mongo']
MIN_SPOTS = 20
MAX_SPOTS = 40

"""
# Clear everything
from pymongo import MongoClient

connection = MongoClient(APP.config['MONGO_HOST'],
                         APP.config['MONGO_PORT'])
connection.drop_database(APP.config['MONGO_DBNAME'])
connection.close()
"""


def post(resource, data):
    """Create something, ignoring auth."""
    with APP.test_request_context():
        g.apiuser = 'Not None :)'
        g.nethz = 'Something'
        g.admin = True

        response = CLIENT.post('%s/%s' % (APP.config['URL_PREFIX'], resource),
                               data=json.dumps(data),
                               content_type="application/json",
                               headers={'Authorization': 'Token Lala'})

        if response.status_code != 201:
            error = json.loads(response.get_data(as_text=True))
            status = error['_error']['code']
            message = str(error['_error'].get('message', ''))
            issues = str(error.get('_issues', ''))
            print('%s:' % status, issues or message)
            return {}

        return json.loads(response.get_data(as_text=True))


def create_lectures(department):
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
            response = post('lectures', data)
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


def create_course(lecture, assistant, open_signup=True):
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
    return post('courses', data)['_id']


def create_signups(course):
    """Create random number of signups to a course."""
    for n in range(randint(0, 2*MAX_SPOTS)):
        data = {
            'nethz': 'student%d' % n,
            'course': course
        }
        post('signups', data=data)


if __name__ == '__main__':
    # Create courses
    # (Repeat for itet and mavt)
    for department in ['itet', 'mavt']:
        # Create a few lectures
        lectures = create_lectures(department)

        # Create a few courses with closed signup
        for lecture in lectures:
            for n in range(randint(0, 2)):
                create_course(lecture, ASSISTANTS[n], open_signup=False)

        # Create a few courses with open signup
        courses = []
        for lecture in lectures:
            for n in range(randint(2, len(ASSISTANTS))):
                courses.append(create_course(lecture, ASSISTANTS[n]))

        # Create signups for courses
        for course in courses:
            create_signups(course)

    # Start the app
    APP.run(host=HOST, port=int(PORT))
