import PvkList from './PvkList';

const m = require('mithril');

module.exports = {
  view() {
    return m('div', [m(PvkList)]);
  },
};
