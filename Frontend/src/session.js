// Session with AMIVAPI

import m from 'mithril';
import ls from 'local-storage';
import { amivApiUrl, adminGroupName } from 'config';

const storedSession = ls('session');

export default {
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
