import PvkList from './PvkList';

const m = require('mithril');
const { Courses, UserCourses } = require('./api.js');

module.exports = {
  oninit() { Courses.load(); },

  view() {
<<<<<<< HEAD
    return m('div', [m(PvkList)]);
=======
    // return m('div', 'Hellooo!');
    return m('ul', [
      Courses.list.map(course =>
        m('li', [
          m('p', `${course.lecture.title}, ${course.assistant}`),
          m(
            'button',
            { onclick() { UserCourses.select(course); } },
            'Add Course',
          ),
        ])),
    ]);
    // m('button', { onclick() { Courses.select(); } }, 'Add Course');
>>>>>>> Frontend: Talk to backend and display courses in sidebar
  },
};
