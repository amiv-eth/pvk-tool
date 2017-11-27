// User Sidebar
const m = require('mithril');
const { UserCourses } = require('./api.js');

function courseView(course) {
  return m('li', `${course.lecture.title}, ${course.assistant}`);
}

function asList(courses) { return courses.map(courseView); }

module.exports = {
  oninit() { UserCourses.load(); },

  view() {
    return [
      m('h1', 'Selected Courses'),
      UserCourses.selected.length ? [
        asList(UserCourses.selected),
        m('button', { onclick() { UserCourses.reserve(); } }, 'reserve'),
      ] : m('p', 'No courses selected.'),

      m('h1', 'Reserved Courses'),
      UserCourses.reserved.length ? [
        asList(UserCourses.reserved),
        m('button', { onclick() { UserCourses.pay(); } }, 'Pay'),
      ] : m('p', 'No courses reserved.'),

      m('h1', 'Accepted Courses'),
      UserCourses.accepted.length ? [
        asList(UserCourses.accepted),
      ] : m('p', 'No courses accepted.'),
    ];
  },
};
