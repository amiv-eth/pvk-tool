/* eslint-disable no-param-reassign */

import m from 'mithril';
import { courses, userCourses } from './backend';

export default function isOverlapping(selectedCourseList, newCourse) {
  if (selectedCourseList === undefined) { return 0; }
  const currentStartTime = newCourse.datetimes.start;
  const currentEndTime = newCourse.datetimes.end;
  let result = 0;
  selectedCourseList.forEach(selectedCourse => {
    console.log(selectedCourse);
    selectedCourse.datetimes.forEach((datetime) => {
      if (((currentStartTime > datetime.start && currentStartTime < datetime.end)
           || (currentEndTime > datetime.start && currentEndTime < datetime.end))) {
        result += 1;
      }
    })});
  return result;
}
