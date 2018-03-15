/* eslint-disable no-param-reassign */

import m from 'mithril';

import { lectures } from './backend';

const currentCourse = {
  assistantList: ['Mathis', 'Sandro', 'Celina'],
  spots: '42',
  assistant: 'Mo',
  room: 'CAB E37',
  signup: {
    start: '',
    end: '',
  },
  datetimes: [{
    start: '2017-12-02T22:26',
    end: '',
  }],
};


function assistantList() {
  if (!currentCourse.lecture) { return []; }
  return lectures.list.find(({ _id }) =>
    _id === currentCourse.lecture).assistants;
}

function bind(obj, prop, type = 'text') {
  return {
    value: obj[prop],
    onchange(e) {
      obj[prop] = e.target.value;
    },
    type,
  };
}

class TimespanView {
  static view({ attrs: { timespan } }) {
    return [
      m('div', 'start: '),
      m(
        'input',
        bind(
          timespan,
          'start',
          'datetime-local',
        ),
        'start',
      ),
      m('div', 'end: '),
      m(
        'input',
        bind(
          timespan,
          'end',
          'datetime-local',
        ),
        'end',
      ),
    ];
  }
}


class chosenLecture {
  static view() {
    return [
      m(
        'select',
        {
          onchange: m.withAttr('selectedIndex', (index) => {
            currentCourse.lecture = lectures.list[index]._id;
          }),
        },
        lectures.list.map(lecture =>
          m('option', lecture.title)),
      ),
    ];
  }
}

class chosenAssistant {
  static view() {
    return [
      m('select', [
        assistantList().map(assistant => [
          m('option', assistant),
        ]),
      ]),
    ];
  }
}

class participantNumber {
  static view() {
    return [
      'How many Students may choose the Course? ',
      m('div'),
      m(
        'input',
        bind(currentCourse, 'spots', 'number'),
      ),
    ];
  }
}

class courseRoom {
  static view() {
    return [
      'What room will the course take place in? ',
      m('div'),
      m(
        'input',
        bind(currentCourse, 'room'),
      ),
    ];
  }
}

function addDatetime() {
  currentCourse.datetimes.push('');
}

function removeDatetime(index) {
  currentCourse.datetimes.splice(index, 1);
}


export default class CourseCreationView {
  static oninit() { lectures.get(); }

  static view() {
    return [
      m('div', 'As Admin, you can add Courses'),
      m('div', 'Choose Lecture'),
      m(chosenLecture),
      m('div', 'Choose Assistant'),
      m(chosenAssistant),
      m('div'),
      m(participantNumber),
      m('div'),
      m(courseRoom),
      m('div', 'What time does the course signup start and end?'),
      m('div'),
      m(TimespanView, { timespan: currentCourse.signup }),
      m('div', 'What time does the ourcse start and end?'),
      currentCourse.datetimes.map((timespan, index) => [
        m(TimespanView, { timespan }),
        m(
          'button',
          {
            onclick() {
              removeDatetime(index);
            },
          },
          'Remove course time',
        ),
        m('div'),
      ]),
      m(
        'button',
        { onclick: addDatetime },
        'Add other course time',
      ),
    ];
  }
}
