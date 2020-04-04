from flask import Flask
from dev import api_manager
from utils import config

# Flask application factory pattern is not used here as Flask is only used for
# dev purposes on the local machine.
# Only the necessary files (i.e. /logic and /utils folders) are packaged to run
# as a set of serverless functions on AWS Lambda in production.

app = Flask(__name__)
api_manager.init(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.FLASK_PORT, debug=True)
