/* eslint linebreak-style: ['error', 'windows'] */
// User Sidebar
import Pvk from './Pvk';

const m = require('mithril');

module.exports = {
  view() {
    return [
      m('h2', 'Your Courses'),
      m('p', 'You are not signed up for anything yet.'),
      m('p', `Amnt of Pvks:  ${Pvk.list.length}`),
    ];
  },
};
