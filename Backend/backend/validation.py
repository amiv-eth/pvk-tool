"""Custom Validators

We require several custom validation rules, e.g. that user can only use their
own nethz.

Learn how validation works [here](http://python-eve.org/validation.html).

TODO: Several validation rules still need to be implemented. See `settings.py`.

"""

from itertools import combinations, chain

from flask import request, current_app
from eve.io.mongo import Validator

from backend.security import is_admin, get_user


class APIValidator(Validator):
    """Provide a rule to check nethz of current user."""

    def _get_field(self, field):
        """Get other field. Check original document as well if PATCH."""
        if request.method != 'PATCH':
            return self.document.get(field)
        # PATCH: field is only in self.document if modified
        return self.document.get(field) or self._original_document.get(field)

    # nethz validation

    def _validate_only_own_nethz(self, enabled, field, value):
        """If the user is no admin, only own nethz is allowed for singup.

        Furthermore, the user must be a member to use his nethz.
        Only admins can sign up someone else.
        """
        if enabled and not is_admin():
            if value != get_user().get('nethz'):
                self._error(field,
                            "you can only use your own nethz to sign up")
            # If the nethz matches, we have to check if the user is a member
            elif get_user().get('membership') == 'none':
                self._error(field,
                            "only members can sign up")

    # Various helpers

    def _validate_unique_combination(self, unique_combination, field, value):
        """Validate that a combination of fields is unique.

        Code is copy-pasted from amivapi, see there for more explanation.
        https://github.com/amiv-eth/amivapi/blob/master/amivapi/utils.py
        """
        lookup = {field: value}  # self
        for other_field in unique_combination:
            lookup[other_field] = self._get_field(other_field)

        resource = self.resource
        if current_app.data.find_one(resource, None, **lookup) is not None:
            self._error(field, "value already exists in the database in " +
                        "combination with values for: %s" %
                        unique_combination)

    def _validate_not_patchable(self, enabled, field, _):
        """Inhibit patching of the field, also copied from AMIVAPI."""
        if enabled and (request.method == 'PATCH'):
            self._error(field, "this field can not be changed with PATCH")

    def _validate_only_admin_empty(self, only_admin_empty, field, value):
        """Allow the field to be empty only if the user is admin."""
        if only_admin_empty and not value and not is_admin():
            self._error(field, "only admins may leave this field empty")

    def _validate_no_waiting(self, no_waiting, field, value):
        """Disallow signups which are on waiting list status."""
        signup = current_app.data.driver.db['signups'].find_one({'_id': value})
        if no_waiting and signup['status'] == 'waiting':
            self._error(field, "this field may not contain signups " +
                        "which are still on the waiting list")

    def _validate_no_accepted(self, no_accepted, field, value):
        """Disallow signups that have already been paid."""
        signup = current_app.data.driver.db['signups'].find_one({'_id': value})
        if no_accepted and signup['status'] == 'accepted':
            self._error(field, "this field may not contain signups " +
                        "which have already been paid")

    def _validate_no_copies(self, no_copies, field, value):
        """Ensure that each item only appears once in the list."""
        if no_copies and len(set(value)) != len(value):
            self._error(field, "this field may not contain duplicate signups")

    # Time related

    def _validate_start_before_end(self, enabled, field, value):
        """Ensure that the start time is before the end time."""
        if enabled and(value.get('start') > value.get('end')):
            self._error(field, 'start time must be earlier then end time.')

    def _validate_unique_room_booking(self, enabled, field, value):
        """A room can not be used at the same time by several courses."""
        # Compatibility with both room and datetime fields for POST and PATCH
        room = self._get_field('room')
        timespans = self._get_field('datetimes')

        # Get _id of current course and filter to ignore it
        course_id = self._get_field('_id')
        id_filter = {'_id': {'$ne': course_id}} if course_id else {}

        if enabled and timespans and room:
            # Get all other courses with the same room
            course_db = current_app.data.driver.db['courses']
            courses = course_db.find({'room': room, **id_filter})
            # chain all timespan lists into one list of other timespans
            other_timespans = chain.from_iterable(course['datetimes']
                                                  for course in courses)

            if has_overlap(*timespans, *other_timespans):
                self._error(field, "the room '%s' is already occupied by "
                                   "another course at the same time" % value)

    def _validate_unique_assistant_booking(self, enabled, field, value):
        """An assistant can not hold several courses simultaneously."""
        # See room booking comments
        assistant = self._get_field('assistant')
        timespans = self._get_field('datetimes')

        course_id = self._get_field('_id')
        id_filter = {'_id': {'$ne': course_id}} if course_id else {}

        if enabled and timespans and assistant:
            course_db = current_app.data.driver.db['courses']
            courses = course_db.find({'assistant': assistant, **id_filter})
            other_timespans = chain.from_iterable(course['datetimes']
                                                  for course in courses)

            if has_overlap(*timespans, *other_timespans):
                self._error(field, "the assistant '%s' is giving "
                                   "another course at the same time" % value)

    def _validate_no_time_overlap(self, enabled, field, value):
        """Multiple timeslots of the same course must not overlap."""
        # value will be a list of timeslots
        if enabled and has_overlap(*value):
            self._error(field, "time slots must not overlap")

    def _validate_no_course_overlap(self, resource, field, value):
        """Ensure that a user cannot select/sign up for parallel courses."""
        nethz = self._get_field('nethz')

        # Get timespan of current course
        course_db = current_app.data.driver.db['courses']
        timespans = course_db.find_one({'_id': value}).get('datetimes')

        if nethz and timespans:
            # Find ids from all other courses for this nethz
            resource_db = current_app.data.driver.db[resource]
            items = resource_db.find({'nethz': nethz})
            course_ids = [item['course'] for item in items
                          if item['course'] != value]

            # Get all courses and extract time spans
            courses = course_db.find({'_id': {'$in': course_ids}})
            # chain all timespan lists into one list of other timespans
            other_timespans = chain.from_iterable(course['datetimes']
                                                  for course in courses)

            if has_overlap(*timespans, *other_timespans):
                self._error(field, 'this course has a timing conflict with an '
                                   'already chosen course')


def has_overlap(*timeslots):
    """Return True if any two timeslots overlap, False otherwise."""
    def has_one_overlap(first, second):
        """Compare two timeslots."""
        # All data is UTC, but some has tzinfo, some doesnt => Normalize
        s_1 = first['start'].replace(tzinfo=None)
        e_1 = first['end'].replace(tzinfo=None)
        s_2 = second['start'].replace(tzinfo=None)
        e_2 = second['end'].replace(tzinfo=None)
        # Overlap if one course is "(not before) and (not after)" the other
        return (e_1 > s_2) and (s_1 < e_2)

    # Return if *any* combination of elements overlaps
    return any(has_one_overlap(first, second)
               for (first, second) in combinations(timeslots, 2))
