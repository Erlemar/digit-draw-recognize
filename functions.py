__author__ = 'Artgor'
from sklearn.externals import joblib

from codecs import open
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
from neural_net import TwoLayerNet
from two_layer_net import net as tln2

class Model(object):
	def __init__(self):
		self.params = np.load('models/updated_weights.npy')[()]
		self.nothing = 0

	def process_image(self, image):
		filename = 'digit' +  '__' + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)
		img = Image.open('tmp/' + filename)

		bbox = Image.eval(img, lambda px: 255-px).getbbox()
		widthlen = bbox[2] - bbox[0]
		heightlen = bbox[3] - bbox[1]

		if heightlen > widthlen:
			widthlen = int(20.0 * widthlen/heightlen)
			heightlen = 20
		else:
			heightlen = int(20.0 * widthlen/heightlen)
			widthlen = 20

		hstart = int((28 - heightlen) / 2)
		wstart = int((28 - widthlen) / 2)

		img1 = img.crop(bbox).resize((widthlen, heightlen), Image.NEAREST)

		smallImg = Image.new('L', (28,28), 255)
		smallImg.paste(img1, (wstart, hstart))

		imgdata = list(smallImg.getdata())
		img_array = np.array([(255.0 - x) / 255.0 for x in imgdata])
		return img_array
	
	def save_image(self, drawn_digit, image):
		filename = 'digit' + str(drawn_digit) + '__' + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)
			
		REGION_HOST = 's3-external-1.amazonaws.com'
		conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		bucket = conn.get_bucket('digit_draw_recognize')
		
		k = Key(bucket)
		fn = 'tmp/' + filename
		k.key = filename
		k.set_contents_from_filename(fn)
		
		return ('Image saved successfully with the name {0}'.format(filename))
	
	def predict(self, image):
		img_array = self.process_image(image)
		net = tln2(self.params, input_size=28*28, hidden_size=100, output_size=10)
		#net.params = self.params

		prediction = net.predict_single(img_array)
		return prediction
		
	def train(self, image, digit):
		net = tln2(self.params, input_size=28*28, hidden_size=100, output_size=10)
		X = self.process_image(image)
		y = np.array(int(digit))
		net.train(X, y)
		np.save('models/updated_weights.npy', net.params)
		return 'ok'