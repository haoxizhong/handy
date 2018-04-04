import logging
import os
import sys

if __name__ == '__main__':
    sys.setrecursionlimit(10 ** 5)
    from application import app, initialize

    initialize()

    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"], threaded=True)
