/* eslint-disable no-param-reassign */

import { courses } from './backend';

export default function isExistentialCrisisHappening() {
  // check if the courses object from Backend contains requiered
  // department, year and dates Attributes
  return courses.list.map((singleCourse) => {
    if (singleCourse.lecture.department === undefined) { return singleCourse._id; }
    if (singleCourse.lecture.year === undefined) { return singleCourse._id; }
    return singleCourse.datetimes.map((timeslot) => {
      if (timeslot.start === undefined) { return singleCourse._id; }
      if (timeslot.end === undefined) { return singleCourse._id; }
      return 0;
    });
  }).filter(element => element === 0);
}
