// User Sidebar
import m from 'mithril';
import { userCourses, courses } from './backend';

class CourseView {
  static view({ attrs: { _id, courseId, remove } }) {
    // Get Lecture of Course
    const course = courses.list.find(item => item._id === courseId);
    // Otherwise display loading
    return m('li', [
      m('span', course ? course.lecture.title : 'Loading...'),
      // If there is no id, the element is not yet created,
      // so a delete button does not make any sense
      m('button', { onclick: remove, disabled: !_id }, 'X'),
    ]);
  }
}


export default class UserSidebar {
  static oninit() { userCourses.get(); }

  static view() {
    return [
      m('h1', 'Selected Courses'),
      userCourses.selected.length ? [
        userCourses.selected.map(({ _id, course: courseId }) =>
          m(
            CourseView,
            { _id, courseId, remove() { userCourses.deselect(_id); } },
          )),
        m('button', { onclick() { userCourses.reserve(); } }, 'reserve'),
      ] : m('p', 'No courses selected.'),

      m('h1', 'Reserved Courses'),
      userCourses.reserved.length ? [
        userCourses.reserved.map(({ _id, course: courseId }) =>
          m(
            CourseView,
            { _id, courseId, remove() { userCourses.free(_id); } },
          )),
        // m('button', { onclick() { userCourses.pay(); } }, 'Pay'),
      ] : m('p', 'No courses reserved.'),
      userCourses.waiting.length ? [
        m('h4', 'Waiting'),
        userCourses.waiting.map(({ _id, course: courseId }) =>
          m(
            CourseView,
            { _id, courseId, remove() { userCourses.free(_id); } },
          )),
      ] : [],
      m('h1', 'Accepted Courses'),
      m('p', 'No courses accepted.'), // TODO: Implement
    ];
  }
}
