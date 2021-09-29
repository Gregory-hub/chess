import os
import netifaces as ni
from netifaces import AF_INET
import logging
from logging import config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

hosts = [ni.ifaddresses(interface)[AF_INET][0]['addr'] for interface in ni.interfaces() if AF_INET in ni.ifaddresses(interface)]
hosts.append(hosts.pop(hosts.index('127.0.0.1')))
port = 5000

app = Flask(__name__, template_folder=os.path.abspath('templates'), static_folder=os.path.abspath('static'))
app.secret_key = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://' + os.environ.get('DB_USER') + ':' + os.environ.get('DB_PASSWORD') + '@localhost/chess'
db = SQLAlchemy(app)
socketio = SocketIO(app)
hasher = Bcrypt(app)
login_manager = LoginManager(app)
clients = []


logger_config = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s in %(module)s.%(funcName)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'simple': {
            'class': 'logging.FileHandler',
            'filename': 'logger.log',
            'level': 'INFO',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'chess': {
            'level': 'INFO',
            'handlers': {
                'simple'
            }
        }
    }
}
config.dictConfig(logger_config)
logger = logging.getLogger('chess')

from chess import routes
