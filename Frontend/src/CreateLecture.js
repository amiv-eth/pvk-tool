/* eslint-disable no-param-reassign */

import m from 'mithril';

import { lectures } from './backend';

const currentLecture = {
  title: 'Hallo',
  department: 'itet',
  year: '2',
  assistants: ['rcelina', 'rstadler', 'troll'],
};

function addAssistants() {
  currentLecture.assistants.push('');
}

function removeAssistants(index) {
  currentLecture.assistants.splice(index, 1);
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

class Form {
  static view() {
    return [
      m('div', 'Title: '),
      m('input', bind(currentLecture, 'title')),
      m('div', 'Department: '),
      m('input', bind(currentLecture, 'department')),
      m('div', 'Year: '),
      m('input', bind(currentLecture, 'year')),
      m('div', 'Assistants: '),
      currentLecture.assistants.map((_, index) => [
        m('div', [
          m(
            'input',
            bind(currentLecture.assistants, index),
          ),
          m(
            'button',
            {
              onclick() {
                removeAssistants(index);
              },
            },
            'Remove Assistants',
          ),
        ]),
      ]),
      m(
        'button',
        { onclick: addAssistants },
        'Add Assistants',
      ),
    ];
  }
}

class LectureList {
  static view() {
    return [
      m('div', 'Folgender Kurs wurde eingegeben:'),
      m('div'),
      `Coursetitle: ${currentLecture.title}`,
      m('div'),
      `Department: ${currentLecture.department}`,
      m('div'),
      `year: ${currentLecture.year}`,
    ];
  }
}


export default class LectureCreationView {
  static oninit() { lectures.get(); }
  static view() {
    return [
      m('div', 'You are an admin. Niceooo!'),
      m('div', 'enter the following fields for the new Lecture'),
      m(Form),
      m(LectureList),
      m('div'),
      m(
        'button',
        { onclick: createLecture },
        'Create Lecture',
      ),
      m('div', lectures.list.map(({ title, _id }) => [
        m(
          'div',
          title,
          m(
            'button',
            { onclick() { lectures.deleteItem(_id); } },
            'Delete',
          ),
        ),
      ])),
    ];
  }
}
