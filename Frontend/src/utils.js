/* eslint-disable no-param-reassign */

import { courses } from './backend';

function getCourseObject(courseId) {
  // returns course object for given courseId
  if (courses.items[courseId]) { return courses.items[courseId]; }
  return [];
}


export default function isOverlapping(courseList, course) {
  // Checks for each course for a time overlapping with the sidebar Course List
  if (courseList === undefined) { return 0; }
  let result = 0;
  courseList.forEach((selectedCourse) => {
    getCourseObject(selectedCourse.course).datetimes.forEach((datetime) => {
      course.datetimes.forEach((newDatetime) => {
        /*
        // check if start time of course is between any course from sidebar Course List
        if (Date.parse(newDatetime.start) >= Date.parse(datetime.start)
            && Date.parse(newDatetime.start) <= Date.parse(datetime.end)) {
          result += 1;
        }
        // check if end time of course is between any course from sidebar Course List
        if ((Date.parse(newDatetime.end) > Date.parse(datetime.start)
            && Date.parse(newDatetime.end) <= Date.parse(datetime.end))) {
          result += 1;
        }
        // check if course contains any course from sidebar Course List
        if ((Date.parse(newDatetime.start) < Date.parse(datetime.start)
            && Date.parse(newDatetime.end) > Date.parse(datetime.end))) {
          result += 1;
        }
        // check if course is contained by any course from sidebar Course List
        if ((Date.parse(newDatetime.start) > Date.parse(datetime.start)
            && Date.parse(newDatetime.end) < Date.parse(datetime.end))) {
          result += 1; */
        // New solution:----------------------------------
        // Either newDatetime is strictly bevore datetime
        // or the oppposite must be true, so that the times do not overlapp
        if ((Date.parse(newDatetime.start) >= Date.parse(datetime.end)
            || Date.parse(datetime.start) >= Date.parse(newDatetime.end)) === false) {
          result += 1;
        }
      });
    });
  });
  return result;
}

export function dateFormatterStart(datestring) {
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

export function dateFormatterEnd(datestring) {
  // converts an API datestring into the standard format 10:21
  if (!datestring) return '';
  const date = new Date(datestring);
  return date.toLocaleString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  });
}
