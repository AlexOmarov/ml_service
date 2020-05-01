from flask import Flask
from waitress import serve

app = Flask(__name__)


if __name__ == '__main__':
    serve(app, listen='*:5000')
