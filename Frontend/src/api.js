// Api calls

var m = require("mithril");

var apiUrl = "https://amiv-api.ethz.ch";
var adminGroupName = "PVK Admins";

var Session = {
    // Quick check if session exists
    active() {return this.data.token},

    // User data
    user: {},

    // Session data
    data: {},

    // Admin?
    admin: false,

    // Login and Logout
    login(username, password) {
        // Login and request user data along with the session
        return m.request({
            method: "POST",
            url: apiUrl + '/sessions?embedded={"user": 1}',
            data: {
                username: username,
                password: password
            },
        }).then(data => {
            // Session data
            this.data = {
                token: data.token,
                _id: data._id,
                _etag: data._etag,
            }

            // User data
            this.user = {
                name: data.user.firstname,
                nethz: data.user.nethz,
                department: data.user.department,
                _id: data.user._id,
            }

            // Check if admin
            this.check_admin(data.token);
        })
    },
    logout() {
        if (this.data.token) {
            return m.request({
                method: "DELETE",
                url: apiUrl + "/sessions/" + this.data._id,
                headers: {
                    Authorization: "Token " + this.data.token,
                    "If-Match": this.data._etag,
                },
            }).then((data) => {
                this.data = this.user = {};
                this.admin = false;
            })
        } else {
            // Nothing to do, return promise that always resolves
            return Promise.resolve();
        }
    },

    check_admin(token) {
        // First: Look for Admin Group
        let projection = "projection=" + JSON.stringify({'_id': 1});
        let where = "where=" + JSON.stringify({'name': adminGroupName});

        m.request({
            method: "GET",
            url: apiUrl + "/groups?" + projection + "&" + where,
            headers: {Authorization: "Token " + token},
        }).then((data) => {
            if (data._meta.total !== 0) {
                // Admin group exists and we have it's id, check membership
                let groupId = data._items[0]._id;
                let where = 'where=' + JSON.stringify({
                    user: this.user._id,
                    group: groupId,
                });
                m.request({
                    method: "GET",
                    url: apiUrl + "/groupmemberships?" + where,
                    headers: {Authorization: "Token " + token},
                }).then((data) => {
                    if (data._meta.total !== 0) {
                        // User is admin!
                        this.admin = true;
                    };
                })
            }
        });
    },
};

module.exports = {
    Session: Session,
};
