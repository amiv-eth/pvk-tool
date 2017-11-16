/* eslint linebreak-style: ['error', 'windows'] */


const m = require('mithril');
const { Session } = require('./api.js');

const Layout = require('./Layout.js');
const UserSidebar = require('./UserSidebar.js');
const AdminSidebar = require('./AdminSidebar.js');
const CourseList = require('./CourseList.js');
const CourseOverview = require('./CourseOverview.js');


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
      if (!Session.admin) { m.route.set('/course'); }
      return m(Layout, {
        sidebar: AdminSidebar,
        content: CourseOverview,
      });
    },
  },
});
