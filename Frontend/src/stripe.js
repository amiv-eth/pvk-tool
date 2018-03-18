// Stripe Frontend

// stripe-checkout is loaded in index.html. Other methods of loading it are
// not officially supported. [Docs](https://stripe.com/docs/checkout)

import { Dialog } from 'polythene-mithril';
import { stripeKey } from 'config';
import { userCourses, request } from './backend';
import logo from './amiv_logo_no_text.svg';


const handler = StripeCheckout.configure({
  key: stripeKey,
  image: logo,
  locale: 'auto',
  allowRememberMe: false,
  token(token) {
    return request({
      resource: 'payments',
      method: 'POST',
      data: {
        signups: userCourses.reserved.map(signup => signup._id),
        token: token.id,
      },
    }).then(() => {
      // Update the sidebar
      userCourses.getAll();
      // Show a confirmation dialog
      Dialog.show({
        title: 'Thanks for your payment!',
        body: 'You will receive a confirmation e-mail within the next ' +
              'few minutes.',
      });
    }).catch((err) => {
      // Show an error dialog
      Dialog.show({
        title: err.code === 500 ? 'Server error' : 'Payment failed',
        body: err._error.message,
      });
    });
  },
});


// Close Checkout on page navigation:
window.addEventListener('popstate', () => {
  handler.close();
});

export default handler;
