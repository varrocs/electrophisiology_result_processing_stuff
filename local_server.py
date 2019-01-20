
from flask import Flask, request
import main

app = Flask(__name__)

"""
A wrapper so the flask request can be passed to the main component
For local testing purposes
"""

@app.route('/', methods=['GET', 'POST'])
def test_handler():
    return main.upload_handler(request)
