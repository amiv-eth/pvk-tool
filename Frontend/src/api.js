// Api calls

const m = require('mithril');
const ls = require('local-storage');

const amivApiUrl = 'https://amiv-api.ethz.ch';
const pvkApiUrl = `//${window.location.hostname}/api`;

const adminGroupName = 'PVK Admins';

const storedSession = ls('session');


// Session with AMIVAPI
const Session = {
  // Quick check if session exists
  active() { return this.data.token; },

  // User data
  user: storedSession ? storedSession.user : {},

  // Session data
  data: storedSession ? storedSession.data : {},

  // Admin?
  admin: storedSession ? storedSession.admin : false,

  // Safe to local-storage
  safe() {
    ls('session', {
      user: this.user,
      data: this.data,
      admin: this.admin,
    });
  },

  // Remove all session data and clear local storage
  clear() {
    this.user = '';
    this.data = '';
    this.admin = false;
    ls.remove('session');
  },

  // Login and Logout
  login(username, password) {
    // Login and request user data along with the session
    return m.request({
      method: 'POST',
      url: `${amivApiUrl}/sessions?embedded={"user": 1}`,
      data: { username, password },
    }).then((data) => {
      // Session data
      this.data = {
        token: data.token,
        _id: data._id,
        _etag: data._etag,
      };

      // User data
      this.user = {
        name: data.user.firstname,
        nethz: data.user.nethz,
        department: data.user.department,
        _id: data.user._id,
      };

      // Check if admin
      this.check_admin(data.token);

      this.safe();
    });
  },
  logout() {
    if (this.data.token) {
      return m.request({
        method: 'DELETE',
        url: `${amivApiUrl}/sessions/${this.data._id}`,
        headers: {
          Authorization: `Token ${this.data.token}`,
          'If-Match': this.data._etag,
        },
      }).then(() => {
        this.clear();
      }).catch((err) => {
        if (err._error.code === 401) {
          // Token already no valid anymore, clear session
          this.clear();
        } else {
          throw err._error;
        }
      });
    }
    // Otherwise nothing to do, return a promise that always resolves
    return Promise.resolve();
  },

  check_admin(token) {
    // First: Look for Admin Group
    let query = m.buildQueryString({
      projection: { _id: 1 },
      where: { name: adminGroupName },
    });
    m.request({
      method: 'GET',
      url: `${amivApiUrl}/groups?${query}`,
      headers: { Authorization: `Token ${token}` },
    }).then((data) => {
      if (data._meta.total !== 0) {
        // Admin group exists and we have it's id, check membership
        query = m.buildQueryString({
          where: {
            user: this.user._id,
            group: data._items[0]._id,
          },
        });
        return m.request({
          method: 'GET',
          url: `${amivApiUrl}/groupmemberships?${query}`,
          headers: { Authorization: `Token ${token}` },
        });
      }
      // Can't continue, return a promise that always rejects
      return Promise.reject();
    }).then((data) => {
      if (data._meta.total !== 0) {
        // User is admin!
        this.admin = true;
        this.safe();
      }
    }).catch(() => {
      // User is no admin.
      this.admin = false;
      this.safe();
    });
  },
};


// Request to the PVK backend
function request({
  resource, method = 'GET', id = '', data = {}, query = {},
}) {
  // Parse query such that the backend understands it
  const parsedQuery = {};
  Object.keys(query).forEach((key) => {
    parsedQuery[key] = JSON.stringify(query[key]);
  });
  const queryString = m.buildQueryString(parsedQuery);

  // Send the request
  return m.request({
    method,
    data,
    url: `${pvkApiUrl}/${resource}/${id}?${queryString}`,
    headers: { Authorization: `Token ${Session.data.token}` },
  }).catch((err) => {
    // If the error is 401, the token is invalid -> auto log out
    if (err._error.code === 401) { Session.clear(); }

    // Actual error information is in the '_error' field, pass this on
    throw err._error;
  });
}


// Generic PVK resource
class Resource {
  constructor(name, query = {}) {
    this.name = name;
    this.list = [];
    this.query = query;
  }

  load() {
    return request({ resource: this.name, query: this.query }).then((data) => {
      // Fill own list
      this.list = data._items;
      // Pass on data
      return data;
    });
  }
}


const UserCourses = {
  resources: {
    selections: new Resource(
      'selections',
      { where: { nethz: Session.user.nethz } },
    ),
    signups: new Resource(
      'signups',
      { where: { nethz: Session.user.nethz } },
    ),
  },

  load() {
    this.resources.selections.load().then(() => {
      // We are only interested in one the first (and single) element
      this.resources.selections.list = this.resources.selections.list[0] || [];
    });
    this.resources.signups.load();
  },

  get selected() { return this.resources.selections.list; },
  get reserved() {
    return this.resources.signups.list.filter(({ status }) =>
      status === 'reserved');
  },
  get accepted() {
    return this.resources.signups.list.filter(({ status }) =>
      status === 'accepted');
  },

  // TODO(Alex)
  select() {},
  reserve() {},
  pay() {},
};

const Courses = new Resource('courses', { embedded: { lecture: 1 } });


module.exports = {
  Session,
  request,
  UserCourses,
  Courses,
};
