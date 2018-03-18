/* eslint-disable no-param-reassign */

import { courses } from './backend';

function getCourseObject(courseId) {
  // returns course object for given courseId
  if (courses.items[courseId]) { return courses.items[courseId]; }
  return [];
}


export default function isOverlapping(sidebarCourseList, newCourse) {
  // Checks for each newCourse for a time overlapping with the sidebar Course List
  if (sidebarCourseList === undefined) { return 0; }
  let result = 0;
  sidebarCourseList.forEach((selectedCourse) => {
    getCourseObject(selectedCourse.course).datetimes.forEach((datetime) => {
      newCourse.datetimes.forEach((newDatetime) => {
        // check if start time of newCourse is between any course from sidebar Course List
        if (Date.parse(newDatetime.start) >= Date.parse(datetime.start)
            && Date.parse(newDatetime.start) <= Date.parse(datetime.end)) {
          result += 1;
        }
        // check if end time of newCourse is between any course from sidebar Course List
        if ((Date.parse(newDatetime.end) > Date.parse(datetime.start)
            && Date.parse(newDatetime.end) <= Date.parse(datetime.end))) {
          result += 1;
        }
        // check if newCourse contains any course from sidebar Course List
        if ((Date.parse(newDatetime.start) < Date.parse(datetime.start)
            && Date.parse(newDatetime.end) > Date.parse(datetime.end))) {
          result += 1;
        }
        // check if newCourse is contained by any course from sidebar Course List
        if ((Date.parse(newDatetime.start) > Date.parse(datetime.start)
            && Date.parse(newDatetime.end) < Date.parse(datetime.end))) {
          result += 1;
        }
      });
    });
  });
  return result;
}

