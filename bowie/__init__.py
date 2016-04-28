"""Flask web server initialization"""
from flask import Flask
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
import bowie.views
