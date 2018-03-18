// Stripe Frontend Script
import m from 'mithril';
import { userCourses, pvkApiUrl } from './backend';


const handler = StripeCheckout.configure({
  // TODO: Change test key and image url
  key: 'pk_test_Gp4vLvlcgFGUcjv89WiTb8m7',
  image: 'https://www.amiv.ethz.ch/system/files/file_upload/3645/LOGO_FINAL_NO_TEXT.png',
  locale: 'auto',
  allowRememberMe: false,
  token: (token) => {
    // You can access the token ID with `token.id`.
    // Get the token ID to your server-side code for use.
    m.request({
      method: 'POST',
      url: ':pvkApiUrl/payments',
      data: {
        pvkApiUrl,
        signups: userCourses.reserved.map(signup => signup._id),
        token: token.id,
      },
    }).then(() => {
      userCourses.getAll();
    });
  },
});


// Close Checkout on page navigation:
window.addEventListener('popstate', () => {
  handler.close();
});

export default handler;
