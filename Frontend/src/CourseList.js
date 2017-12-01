const m = require('mithril');
const { Courses } = require('./api.js');

module.exports = {
  oninit() { Courses.load(); },

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
      m('tbody', Courses.list.map(course =>
        m('tr', [
          m('td', course.lecture.title),
          m('td', course.lecture.department),
          m('td', course.assistant.name),
          course.datetimes.map(timeslot => [
            m('td', timeslot.start),
            m('td', timeslot.end),
          ]),
          m('td', m('button', 'add course')),
        ]))),
    ]);
  },
};
