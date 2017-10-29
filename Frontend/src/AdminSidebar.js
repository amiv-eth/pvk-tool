// Nothing yet

const m = require('mithril');

module.exports = {
  view() {
    return [
      m('h2', 'Administration'),
      m('a', { href: '/admin', oncreate: m.route.link }, 'Course Overview'),
    ];
  },
};
