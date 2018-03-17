/* eslint-disable no-param-reassign */


import m from 'mithril';
import { courses, userCourses } from './backend';

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

class expandableContent {
  static view(vnode) {
    return [
      m(
        'button',
        { onclick() { vnode.state.expanded = !vnode.state.expanded; } },
        vnode.attrs.name,
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
      m(expandableContent, { name: year }, [
        getUniqueLecturesByYear(coursesFilteredByDepartment, year).map(lecture =>
          m(
            expandableContent,
            { name: lecture },
            displayCourses(coursesFilteredByDepartment
              .filter(course => course.lecture.year === year)
              .filter(course => course.lecture.title === lecture)),
          ))]));
  }
}
