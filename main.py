__author__ = 'Artgor'
import time
print("Loading data")
start_time = time.time()
from functions import Model
from codecs import open
import time
from flask import Flask, render_template, request
from functools import update_wrapper
from flask_cors import CORS, cross_origin
from scipy import misc
import numpy as np
from PIL import Image
import base64
import re
from io import StringIO
import os
import uuid
import boto
import boto3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from datetime import timedelta

start_time = time.time()
app = Flask(__name__)
model = Model()
print("Functionality is ready, loading took {0} seconds.".format(time.time() - start_time))
CORS(app, headers=['Content-Type'])

@app.route("/", methods=["POST", "GET", 'OPTIONS'])
#@cross_origin(origin='https://digits-draw-recognize.herokuapp.com')
def index_page(text="", prediction_message=""):

	return render_template('index.html', text=text, prediction_message=prediction_message)

@app.route('/hook', methods = ["GET", "POST", 'OPTIONS'])
#@cross_origin(origin='https://digits-draw-recognize.herokuapp.com')
def get_image():
	if request.method == 'POST':
		image_b64 = request.values['imageBase64']
		drawn_digit = request.values['digit']
		print('Data received')
		image_encoded = image_b64.split(',')[1]
		image = base64.decodebytes(image_encoded.encode('utf-8'))		
		save = model.save_image(drawn_digit, image)	

		print('Done')
	return save

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port, debug=False)