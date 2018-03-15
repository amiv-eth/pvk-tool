import m from 'mithril';

import session from './session';

import Layout from './Layout';
import UserSidebar from './UserSidebar';
import AdminSidebar from './AdminSidebar';
import CourseList from './CourseList';
import CourseOverview from './CourseOverview';
import CreateLecture from './CreateLecture';
import CreateCourse from './CreateCourse';

m.route(document.body, '/courses', {
  '/courses': {
    render() {
      return m(Layout, {
        sidebar: UserSidebar,
        content: CourseList,
      });
    },
  },
  '/admin': {
    render() {
      // If not admin, redirect to Courses
      if (!session.admin) { m.route.set('/course'); }
      return m(Layout, {
        sidebar: AdminSidebar,
        content: CourseOverview,
      });
    },
  },
  '/new-lecture': {
    render() {
      // If not admin, redirect to Courses
      if (!session.admin) { m.route.set('/course'); }
      return m(Layout, {
        sidebar: AdminSidebar,
        content: CreateLecture,
      });
    },
  },
  '/new-course': {
    render() {
      // If not admin, redirect to Courses
      if (!session.admin) { m.route.set('/course'); }
      return m(Layout, {
        sidebar: AdminSidebar,
        content: CreateCourse,
      });
    },
  },
});
