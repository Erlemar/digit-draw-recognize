__author__ = 'Artgor'
import time
print("Загрузка данных")
start_time = time.time()
from sentiment_classifier import SentimentClassifier
from codecs import open
import time
from flask import Flask, render_template, request
from scipy import misc
import numpy as np
from PIL import Image
import base64
import re
from io import StringIO
import os
app = Flask(__name__)

#print("Загрузка данных")
#start_time = time.time()
classifier = SentimentClassifier()
print("Функционал готов к работе, загрузка заняла {0} секунд.".format(time.time() - start_time))

@app.route("/", methods=["POST", "GET"])
def index_page(text="", prediction_message=""):
	if request.method == "POST":
		text = request.form["text"]
		logfile = open("demo_logs.txt", "a", "utf-8")
		print(text)
		print("<response>", file=logfile)
		print(text, file=logfile)
		image_b64 = request.values['imageBase64']
		image_data = re.sub('^data:image/.+;base64,', '', image_b64).decode('base64')
		image_PIL = Image.open(StringIO(image_b64))
		image_np = np.array(image_PIL)
		print('Image received: {}'.format(image_np.shape))
		prediction_message = 'Image'
		#prediction_message = classifier.simple_calculation(text)
		print (prediction_message)
		print(prediction_message, file=logfile)
		print("<response>", file=logfile)
		logfile.close()

	return render_template('hello.html', text=text, prediction_message=prediction_message)

@app.route('/hook', methods=['POST'])
def get_image():
	image_b64 = request.values['imageBase64']
	image_encoded = image_b64.split(',')[1]
	image = base64.decodebytes(image_encoded.encode('utf-8'))
	'digit1-O_n1'.split('n')
	drawn_digit = request.values['digit']
	images_with_digit = len([i for i in os.listdir('d:/_python/Python projects/final_demo_copy/images/') if 'digit' + str(drawn_digit) in i])
	type = 'O'
	filename = 'images/digit' + str(drawn_digit) + '-' + type + '_n' + str(images_with_digit) + '.jpg'
	with open("hello.txt", "w") as f:
		f.write(image_b64) 
	with open(filename, 'wb') as f:
		f.write(image)
	face = misc.imread(filename)

	print ('Image received: {}'.format(face.shape))
	
	return ''