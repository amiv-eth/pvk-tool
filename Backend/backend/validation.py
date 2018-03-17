"""Custom Validators

We require several custom validation rules, e.g. that user can only use their
own nethz.

Learn how validation works [here](http://python-eve.org/validation.html).

TODO: Several validation rules still need to be implemented. See `settings.py`.

"""

from flask import request, current_app
from eve.io.mongo import Validator

from backend.security import is_admin, get_nethz


class APIValidator(Validator):
    """Provide a rule to check nethz of current user."""

    def _validate_only_own_nethz(self, enabled, field, value):
        """If the user is no admin, only own nethz is allowed for singup."""
        if enabled and not is_admin():
            if value != get_nethz():
                self._error(field,
                            "You can only use your own nethz to sign up.")

    def _validate_unique_combination(self, unique_combination, field, value):
        """Validate that a combination of fields is unique.

        Code is copy-pasted from amivapi, see there for more explanation.
        https://github.com/amiv-eth/amivapi/blob/master/amivapi/utils.py
        """
        lookup = {field: value}  # self
        for other_field in unique_combination:
            lookup[other_field] = self.document.get(other_field)

        if request.method == 'PATCH':
            original = self._original_document
            for key in unique_combination:
                if key not in self.document.keys():
                    lookup[key] = original[key]

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
        """Ensure that each signup only appears once per payment."""
        if no_copies and len(set(value)) != len(value):
            self._error(field, "this field may not contain duplicate signups")
