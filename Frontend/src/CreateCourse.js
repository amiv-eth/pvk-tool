/* eslint-disable no-param-reassign */

const m = require('mithril');

const { lectures } = require('./backend.js');

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
  },
};

const chosenAssistant = {
  view() {
    return [
      m('select', [
        assistantList().map(assistant => [
          m('option', assistant),
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

function addDatetime() {
  currentCourse.datetimes.push('');
}

function removeDatetime(index) {
  currentCourse.datetimes.splice(index, 1);
}


module.exports = {
  oninit() { lectures.get(); },

  view() {
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
      m(timespanView, { timespan: currentCourse.signup }),
      m('div', 'What time does the ourcse start and end?'),
      currentCourse.datetimes.map((timespan, index) => [
        m(timespanView, { timespan }),
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
  },
};
