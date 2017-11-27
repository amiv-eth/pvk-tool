import m from 'mithril';

class Pvk {
  constructor() {
    this.list = [];
  }

  loadlist() {
    // todo: this is just a mock request and has to be replaced with the proper one
    // request is needed to force mithrijs to update shared objects
    m.request({
      method: 'GET',
      // url: `${apiUrl}`,
    }).then(() => {
      this.list = [{
        lecture: {
          title: 'lecture1',
          department: 'depart1',
          year: 17,
        },
        assistant: {
          nethz: 'nethzmail',
          name: 'assi name',
        },
        datetimes: [{
          start: '2017-10-15T16:15:20Z',
          end: '2017-10-16T16:15:20Z',
        }],
        spots: 15,
        selected: true,
        reserved: true,
        payed: true,
      }, {
        lecture: {
          title: 'lecture1',
          department: 'depart1',
          year: 17,
        },
        assistant: {
          nethz: 'nethzmail',
          name: 'assi name',
        },
        datetimes: [{
          start: '2017-10-15T16:15:20Z',
          end: '2017-10-16T16:15:20Z',
        }],
        spots: 15,
        selected: false,
        reserved: false,
        payed: false,
      }];
    });
  }
}

export default new Pvk();
