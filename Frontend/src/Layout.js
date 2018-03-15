// Basic Layout with sidebar
// Idea from https://mithril.js.org/simple-application.html
//
// Includes the generic login / logout

import m from 'mithril';
import session from './session';

let nethz = '';
let password = '';
let error = '';

let busy = false;

function login() {
  if (!busy && nethz && password) {
    busy = true;
    session.login(nethz, password).then(() => {
      nethz = '';
      password = '';
      error = '';
      busy = false;
    }).catch((err) => {
      error = err._error.message;
      busy = false;
    });
  }
}

function logout() {
  busy = true;
  session.logout().then(() => {
    busy = false;
    error = '';
  }).catch((err) => {
    error = err._error.message;
    busy = false;
  });
}

class LoginPage {
  static view() {
    return [
      m('h1', 'PVK Tool Demo'),
      m('div', error),
      m('form', [
        m('label', 'nethz'),
        m('input', {
          type: 'text',
          placeholder: 'nethz',
          disabled: busy,
          oninput: m.withAttr('value', (value) => { nethz = value; }),
          value: nethz,
        }),
        m('br'),
        m('label', 'password'),
        m('input', {
          type: 'text',
          placeholder: 'password',
          disabled: busy,
          oninput: m.withAttr('value', (value) => { password = value; }),
          value: password,
        }),
      ]),
      m(
        'input',
        {
          type: 'submit',
          disabled: busy,
          onclick: login,
          value: 'Login',
        },
        '',
      ),
    ];
  }
}


class SidebarHeader {
  static view() {
    return [
      m('h1', 'PVK Tool Demo'),
      m('p', `Hello, ${session.user.name}`),
      m('button', { onclick: logout }, 'Logout'),
      session.admin ? [
        m('br'),
        m('a', { href: '/course', oncreate: m.route.link }, 'User Tools'),
        m('br'),
        m('a', { href: '/admin', oncreate: m.route.link }, 'Admin Tools'),
      ] : [],
    ];
  }
}


export default class Layout {
  static view(vnode) {
    return session.active() ? m('', [
      m('aside', [m(SidebarHeader), m(vnode.attrs.sidebar)]),
      m('main', m(vnode.attrs.content)),
    ]) : m(LoginPage);
  }
}
