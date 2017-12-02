const m = require('mithril');
const { courses, userCourses } = require('./backend.js');

function isSelected(course) {
  return userCourses.selected.some(sel => sel === course._id);
}

function isBusy() { return userCourses.resources.selections.isBusy(); }

module.exports = {
  oninit() { courses.get(); },

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
      m('tbody', courses.list.map(course =>
        m('tr', [
          m('td', course.lecture.title),
          m('td', course.lecture.department),
          m('td', course.assistant),
          course.datetimes.map(timeslot => [
            m('td', timeslot.start),
            m('td', timeslot.end),
          ]),
          m(
            'td',
            m(
              'button',
              {
                onclick() { userCourses.selectCourse(course._id); },
                disabled: isSelected(course) || isBusy(),
                //   ?
                //  true : false,
                //  return false;
                //  return !((UserCourses.selected.courses || []).some(sel =>
                //    sel === course._id));
                // },
              },
              'add course',
            ),
          ),
        ]))),
    ]);
  },
};
