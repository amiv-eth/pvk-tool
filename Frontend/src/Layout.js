// Basic Layout with sidebar
// Idea from https://mithril.js.org/simple-application.html
//
// Includes the generic login / logout

const m = require('mithril');
const { Session } = require('./api.js');

let nethz = '';
let password = '';
let error = '';

let busy = false;

function login() {
  if (!busy && nethz && password) {
    busy = true;
    Session.login(nethz, password).then(() => {
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
  Session.logout().then(() => {
    busy = false;
    error = '';
  }).catch((err) => {
    error = err._error.message;
    busy = false;
  });
}

const LoginPage = {
  view() {
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
  },
};


const SidebarHeader = {
  view() {
    return [
      m('h1', 'PVK Tool Demo'),
      m('p', `Hello, ${Session.user.name}`),
      m('button', { onclick: logout }, 'Logout'),
      Session.admin ? [
        m('br'),
        m('a', { href: '/course', oncreate: m.route.link }, 'User Tools'),
        m('br'),
        m('a', { href: '/admin', oncreate: m.route.link }, 'Admin Tools'),
      ] : [],
    ];
  },
};


module.exports = {
  view(vnode) {
    return Session.active() ? m('', [
      m('aside', [m(SidebarHeader), m(vnode.attrs.sidebar)]),
      m('main', m(vnode.attrs.content)),
    ]) : m(LoginPage);
  },
};
