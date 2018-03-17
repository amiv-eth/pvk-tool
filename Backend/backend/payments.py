"""Handle Stripe API interactions."""
from flask import abort
import stripe

from backend.settings import COURSE_PRICE, STRIPE_API_KEY
from backend.signups import mark_as_paid


stripe.api_key = STRIPE_API_KEY


def create_payment(payments):
    """Create a charge with the Stripe API.

    on_insert_payments hook

    items is guaranteed to only contain items that have passed validation.
    """

    # We don't want payment to be a list
    payment = payments[0]

    # We don't accept free money
    if not payment['signups']:
        abort(400, 'Payment must be for at least one signup')

    # For now we assume a constant price per course
    amount = len(payment['signups']) * COURSE_PRICE

    # If no token is set, we're dealing with an admin payment
    # Thus, no call to the Stripe API is made
    if not payment.get('token'):
        return True

    # Create a new charge
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='CHF',
            source=payment['token'],
        )
    except stripe.error.CardError:
        # Something's wrong with the card
        abort(422, 'Card declined')
    except stripe.error.RateLimitError:
        # Too many requests made to the API too quickly
        abort(429, 'Too many requests')
    except stripe.error.InvalidRequestError:
        # Invalid parameters were supplied to Stripe's API
        abort(500, 'Invalid call to Stripe API')
    except stripe.error.AuthenticationError:
        # Authentication with Stripe's API failed
        abort(500, 'Authentication with Stripe API failed')
    except stripe.error.APIConnectionError:
        # Network communication with Stripe failed
        abort(500, 'Failed to connect to Stripe API')
    except stripe.error.StripeError:
        # Some error to do with Stripe
        abort(500, 'Stripe payment processing failed')

    # Charge succeeded, save the charge id in the database
    payment['charge_id'] = charge.id

    # Mark corresponding signups as paid
    mark_as_paid([payment])

    return True
