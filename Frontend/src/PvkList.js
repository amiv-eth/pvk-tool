import m from 'mithril';

import Pvk from './Pvk';

module.exports = {
  oninit() {
    Pvk.loadlist();
    m.redraw();
  },
  view() {
    return m('table', [
      m('thead', [
        m('tr', [
          m('th', 'Course'),
          m('th', 'Department'),
          m('th', 'Name'),
          m('th', 'Starting time'),
          m('th', 'Ending time'),
        ]),
      ]),
      m('tbody', Pvk.list.map(pvk =>
        m('tr', [
          m('td', pvk.lecture.title),
          m('td', pvk.lecture.department),
          m('td', pvk.assistant.name),
          pvk.datetimes.map(timeslot => [
            m('td', timeslot.start),
            m('td', timeslot.end),
          ]),
          m('td', m('button', 'add course')),
        ]))),
    ]);
  },
};
