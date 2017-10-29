// User Sidebar

const m = require('mithril');

module.exports = {
  view() {
    return [
      m('h2', 'Your Courses'),
      m('p', 'You are not signed up for anything yet.'),
    ];
  },
};
