/* eslint-disable no-param-reassign */


import m from 'mithril';
import { courses, userCourses } from './backend';
import SidebarCard from './components/SidebarCard';
import isOverlapping from './timeOverlap';

function isSelectedOrReserved(course) {
  return userCourses.selected.some(sel => sel.course === course._id) ||
    userCourses.signups.some(signup => signup.course === course._id);
}

function displayCourses(coursesList) {
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
    m('tbody', coursesList.map(course =>
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
            },
            'add course',
          ),
        ),
      ]))),
  ]);
}


export const icons = {
  ArrowRight: '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M8.59 16.34l4.58-4.59-4.58-4.59L10 5.75l6 6-6 6z"/><path d="M0-.25h24v24H0z" fill="none"/></svg>',
  ArrowDown: '<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M7.41 7.84L12 12.42l4.59-4.58L18 9.25l-6 6-6-6z"/><path d="M0-.75h24v24H0z" fill="none"/></svg>',
};

// Choose itet oder mavt
const selectedDepartment = 'mavt';

function coursesByDeparment(coursesList, department) {
  return coursesList.filter(c => Boolean(c.lecture)).filter(course =>
    course.lecture.department === department);
}

function onlyUnique(value, index, self) {
  return self.indexOf(value) === index;
}

function getUniqueYears(courseList) {
  return courseList.map(course => course.lecture.year).sort().filter(onlyUnique);
}

function getUniqueLecturesByYear(courseList, year) {
  return courseList
    .filter(course => course.lecture.year === year)
    .map(course => course.lecture.title)
    .sort()
    .filter(onlyUnique);
}


function dateFormatterStart(datestring) {
  // converts an API datestring into the standard format Mon 30/01/1990, 10:21
  if (!datestring) return '';
  const date = new Date(datestring);
  return date.toLocaleString('en-GB', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function dateFormatterEnd(datestring) {
  // converts an API datestring into the standard format 10:21
  if (!datestring) return '';
  const date = new Date(datestring);
  return date.toLocaleString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function displayCard(course) {
  const attributes = {
    title: `Assistant: ${course.assistant}`,
    subtitle: `Room: ${course.room}`,
    content:
      m('ul', course.datetimes.map(timeslot =>
        m('li', [dateFormatterStart(timeslot.start), '  - ',
          dateFormatterEnd(timeslot.end)]))),
  };
  if (!isOverlapping(userCourses.selected, course)) {
    attributes.action = () => {
      userCourses.select(course._id);
    };
    attributes.actionName = 'Add';
  }
  return m(SidebarCard, attributes);
}


class expandableContent {
  static view(vnode) {
    return [
      m(
        'div',
        {
          onclick() {
            vnode.state.expanded = !vnode.state.expanded;
          },
        },
        m(
          `h${vnode.attrs.level + 1}`,
          [vnode.state.expanded ? m.trust(icons.ArrowDown) : m.trust(icons.ArrowRight),
            vnode.attrs.name],
        ),
      ),
      vnode.state.expanded ? vnode.children : [],
    ];
  }
}

export default class CourseList {
  static oninit() {
    courses.getAll();
  }

  static view() {
    const coursesFilteredByDepartment = coursesByDeparment(courses.list, selectedDepartment);
    return getUniqueYears(coursesFilteredByDepartment).map(year =>
      m(expandableContent, { name: `Year ${year}`, level: 0 }, [
        getUniqueLecturesByYear(coursesFilteredByDepartment, year).map(lecture =>
          m(
            expandableContent,
            { name: lecture, level: 1 },
            coursesFilteredByDepartment
              .filter(course => course.lecture.year === year)
              .filter(course => course.lecture.title === lecture).map(displayCard),
          ))]));
  }
}
