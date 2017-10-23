// Basic Layout with sidebar
// Idea from https://mithril.js.org/simple-application.html

var m = require("mithril");
var api = require("./api.js");
var Session = api.Session;

var nethz = "";
var password = "";
var error = "";

var busy = false;
function ready() {return !busy && nethz && password;};

var Login = {
    view() {
        return Session.active() ? [
            // User is logged in
            m("p", "Hello, " + Session.user.name),
            Session.admin ? m("div", "You are an admin!") : [],
            m("button", {onclick() {
                busy= true;
                Session.logout().then(data => {
                    busy = false;
                    err = "";
                }).catch(err => {
                    error = err._error.message;
                    busy = false;
                })
            }}, "Abmelden"),
        ] : [
            // User is not logged in
            m("div", error),
            m("form", [
                m("label", "nethz"),
                m("input[type=text][placeholder=nethz]", {
                    oninput: m.withAttr("value", value => {nethz = value}),
                    value: nethz,
                }),
                m("label", "password"),
                m("input[type=text][placeholder=password]", {
                    oninput: m.withAttr("value", value => {password = value}),
                    value: password,
                }),

            ]),
            ready() ? m("button", {
                onclick() {
                    if (ready()) {
                        busy = true;
                        Session.login(nethz, password).then(data => {
                            // nethz("");
                            // password("");
                            error = "";
                            busy = false;
                        }).catch(err => {
                            error = err._error.message;
                            busy = false;
                        })
                    }
                }}, "Anmelden") : m("button[disabled]", "Anmelden"),
        ]
    },
};


module.exports = {
    view(vnode) {
        return m("main", [
            m("div", m(Login)),
            m("div", vnode.children),
        ])
    }
};
