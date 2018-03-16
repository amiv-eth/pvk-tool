# wsgi server (used in docker container)
# [bjoern](https://github.com/jonashaag/bjoern) required.

from backend.app import create_app
import bjoern

if __name__ == '__main__':
    print('Starting bjoern on port 8080...', flush=True)
    bjoern.run(create_app(), '0.0.0.0', 8080)
