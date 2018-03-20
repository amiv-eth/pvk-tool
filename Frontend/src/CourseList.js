/* eslint-disable no-param-reassign */


import m from 'mithril';
import { courses, userCourses } from './backend';
import SidebarCard from './components/SidebarCard';
// import isOverlapping from './timeOverlap';
import {
  getCourseObject,
  dateFormatterStart,
  dateFormatterEnd,
  isOverlappingTime,
} from './utils';
import expandableContent from './components/Expandable';
// To test the existence of data
// import isExistentialCrisisHappening from './Testing';


// choose itet oder mavt
const selectedDepartment = 'mavt';

function coursesByDeparment(coursesList, department) {
  // returns list of filtered courseList by department
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
  // return list of unique lecutres for given year
  return courseList
    .filter(course => course.lecture.year === year)
    .map(course => course.lecture.title)
    .sort()
    .filter(onlyUnique);
}


function displayCard(course) {
  // returns SidebarCard for given course
  const attributes = {
    title: `Assistant: ${course.assistant}`,
    subtitle: `Room: ${course.room}`,
    content:
      m('ul', course.datetimes.map(timeslot =>
        m('li', [dateFormatterStart(timeslot.start), '  - ',
          dateFormatterEnd(timeslot.end)]))),
  };

  // counter for the amount of overlap between the selected course
  // and the course, that will be drawn
  let numberOfOverlap = 0;
  // get lists for selected courses, waiting courses and reserverd courses
  const chosenUserCourses = userCourses.selected;
  userCourses.waiting.forEach(element => chosenUserCourses.push(element));
  userCourses.reserved.forEach(element => chosenUserCourses.push(element));
  // get the start and end timess for eaech course and then test the overlap
  if (chosenUserCourses.length !== 0) {
    chosenUserCourses.forEach((selectedCourse) => {
      getCourseObject(selectedCourse.course).datetimes.forEach((datetime1) => {
        course.datetimes.forEach((datetime2) => {
          numberOfOverlap += isOverlappingTime(datetime1, datetime2);
        });
      });
    });
  }
  // allows adding course to selected courses, if no time collision
  if (numberOfOverlap === 0) {
    attributes.action = () => {
      userCourses.select(course._id);
    };
    attributes.actionName = 'Add';
  } else {
    attributes.actionActive = false;
    attributes.actounName = 'Time conflict';
    attributes.content = [m('ul', course.datetimes.map(timeslot =>
      m('li', [dateFormatterStart(timeslot.start), '  - ',
        dateFormatterEnd(timeslot.end)]))), m('p', 'Time Conflict!')];
  }
  return m(SidebarCard, attributes);
}


export default class CourseList {
  // get courses on initiating webpage
  static oninit() {
    courses.getAll();
  }

  // draw the SidebarCard sorted  year and lecture.name filtered by department
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
