// Stripe Frontend Script
import m from 'mithril';
import { Dialog } from 'polythene-mithril';
import { userCourses, pvkApiUrl } from './backend';
import session from './session';


const handler = StripeCheckout.configure({
  // TODO: Change test key and image url
  key: 'pk_test_Gp4vLvlcgFGUcjv89WiTb8m7',
  image: 'https://www.amiv.ethz.ch/system/files/file_upload/3645/LOGO_FINAL_NO_TEXT.png',
  locale: 'auto',
  allowRememberMe: false,
  token: (token) => {
    m.request({
      method: 'POST',
      url: `${pvkApiUrl}/payments`,
      data: {
        signups: userCourses.reserved.map(signup => signup._id),
        token: token.id,
      },
      headers: {
        Authorization: `Token ${session.data.token}`,
      },
    }).then(() => {
      // Update the sidebar
      userCourses.getAll();
      // Show a confirmation dialog
      Dialog.show({
        title: 'Thanks for your payment!',
        body: 'You will receive a confirmation e-mail within the next few minutes.',
      });
    }).catch((err) => {
      // Show an error dialog
      const title = err.code === 500 ? 'Server error' : 'Payment failed';

      // show the backend's error message
      const res = JSON.parse(err.message);

      Dialog.show({
        title,
        body: res._error.message,
      });
    });
  },
});


// Close Checkout on page navigation:
window.addEventListener('popstate', () => {
  handler.close();
});

export default handler;
