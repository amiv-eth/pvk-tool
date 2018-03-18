// User Sidebar
import m from 'mithril';
import { userCourses, courses } from './backend';
import SidebarCard from './components/SidebarCard';


class CourseViewDeletable {
  static view({ attrs: { courseId, remove } }) {
    // Get Lecture of Course
    const course = courses.items[courseId];
    // Otherwise display loading
    if (course) {
      return m(SidebarCard, {
        title: course.lecture.title,
        subtitle: [course.assistant, ' - ', course.room],
        actionName: 'X',
        action: remove,
      });
    }
    return m(SidebarCard, {
      title: 'Loading ...',
    });
  }
}


class CourseView {
  static view({ attrs: { courseId } }) {
    // Same as deletable course view, but without action
    return m(CourseViewDeletable, { courseId });
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
              CourseViewDeletable,
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
            CourseViewDeletable,
            { _id, courseId, remove() { userCourses.free(_id); } },
          )),
      }),


      m(SidebarCard, {
        title: 'Reserved Courses',
        content: userCourses.reserved.length ? [
          userCourses.reserved.map(({ _id, course: courseId }) =>
            m(
              CourseViewDeletable,
              { _id, courseId, remove() { userCourses.free(_id); } },
            )),
        ] : 'No courses reserved.',
        action() { userCourses.pay(); },
        actionName: 'pay',
        actionActive: userCourses.reserved.length > 0,
      }),

      m(SidebarCard, {
        title: 'Accepted Courses',
        content: userCourses.accepted.length ? [
          userCourses.accepted.map(({ course: courseId }) =>
            m(
              CourseView,
              { courseId },
            )),
        ] : 'No courses accepted.',
      }),
    ];
  }
}
