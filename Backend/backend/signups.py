"""Signup processing (Waiting list and payments).

So far only dummy functionality, i.e. if a payment is posted, all courses
are set to accepted.

As soon as we have payment service provider, the definite functionality needs
to be implemented.

TODO: Send notification mails
"""

import json
from functools import wraps
from itertools import chain

from bson import ObjectId
from flask import current_app, abort
from eve.methods.patch import patch_internal


def wrap_response(function):
    """Wrapper to modify payload for successful requests (status 2xx)."""
    @wraps(function)
    def _wrapped(_, response):
        if response.status_code // 100 == 2:
            payload = json.loads(response.get_data(as_text=True))

            if '_items' in payload:
                function(payload['_items'])
            else:
                function([payload])

            response.set_data(json.dumps(payload))
    return _wrapped


@wrap_response
def new_signups(signups):
    """Update the status for all signups to a course."""
    def get_id(course):
        """Return the course id, necessary to cope with embedding.

        If the client requests `course` to be embedded, it will be a dict
        with the id as key. Otherwise `course` will be just the id.
        """
        return course['_id'] if isinstance(course, dict) else course

    # Remove duplicates by using a set
    courses = set(get_id(item['course']) for item in signups)
    # Re-format signups into a dict so we can update them easier later
    signups_by_id = {str(item['_id']): item for item in signups}

    modified = chain.from_iterable(update_signups(course)
                                   for course in courses)

    for _id in modified:
        # Update response payload if needed
        try:
            signups_by_id[_id]['status'] = 'reserved'
        except AttributeError:
            pass  # Not in response, nothing to do


def deleted_signup(signup):
    """Update status of course the signup belonged to."""
    update_signups(signup['course'])


def patched_signup(update, original):
    """Update status of all signups of the original and new course."""
    # Only need to do something if course is changed
    if 'course' in update:
        update_signups(update['course'])
        update_signups(original['course'])


def patched_course(update, original):
    """If the number of spots changed, update signups of course."""
    if 'spots' in update:
        update_signups(original['_id'])


def block_course_deletion(course):
    """If a course has signups, it can't be deleted."""
    count = current_app.data.driver.db['signups'].count({
        'course': course['_id']
    })

    if count > 0:
        abort(409, "Course cannot be deleted as long as it has signups.")


def update_signups(course_id):
    """Update waiting list for a course.

    The course id can be given as string or ObjectId.

    We can assume that the course exists, otherwise Eve stops earlier.

    Return list of ids of all reserved signups.
    """
    course_id = ObjectId(course_id)  # Ensure we are working with ObjectId

    # Determine how many spots the course has
    total_spots = (current_app.data.driver.db['courses']
                   .find_one({'_id': course_id}, projection={'spots': 1})
                   .get('spots', 0))

    # Next, count current signups not on waiting list
    signups = current_app.data.driver.db['signups']
    taken_spots = signups.count({'course': course_id,
                                 'status': {'$ne': 'waiting'}})

    available_spots = total_spots - taken_spots

    if available_spots <= 0:
        return []

    # Finally, get as many signups on the waiting list as spots available
    # sort by _updated, use nethz as tie breaker
    chosen_signups = signups.find({'course': course_id,
                                   'status': 'waiting'},
                                  projection=['_id'],
                                  sort=[('_updated', 1), ('nethz', 1)],
                                  limit=available_spots)

    signup_ids = [item['_id'] for item in chosen_signups]

    signups.update_many({'_id': {'$in': signup_ids}},
                        {'$set': {'status': 'reserved'}})

    return [str(item) for item in signup_ids]


def mark_as_paid(payments):
    """After successful payment, set status to `accepted`."""
    # Check if payments is not a list
    if not isinstance(payments, list):
        payments = [payments]

    for payment in payments:

        for signup in payment['signups']:
            data = {'status': 'accepted'}
            patch_internal('signups',
                           _id=str(signup),
                           payload=data,
                           concurrency_check=False,
                           skip_validation=True)


def mark_as_unpaid(payments):
    """Before a payment is deleted, set status to `reserved`."""
    # Check if payments is not a list
    if not isinstance(payments, list):
        payments = [payments]

    for payment in payments:

        for signup in payment['signups']:
            data = {'status': 'reserved'}
            patch_internal('signups',
                           _id=str(signup),
                           payload=data,
                           concurrency_check=False,
                           skip_validation=True)
