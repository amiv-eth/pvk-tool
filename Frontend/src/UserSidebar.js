// User Sidebar
const m = require('mithril');
const { userCourses } = require('./api.js');

function courseView(course) {
  return m('li', course);
}

function asList(courses) { return courses.map(courseView); }

module.exports = {
  oninit() { userCourses.get(); },

  view() {
    return [
      m('h1', 'Selected Courses'),
      userCourses.selected.length ? [
        userCourses.selected.map(selId =>
          m('li', [
            m('span', selId),
            m(
              'button',
              {
                onclick() { userCourses.deselectCourse(selId); },
                disabled: userCourses.resources.selections.isBusy(),
              },
              'X',
            ),
          ])),
        m('button', { onclick() { userCourses.reserve(); } }, 'reserve'),
      ] : m('p', 'No courses selected.'),

      m('h1', 'Reserved Courses'),
      userCourses.reserved.length ? [
        asList(userCourses.reserved),
        m('button', { onclick() { userCourses.pay(); } }, 'Pay'),
      ] : m('p', 'No courses reserved.'),

      m('h1', 'Accepted Courses'),
      userCourses.accepted.length ? [
        asList(userCourses.accepted),
      ] : m('p', 'No courses accepted.'),
    ];
  },
};
