const m = require('mithril');
const { courses, userCourses } = require('./backend.js');

function isSelectedOrReserved(course) {
  return userCourses.selected.some(sel => sel.course === course._id) ||
    userCourses.signups.some(signup => signup.course === course._id);
}

module.exports = {
  oninit() { courses.get().then((d) => { console.log(d); }); },

  view() {
    return m('table', [
      m('thead', [
        m('tr', [
          m('th', 'Course'),
          m('th', 'Department'),
          m('th', 'Name'),
          m('th', 'Spots'),
          m('th', 'Signup Start'),
          m('th', 'Signup End'),
          m('th', 'Starting time'),
          m('th', 'Ending time'),
        ]),
      ]),
      m('tbody', courses.list.map(course =>
        m('tr', [
          m('td', course.lecture.title),
          m('td', course.lecture.department),
          m('td', course.assistant),
          m('td', course.spots),
          m('td', course.signup.start),
          m('td', course.signup.end),
          course.datetimes.map(timeslot => [
            m('td', timeslot.start),
            m('td', timeslot.end),
          ]),
          m(
            'td',
            m(
              'button',
              {
                onclick() { userCourses.select(course._id); },
                disabled: isSelectedOrReserved(course),
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
