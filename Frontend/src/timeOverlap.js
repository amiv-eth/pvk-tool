/* eslint-disable no-param-reassign */

import m from 'mithril';
// import { courses, userCourses } from './backend';
import { courses } from './backend';

function getCourseObject(courseId) {
  if (courses.items[courseId]) { return courses.items[courseId]; }
  return [];
}


export default function isOverlapping(selectedCourseList, newCourse) {
  // console.log(selectedCourseList);
  if (selectedCourseList === undefined) { return 0; }
  let result = 0;
  selectedCourseList.forEach((selectedCourse) => {
    // console.log(getCourseObject(selectedCourse.course));
    getCourseObject(selectedCourse.course).datetimes.forEach((datetime) => {
      newCourse.datetimes.forEach((newDatetime) => {
        // console.log(Date.parse(newDatetime.start));
        if (((Date.parse(newDatetime.start) > Date.parse(datetime.start)
            && Date.parse(newDatetime.start) < Date.parse(datetime.end))
            || (Date.parse(newDatetime.end) > Date.parse(datetime.start)
            && Date.parse(newDatetime.end) < Date.parse(datetime.end)))) {
          result += 1;
        }
      });
    });
  });
  console.log(result);
  return result;
}
