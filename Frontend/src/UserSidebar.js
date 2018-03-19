// User Sidebar
import m from 'mithril';
import { userCourses, courses } from './backend';
import SidebarCard from './components/SidebarCard';


class CourseView {
  static view({ attrs: { _id, courseId, remove } }) {
    // Get Lecture of Course
    const course = courses.items[courseId];
    // Otherwise display loading
    if (course) {
      return m(SidebarCard, {
        title: course.lecture.title,
        subtitle: [course.assistant, ' - ', course.room],
        actionName: 'X',
        action() { remove(); },
      });
    }
    return m(SidebarCard, {
      title: 'Loading ...',
    });
    /*m('li', [
      m('span', course ? course.lecture.title : 'Loading...'),
      // If there is no id, the element is not yet created,
      // so a delete button does not make any sense
      m('button', { onclick: remove, disabled: !_id }, 'X'),
    ]); */
  }
}


export default class UserSidebar {
  static oninit() { userCourses.get(); }

  static view() {
    return [
      m(SidebarCard, {
        title: 'Selected Courses',
        content: userCourses.selected.length ? [
          userCourses.selected.map(({ _id, course: courseId }) =>
            m(
              CourseView,
              { _id, courseId, remove() { userCourses.deselect(_id); } },
            )),
        ] : 'No courses selected.',
        action() { userCourses.reserve(); },
        actionName: 'reserve',
      }),

      m(SidebarCard, {
        title: 'Waiting List',
        content: userCourses.waiting.map(({ _id, course: courseId }) =>
          m(
            CourseView,
            { _id, courseId, remove() { userCourses.free(_id); } },
          )),
      }),


      m(SidebarCard, {
        title: 'Reserved Courses',
        content: userCourses.reserved.length ? [
          userCourses.reserved.map(({ _id, course: courseId }) =>
            m(
              CourseView,
              { _id, courseId, remove() { userCourses.free(_id); } },
            )),
        ] : 'No courses reserved.',
        action() { userCourses.pay(); },
        actionName: 'pay',
      }),

      m(SidebarCard, {
        title: 'Accepted Courses',
        content: 'No courses accepted.',
      }),
    ];
  }
}
