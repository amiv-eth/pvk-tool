# new_pvk_tool
A new AMIV PVK tool using Eve and authenticating users with AMIVAPI.


## Frontend

WIP.


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
  ```
  mongo pvk_test --eval 'db.createUser({user:"pvk_user",pwd:"pvk_pass",roles:["readWrite"]});'
  ```

- Secondly, set up your virtual environment, install requirements as well as
  [py.test](https://docs.pytest.org/en/latest/).

  ```
  python -m venv env
  source env/bin/activate

  pip install -r requirements.txt
  pip install pytest
  ```

- Finally, you can run the tests from your virtual environment with:

  ```
  py.test
  ```
