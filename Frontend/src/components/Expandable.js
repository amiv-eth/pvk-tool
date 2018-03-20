/* eslint-disable no-param-reassign */

import m from 'mithril';

const icons = {
  // html arrows for expandable content
  ArrowRight: '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M8.59 16.34l4.58-4.59-4.58-4.59L10 5.75l6 6-6 6z"/><path d="M0-.25h24v24H0z" fill="none"/></svg>',
  ArrowDown: '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M7.41 7.84L12 12.42l4.59-4.58L18 9.25l-6 6-6-6z"/><path d="M0-.75h24v24H0z" fill="none"/></svg>',
};

export default class expandableContent {
  // return object with state.expanded, state.level and state.name
  static view(vnode) {
    return [
      m(
        'div',
        {
          onclick() {
            vnode.state.expanded = !vnode.state.expanded;
          },
        },
        m(
          `h${vnode.attrs.level + 1}`,
          [vnode.state.expanded ? m.trust(icons.ArrowDown) : m.trust(icons.ArrowRight),
            vnode.attrs.name],
        ),
      ),
      vnode.state.expanded ? vnode.children : [],
    ];
  }
}
