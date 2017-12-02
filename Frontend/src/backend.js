// Api calls

const m = require('mithril');
const session = require('./session.js');


const pvkApiUrl = `//${window.location.hostname}/api`;


// Helper to filter temp out of list
function withoutTemp(list, temp) { return list.filter(item => item !== temp); }


// Request to the PVK backend
function request({
  resource,
  method = 'GET',
  id = '',
  data = {},
  query = {},
  headers = {},
}) {
  // Parse query such that the backend understands it
  const parsedQuery = {};
  Object.keys(query).forEach((key) => {
    parsedQuery[key] = JSON.stringify(query[key]);
  });
  const queryString = m.buildQueryString(parsedQuery);

  const allHeaders = Object.assign(
    {},
    { Authorization: `Token ${session.data.token}` },
    headers,
  );

  // Send the request
  return m.request({
    method,
    data,
    url: `${pvkApiUrl}/${resource}/${id}?${queryString}`,
    headers: allHeaders,
  }).catch((err) => {
    // If the error is 401, the token is invalid -> auto log out
    if (err._error.code === 401) { session.clear(); }

    // Pass on Error
    throw err;
  });
}


// Generic PVK resource
class Resource {
  constructor(name, query = {}) {
    this.name = name;
    this.query = query;

    // List for items confirmend by api
    this._items = {};

    // Temporary objects to react instantly to requests
    this._items_new = [];
    this._items_updated = {};
    this._items_deleted = [];
  }

  isBusy() {
    return Object.keys(this._items_updated).length !== 0 ||
      this._items_deleted.length !== 0;
  }

  get list() {
    const currentItems = Object.keys(this._items)
      .filter(key => this._items_deleted.indexOf(key) === -1)
      .map(key => this._items_updated[key] || this._items[key]);
    return [...currentItems, ...this._items_new];
  }

  get() {
    return request({
      resource: this.name,
      query: this.query,
    }).then((data) => {
      // Fill own list
      this._items = {};
      data._items.forEach((item) => { this._items[item._id] = item; });
      // Pass on data
      return data;
    });
  }

  getItem(id) {
    return request({
      resource: this.name,
      id,
      query: this.query,
    }).then((data) => {
      // Fill own list
      this._items[data._id] = data;
      // Pass on data
      return data;
    });
  }

  post(data) {
    // Add data already to list of unprocessed items
    this._items_new.push(data);

    // Send request, remove temporary object as soon as response arrives
    return request({
      resource: this.name,
      method: 'POST',
      data,
    }).then((confirmedData) => {
      // Success!
      this._items_new = withoutTemp(this._items_new, data);
      this._items[confirmedData._id] = confirmedData;
      return confirmedData;
    }).catch((err) => {
      this._items_new = withoutTemp(this._items_new, data);
      throw err;
    });
  }

  patchItem(id, changes) {
    // Add changes to temporary storage
    this._items_updated[id] = Object.assign(
      {},
      this._items[id],
      changes,
    );

    // Send request, remove temporary object as soon as response arrives
    return request({
      resource: this.name,
      id,
      method: 'PATCH',
      headers: { 'If-Match': this._items[id]._etag },
      data: changes,
    }).then((confirmedData) => {
      // Remove item
      this._items[id] = confirmedData;
      delete this._items_updated[id];
    }).catch((err) => {
      // If 412: Data is outdated, reload!
      if (err._error.code === 412) { this.get(); }

      delete this._items_updated[id];
      throw err;
    });
  }

  deleteItem(id) {
    // Set item id on deleted-list
    this._items_deleted.push(id);

    // Send request, remove temporary object as soon as response arrives
    return request({
      resource: this.name,
      id,
      method: 'DELETE',
      headers: { 'If-Match': this._items[id]._etag },
    }).then((result) => {
      // Remove item
      delete this._items[id];
      this._items_deleted = withoutTemp(this._items_deleted, id);
      return result;
    }).catch((err) => {
      // If 412: Data is outdated, reload!
      if (err._error.code === 412) { this.get(); }

      this._items_deleted = withoutTemp(this._items_deleted, id);
      throw err;
    });
  }
}

const userCourses = {

  resources: {
    selections: new Resource(
      'selections',
      { where: { nethz: session.user.nethz } },
    ),
    signups: new Resource(
      'signups',
      { where: { nethz: session.user.nethz } },
    ),
  },

  get() {
    this.resources.selections.get();
    this.resources.signups.get();
  },

  get selected() {
    // We are only interested in the first (only) item
    const sel = this.resources.selections.list[0];
    return sel ? sel.courses : [];
  },
  get reserved() {
    return this.resources.signups.list.filter(({ status }) =>
      status === 'reserved');
  },
  get accepted() {
    return this.resources.signups.list.filter(({ status }) =>
      status === 'accepted');
  },

  selectCourse(courseId) {
    // If user already has a selection and update it
    const currentSelection = this.resources.selections.list[0] || [];
    if (this.selected.length > 0) {
      const selectionId = currentSelection._id;
      const newSelection = [
        ...currentSelection.courses,
        courseId,
      ];
      return this.resources.selections.patchItem(
        selectionId,
        { courses: newSelection },
      );
      // TODO: Provide error feedback to user in .catch
    }

    // Otherwise create a new selection
    return this.resources.selections.post({
      nethz: session.user.nethz,
      courses: [courseId],
    });
  },

  deselectCourse(courseId) {
    const selection = this.resources.selections.list[0] || [];
    const newSelection = selection.courses.filter(item => item !== courseId);
    const selectionId = selection._id;

    if (newSelection.length === 0) {
      this.resources.selections.deleteItem(selectionId);
    } else {
      this.resources.selections.patchItem(
        selectionId,
        { courses: newSelection },
      );
    }
    // TODO: Provide error feedback to user in .catch
  },

  reserve() {},
  pay() {},
};

const courses = new Resource('courses', { embedded: { lecture: 1 } });
const lectures = new Resource('lectures');

module.exports = {
  userCourses,
  courses,
  lectures,
};
