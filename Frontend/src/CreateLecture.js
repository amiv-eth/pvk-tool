/* eslint-disable no-param-reassign */

const m = require('mithril');

const { lectures } = require('./backend.js');

const currentLecture = {
  title: 'Hallo',
  department: 'Alex',
  year: '42',
  assistant: ['rcelina', 'rstadler', 'troll'],
};

function addAssistant() {
  currentLecture.assistant.push('');
}

function removeAssistant(index) {
  currentLecture.assistant.splice(index, 1);
}

function bind(obj, prop) {
  return {
    value: obj[prop],
    onchange(e) {
      obj[prop] = e.target.value;
    },
  };
}

function createLecture() {
  lectures.post(currentLecture).then((response) => {
    console.log(response);
  }).catch((error) => {
    console.log(error);
  });
}

const enterField = {
  view() {
    return [
      m('div', 'Title: '),
      m('input', bind(currentLecture, 'title')),
      m('div', 'Department: '),
      m('input', bind(currentLecture, 'department')),
      m('div', 'Year: '),
      m('input', bind(currentLecture, 'year')),
      m('div', 'Assistant: '),
      currentLecture.assistant.map((_, index) => [
        m('div', [
          m(
            'input',
            bind(currentLecture.assistant, index),
          ),
          m(
            'button',
            {
              onclick() {
                removeAssistant(index);
              },
            },
            'Remove Assistant',
          ),
        ]),
      ]),
      m(
        'button',
        { onclick: addAssistant },
        'Add Assistant',
      ),
    ];
  },
};

const listLecture = {
  view() {
    return [
      m('div', 'Folgender Kurs wurde eingegeben:'),
      m('div'),
      `Coursetitle: ${currentLecture.title}`,
      m('div'),
      `Department: ${currentLecture.department}`,
      m('div'),
      `year: ${currentLecture.year}`,
    ];
  },
};


module.exports = {
  oninit() { lectures.get(); },
  view() {
    return [
      m('div', 'You are an admin. Niceooo!'),
      m('div', 'enter the following fields for the new Lecture'),
      m(enterField),
      m(listLecture),
      m('div'),
      m(
        'button',
        { onclick: createLecture },
        'Create Lecture',
      ),
      m('div', lectures.list.map(({ title }) =>
        m('div', title))),
    ];
  },
};
