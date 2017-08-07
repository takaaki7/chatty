from logging import getLogger

import stripe
from bottle import abort, HTTPError

from chatty import config
from chatty import session_scope
from chatty.domain.model.match import User
from chatty.domain.model.points import MenuPrice, Payment, PaymentSource
from chatty.domain.user_state import UserContext
from chatty.libs import slack

logger = getLogger(__name__)
stripe.api_key = config.STRIPE_SECRET_KEY

MESSAGE_CONTACT_US = "Your payment failed. Please try again later. If the problem persists, please contact us at https://m.me/ChattySupport"
MESSAGE_TOO_MATCH_POINTS = "Payment canceled because points exceeded the limit."
MESSAGE_CONTACT_CREDIT = "Please check whether the credit card information that you entered is incorrect, or your credit limit has been exceeded.\n"
"If there are no mistakes in your input, and the same error still appears after you have tried again, then please contact your credit card company."


@session_scope
def pay_from_form(puid, token, points, price, currency):
    if not MenuPrice.is_valid(points, price, currency):
        abort(400,
              "Payment failed due to expiration of token. Please refresh your web browser and then try again.")
    astr = "{} {} {} {}".format(puid, token, points, price, currency)

    def translate(text):
        return uc._(text) if uc is not None else text

    try:
        user = User.get(puid)
        uc = UserContext(user)
        if user.points + points > 4000:
            abort(400, MESSAGE_TOO_MATCH_POINTS)
        customer = stripe.Customer.create(
            source=token,
            metadata={'puid': puid, 'fb_id': user.fb_id}
        )
        PaymentSource.create(user.fb_id, customer.id)
        charge = stripe.Charge.create(
            amount=price,
            currency=currency.lower(),
            description="Chatty: {} points".format(points),
            customer=customer.id,
            metadata={'puid': puid, 'fb_id': user.fb_id}
        )
        user.points += int(points)
        Payment.create(charge.id, user.fb_id, customer.id, points,
                       price, currency.lower())
        # https://stripe.com/docs/api#error_handling
        # https://stripe.com/docs/declines#decline-codes

    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        logger.error("Failed payment {} {} ".format(astr, e.json_body))
        abort(400, translate(MESSAGE_CONTACT_CREDIT))
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        abort(400, translate(MESSAGE_CONTACT_US))
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        slack.post("Failed payment {} {}".format(astr, e.json_body))
        abort(400, translate(MESSAGE_CONTACT_US))
    except stripe.error.AuthenticationError as e:
        slack.post("Failed payment {} {}".format(astr, e.json_body))
        abort(400, translate(MESSAGE_CONTACT_US))
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        abort(400, translate(MESSAGE_CONTACT_US))
    except stripe.error.StripeError as e:
        slack.post("Failed payment {} {}".format(astr, e.json_body))
        # Display a very generic error to the user, and maybe send
        # yourself an email
        abort(400, translate(MESSAGE_CONTACT_US))
    except HTTPError as e:
        raise e
    except Exception as e:
        slack.post("Failed payment {} {}".format(astr, e.message))
        # Something else happened, completely unrelated to Stripe
        abort(400, translate(MESSAGE_CONTACT_US))
    return user.points
