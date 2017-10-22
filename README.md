# new_pvk_tool
A new AMIV PVK tool using Eve and authenticating users with AMIVAPI.

## Running the tests

```
pip install pytest

# Add the test user to the test database
mongo pvk_test --eval 'db.createUser({user:"pvkuser",pwd:"pvkpass",roles:["readWrite"]});'

py.test
```