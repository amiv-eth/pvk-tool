/* eslint linebreak-style: ['error', 'windows'] */
import m from 'mithril';

import Pvk from './Pvk';

class PvkList {
  oninit() {
    this.m = m;
    Pvk.loadlist();
    m.redraw();
  }
  view() {
    return this.m(
      '.pvk-list',
      this.m(
        'table',
        m(
          'thead',
          m(
            'tr',
            m('th', 'Course'),
            m('th', 'Department'),
            m('th', 'Name'),
            m('th', 'Starting time'),
            m('th', 'Ending time'),
          ),
        ),
        m(
          'tbody',
          Pvk.list.map(pvk => m(
            'tr.pvk-list-item',
            m('td.pvk-list-item-title', pvk.lecture.title),
            m('td.pvk-list-item-department', pvk.lecture.department),
            m('td.pvk-list-item-assistant-name', pvk.assistant.name),
            pvk.datetimes.map(timeslot => [m('td.pvk-list-item-timeslot', timeslot.start),
              m('td.pvk-list-item-timeslot', timeslot.end)]),
            m(
              'td.pvk-list-btn ',
              m('button', 'add course'),
            ),
          )),
        ),
      ),
    );
  }
}

export default new PvkList();
