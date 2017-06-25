__author__ = 'Artgor'
import time
print("Loading data")
start_time = time.time()
#from sentiment_classifier import SentimentClassifier
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
import uuid
import boto
import boto3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
app = Flask(__name__)
#start_time = time.time()
#classifier = SentimentClassifier()
print("Functionality is ready, loading took {0} seconds.".format(time.time() - start_time))




def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route("/", methods=["POST", "GET"])
@crossdomain(origin='*')
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

@app.route('/hook', methods = ["GET", "POST"])
@crossdomain(origin='*')
def get_image():
	if request.method == 'POST':
		image_b64 = request.values['imageBase64']
		image_encoded = image_b64.split(',')[1]
		image = base64.decodebytes(image_encoded.encode('utf-8'))
		'digit1-O_n1'.split('n')
		drawn_digit = request.values['digit']
		type = 'O'
		filename = 'digit' + str(drawn_digit) + '-' + type + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)

		REGION_HOST = 's3-external-1.amazonaws.com'
		#S3_BUCKET = os.environ.get('S3_BUCKET')
		#AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
		#AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
		#return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
		#conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, host=REGION_HOST)
		conn = S3Connection('AKIAIRXR5PJRWK6YVZMA', 'hKjhSC6Rtqvkww4JcgQOfVfQLocGm8GBUEEWgtmc', host=REGION_HOST)
		#conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		#conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		bucket = conn.get_bucket('digit_draw_recognize')
		#print(bucket, os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])
		k = Key(bucket)
		key = filename
		fn = 'tmp/' + filename
		k.key = key
		k.set_contents_from_filename(fn)
		print('Done')
	return filename

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port, debug=False)