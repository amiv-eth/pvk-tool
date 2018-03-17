# new_pvk_tool
A new AMIV PVK tool using Eve and authenticating users with AMIVAPI.


## Frontend

The frontend is build using [mithril](https://mithril.js.org) and uses
the [webpack build system](https://webpack.js.org).

In order to bundle all files and use the development server, you first
need to install [node](https://nodejs.org/) and[npm](https://www.npmjs.com).

Afterwards, you can use the following commands:

```bash
# Install dependencies and build system
npm install

# Start development server
# (As soon as its running, open `localhost:9000` in your browser)
npm start

# The development server reloads if you change anything, if it does not, use:
sudo npm start

# Check coding style
npm run lint

# Bundle files for production
npm run build
```

## Backend

The backend is implemented using [Eve](http://python-eve.org), a python
framework built on [Flask](http://flask.pocoo.org) that allows to create REST
APIs with incredible ease (We use the same framework for *AMIVAPI*).

### How to help developing

To get started, you should first check out the
[Eve Quickstart](http://python-eve.org/quickstart.html) to get an idea about
how the framework works. This should only take you around 10 minutes.

Afterwards, start with the file `app.py` to get into the PVK Tool code and
keep the *Eve* and *Flask* docs at hand, if you need to look anything up.

If you add any features, don't forget to write tests!
But don't worry, it's very easy to set them up -- take a look at the
`tests` directory.

### Running the tests locally

- First of all, you need [MongoDB](https://www.mongodb.com) installed and
  running locally.

  Next, create the test user: Add the user `pvk_user` with password `pvk_pass`
  and `readWrite` permission to the `pvk_test` database.

  On Linux or similar, you can use this one-liner:
  
  ```bash
  mongo pvk_test --eval 'db.createUser({user:"pvk_user",pwd:"pvk_pass",roles:["readWrite"]});'
  ```

- Secondly, set up your virtual environment, install requirements as well as
  [py.test](https://docs.pytest.org/en/latest/).

  ```bash
  python -m venv env
  source env/bin/activate
  pip install -r requirements.txt
  pip install pytest
  ```

- Finally, you can run the tests from your virtual environment with:

  ```bash
  py.test
  ```

- Per default, integration tests with amivapi are skipped, since they require
  valid amivapi tokens. 

  You can run  `py.test -rs` to get a summary including skipped tests.

  The api tests can be included by provide tokens for a user (*not in* the
  `PVK Admins` group) and an admin (*in* the `PVK Admins` group)

  ```bash
  # Replace <usertoken> and <admintoken> (including <>) with your tokens
  py.test -rs --usertoken <usertoken> --admintoken <admintoken>
  ```

  An easy way to aquire the tokens is `curl`:

  ```bash
  curl -X POST -Fusername <user> -Fpassword <pass> amiv-api.ethz.ch/sessions
  ```

### Development server reset

We have a development server running. The script `reset_development_server.py`
completely resets its data. (Everything gets deleted and re-created)
Install `requests` (e.g. using `pip install requests`) to use it.
