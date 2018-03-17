# new_pvk_tool
A new AMIV PVK tool using Eve and authenticating users with AMIVAPI.


## Frontend

1. [Install Docker](https://www.docker.com/community-edition#/download)
   (Make sure to verify your installation!)

2. You need MongoDB. Luckily, you can just use Docker for that, too.
   (It's one long command, make sure to copy everything to your command line)
  
   ```bash
   docker run --name mongodb -d -p 27017 \
     -e MONGODB_DATABASE="pvk" \
     -e MONGODB_USERNAME="pvkuser" \
     -e MONGODB_PASSWORD="pvkpass" \
     bitnami/mongodb:latest
   ```
  
   The environment variables specified with `-e` make sure that the db and user
   are created

3. Start the dev-container

   ```bash
   docker run --name pvk -d -p 80:8080 \
     --link mongodb \
     -e MONGO_HOST="mongodb" \
     amiveth/pvk-backend
   ```

   The `--link` and `-e` make sure the backend can access the db container.

And now the backend is available at port 80, ready to use!

4. Create some demo data

```bash
python Backend/create_demo_data.py alex_itet_admin pvk
```

5. Now to the frontend: Install `node` and `npm`
   Inside the `Frontend` directory, fist install the build and dependencies
   with `npm install` and then start the dev server with `npm start`
   (the dev server will reload whenever you change anything. If it does not
   try `sudo npm start`)

   Now, in your browser, open `localhost:9000`


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
