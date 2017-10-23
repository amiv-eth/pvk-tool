var m = require("mithril")
var root = document.body

var Layout = require("./layout.js")

var user = {}

// var MyComponent = require("./mycomponent")

var count = 0 // added a variable

var Hello = {
    view: function() {
        return m("main", [
            m("h1", {class: "title"}, "My first app"),
            // changed the next line
            m("button", {onclick: function() {count++}}, count + " clicks"),
        ])
    }
}

var Splash = {
    view: function() {
        return m("a", {href: "#!/hello"}, "Enter!")
    }
}



m.route(root, "/courses", {
    "/courses": {render() {return m(Layout, m(Splash))}},
    "/hello": {render() {return m(Layout, m(Hello))}},
})

