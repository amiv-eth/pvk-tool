/* eslint-disable no-param-reassign */


import m from 'mithril';
import { courses, userCourses } from './backend';
import SidebarCard from './components/SidebarCard';
import { dateFormatter, isOverlappingTime } from './utils';
import expandableContent from './components/Expandable';

// choose itet oder mavt
const selectedDepartment = 'mavt';

function getCoursesByDepartment(coursesList, department) {
  return coursesList
    .filter(course => Boolean(course.lecture))
    .filter(course => course.lecture.department === department);
}

function onlyUnique(value, index, self) {
  // Trick: indexOf returns the index of the first occurence of `value`
  //        so the following returns true only for the first item
  return self.indexOf(value) === index;
}

function getUniqueYears(courseList) {
  return courseList
    .map(course => course.lecture.year)
    .filter(onlyUnique);
}

function getUniqueLecturesByYear(courseList, year) {
  return courseList
    .filter(course => course.lecture.year === year)
    .map(course => course.lecture.title)
    .filter(onlyUnique);
}


function displayCard(course) {
  // Get all currently selected courses
  const selectedCourses = userCourses.all.map(selection =>
    courses.items[selection.course]).filter(Boolean);

  // Check if this course is already selected
  const selected = selectedCourses.map(c => c._id).indexOf(course._id) !== -1;

  // Find all other courses with time overlap (if any)
  const overlappingCourses = selectedCourses.filter((otherCourse) => {
    let overlap = false;
    if (course.datetimes && otherCourse && otherCourse.datetimes) {
      course.datetimes.forEach((datetime1) => {
        otherCourse.datetimes.forEach((datetime2) => {
          if (isOverlappingTime(datetime1, datetime2)) { overlap = true; }
        });
      });
    }
    return overlap;
  });
  // For prettier output: List of lectures for which courses overlap
  const overlappingLectures = overlappingCourses
    .map(c => c.lecture.title)
    .filter(onlyUnique)
    .join(', ');

  return m(SidebarCard, {
    // Title and content
    title: `Assistant: ${course.assistant}`,
    subtitle: `Room: ${course.room}`,
    content: [
      m('ul', course.datetimes.map(timeslot =>
        m('li', dateFormatter(timeslot)))),
      // If course is not selected already, show potential timing conflicts
      !selected && overlappingCourses.length !== 0 ? [
        m('p', [
          'Time conflict with your courses for the following lectures: ',
          overlappingLectures,
        ]),
      ] : [],
    ],

    // Action
    actionName: selected ? 'Already selected' : 'Select',
    actionActive: !selected && (overlappingCourses.length === 0),
    action() { userCourses.select(course._id); },
  });
}

export default class CourseList {
  // get courses on initiating webpage
  static oninit() {
    courses.getAll();
  }

  // draw the SidebarCard sorted  year and lecture.name filtered by department
  static view() {
    const coursesByDepartment = getCoursesByDepartment(
      courses.list,
      selectedDepartment,
    );
    return getUniqueYears(coursesByDepartment).map(year =>
      m(expandableContent, { name: `Year ${year}`, level: 0 }, [
        getUniqueLecturesByYear(
          coursesByDepartment,
          year,
        ).map(lecture =>
          m(
            expandableContent,
            { name: lecture, level: 1 },
            coursesByDepartment
              .filter(course => course.lecture.year === year)
              .filter(course => course.lecture.title === lecture)
              .map(displayCard),
          ))]));
  }
}
