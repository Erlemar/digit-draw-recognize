__author__ = 'Erlemar'
from functions import Model
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import base64
import os
import uuid
import boto
import boto3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import json

app = Flask(__name__)
model = Model()
CORS(app, headers=['Content-Type'])

@app.route("/", methods=["POST", "GET", 'OPTIONS'])
def index_page():

	return render_template('index.html')
	
@app.route("/about")
def about():

	return render_template('about.html')
	
@app.route("/internals")
def internals():

	return render_template('internals.html')

@app.route("/models")
def models():

	return render_template('models.html')

'''
@app.route('/hook', methods = ["GET", "POST", 'OPTIONS'])
#@cross_origin(origin='https://digits-draw-recognize.herokuapp.com')
def get_image():
	if request.method == 'POST':
		image_b64 = request.values['imageBase64']
		drawn_digit = request.values['digit']
		#print('Data received')
		image_encoded = image_b64.split(',')[1]
		image = base64.decodebytes(image_encoded.encode('utf-8'))		
		save = model.save_image(drawn_digit, image)	

	return save
'''
@app.route('/hook2', methods = ["GET", "POST", 'OPTIONS'])
def predict():
	if request.method == 'POST':
		image_b64 = request.values['imageBase64']
		print('Sending data to script')
		image_encoded = image_b64.split(',')[1]
		image = base64.decodebytes(image_encoded.encode('utf-8'))		
		prediction = model.predict(image)	

	return json.dumps(prediction)
	
@app.route('/hook3', methods = ["GET", "POST", 'OPTIONS'])
def train():
	if request.method == 'POST':
		image_b64 = request.values['imageBase64']
		image_encoded = image_b64.split(',')[1]
		image = base64.decodebytes(image_encoded.encode('utf-8'))
		digit = request.values['digit']
		model.train(image, digit)	

	return 'Trained'
	
if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port, debug=False)