"""Tests for the Stripe payment backend"""
import pytest


@pytest.fixture(autouse=True)
def base_data(app):
    """Build test data for the tests."""
    with app.admin():
        lecture_data = {
            'title': 'Awesome Lecture',
            'department': 'itet',
            'year': 3,
        }
        lecture = app.client.post('lectures',
                                  data=lecture_data,
                                  assert_status=201)

        course = {
            'lecture': lecture['_id'],
            'room': 'ETZ F 6',
            'spots': 20,
            'signup': {
                'start': '2021-05-01T10:00:00Z',
                'end': '2021-05-05T23:59:59Z',
            },
            'datetimes': [{
                'start': '2021-06-05T10:00:00Z',
                'end': '2021-06-05T12:00:00Z',
            }, {
                'start': '2021-06-06T10:00:00Z',
                'end': '2021-06-06T12:00:00Z',
            }],
        }
        response = app.client.post('courses',
                                   data=course,
                                   assert_status=201)

        signup = {
            'nethz': 'nethz',  # default dummy value for user nethz
            'course': response['_id']
        }
        app.client.post('signups',
                        data=signup,
                        assert_status=201)


def test_admin(app):
    """Test that an admin may create and delete payments unconditionally"""
    with app.admin():
        # Fetch the _ids of the signups we want to pay for
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Try to create a payment without a token
        payment = {
            'signups': signups,
            'token': None,
        }
        payment_response = app.client.post('payments',
                                           data=payment,
                                           assert_status=201)

        # Check that the signups have been marked as paid
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] == 'accepted'

        # Try to delete the payment
        app.client.delete('payments/{}'.format(payment_response['_id']),
                          headers={'If-Match': payment_response['_etag']},
                          assert_status=204)

        # Check that the signups have been marked as unpaid
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] == 'reserved'


def test_no_multiple_payments_admin(app):
    """Make sure that no signup / course may be paid more than once by an admin"""
    with app.admin():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Pay the signups twice
        payment = {
            'signups': signups,
            'token': None,
        }
        # First payment succeeds
        app.client.post('payments', data=payment, assert_status=201)
        # Second payment fails
        app.client.post('payments', data=payment, assert_status=422)

        # Check that the signups were marked as paid nonetheless
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] == 'accepted'


def test_no_multiple_payments_user(app):
    """Make sure that no signup / course may be paid more than once by a user"""
    with app.user():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Pay the signups twice
        payment = {
            'signups': signups,
            'token': 'tok_visa',
        }

        # First payment succeeds
        app.client.post('payments', data=payment, assert_status=201)
        # Second payment fails
        app.client.post('payments', data=payment, assert_status=422)

        # Check that the signups were marked as paid
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] == 'accepted'


def test_users_require_token(app):
    """Test that regular users must provide a token to create a payment."""
    with app.user():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Try to create a payment without a token
        # We expect this to fail with a validation error
        payment = {
            'signups': signups,
        }
        app.client.post('payments',
                        data=payment,
                        assert_status=422)


def test_valid_card(app):
    """Test that payment succeeds with a valid card.

    'tok_visa' always corresponds to a valid Visa card.
    """
    with app.user():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Try to create a payment with the Visa test token
        # We expect this to succeed
        payment = {
            'signups': signups,
            'token': 'tok_visa',
        }
        app.client.post('payments',
                        data=payment,
                        assert_status=201)

        # Check that the signups were marked as paid
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] == 'accepted'


def test_invalid_card(app):
    """Test that invalid cards yield a status code of 422.

    'tok_chargeDeclined' always causes the transaction to fail.
    """
    with app.user():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Try to create a payment with the charge declined token
        # We expect this to fail
        payment = {
            'signups': signups,
            'token': 'tok_chargeDeclined',
        }
        app.client.post('payments',
                        data=payment,
                        assert_status=422)

        # Check that the signups were NOT marked as paid
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] != 'accepted'


def test_users_cannot_delete(app):
    """Test that regular users cannot delete payments."""
    # Let admin create a payment
    with app.admin():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Try to create a payment without a token
        payment = {
            'signups': signups,
            'token': None,
        }
        payment_response = app.client.post('payments',
                                           data=payment,
                                           assert_status=201)

    with app.user():
        # Let the user try to delete the payment
        app.client.delete('payments/{}'.format(payment_response['_id']),
                          assert_status=403)

        # Make sure the signups are still marked as paid
        signups = app.client.get('signups')['_items']
        for signup in signups:
            assert signup['status'] == 'accepted'


def test_signup_unique_per_payment(app):
    """Test that the same signup only appears once per payment"""
    with app.admin():
        # Fetch the signups we want to pay
        signups = [signup['_id'] for signup in app.client.get('signups')['_items']]

        # Duplicate the list so every signup appears twice
        signups.extend(signups)

        # Try to create a payment
        # We expect a validation error
        payment = {
            'signups': signups,
            'token': None,
        }
        app.client.post('payments',
                        data=payment,
                        assert_status=422)
