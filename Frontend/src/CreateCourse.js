/* eslint-disable no-param-reassign */

const m = require('mithril');

const currentCourse = {
  courseList: ['Hermann', 'Alex', 'Eppi'],
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


function bind(obj, prop, type = 'text') {
  return {
    value: obj[prop],
    onchange(e) {
      obj[prop] = e.target.value;
    },
    type,
  };
}

const timespanView = {
  view({ attrs: { timespan } }) {
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
  },
};


const chosenLecture = {
  view() {
    return [
      m('select', [
        currentCourse.courseList.map((_, index) => [
          m('option', currentCourse.courseList[index]),
        ]),
      ]),
    ];
  },
};

const chosenAssistant = {
  view() {
    return [
      m('select', [
        currentCourse.assistantList.map((_, index) => [
          m('option', currentCourse.assistantList[index]),
        ]),
      ]),
    ];
  },
};

const participantNumber = {
  view() {
    return [
      'How many Students may choose the Course? ',
      m('div'),
      m(
        'input',
        bind(currentCourse, 'spots', 'number'),
      ),
    ];
  },
};

const courseRoom = {
  view() {
    return [
      'What room will the course take place in? ',
      m('div'),
      m(
        'input',
        bind(currentCourse, 'room'),
      ),
    ];
  },
};


module.exports = {
  view() {
    return [
      m('div', 'As Admin, you can add Courses'),
      m('div', 'Choose Course'),
      m(chosenLecture),
      m('div', 'Choose Assistant'),
      m(chosenAssistant),
      m('div'),
      m(participantNumber),
      m('div'),
      m(courseRoom),
      m('div', 'What time does the course signup start and end?'),
      m('div'),
      m(timespanView, { timespan: currentCourse.signup }),
      m('div', 'What time does the course start and end?'),
      currentCourse.datetimes.map(timespan =>
        m(timespanView, { timespan })),
    ];
  },
};
