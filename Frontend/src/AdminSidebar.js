// Placeholder

import m from 'mithril';

export default class AdminSidebar {
  static view() {
    return [
      m('h2', 'Administration'),
      m('a', { href: '/admin', oncreate: m.route.link }, 'Course Overview'),
    ];
  }
}
