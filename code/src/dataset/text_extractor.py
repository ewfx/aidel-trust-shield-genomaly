#create a flask application where we can upload a file and extract text from it
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import textract

app = Flask(__name__)
