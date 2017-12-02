const m = require('mithril');
const session = require('./session.js');

const Layout = require('./Layout.js');
const UserSidebar = require('./UserSidebar.js');
const AdminSidebar = require('./AdminSidebar.js');
const CourseList = require('./CourseList.js');
const CourseOverview = require('./CourseOverview.js');
const CreateLecture = require('./CreateLecture.js');
const CreateCourse = require('./CreateCourse.js');

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
