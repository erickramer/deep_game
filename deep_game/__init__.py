from flask import Flask
app = Flask(__name__)

from models import Board
board = Board()

import views
