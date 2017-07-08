__author__ = 'Artgor'
#from sklearn.externals import joblib

from codecs import open
#from scipy import misc
import numpy as np
from PIL import Image
import base64
#import re
#from io import StringIO
import os
import uuid
import boto
import boto3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
#from neural_net import TwoLayerNet
from two_layer_net import net as tln2
import random
from scipy.ndimage.interpolation import rotate, shift
from skimage import transform

class Model(object):
	def __init__(self):
		#self.params = np.load('models/updated_weights.npy')[()]
		self.params = self.load_weights_amazon('updated_weights.npy')
		self.nothing = 0

	def process_image(self, image):
		filename = 'digit' +  '__' + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)
		img = Image.open('tmp/' + filename)

		bbox = Image.eval(img, lambda px: 255-px).getbbox()
		if bbox == None:
			return None
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
	
	def augment(self, image, label):
		filename = 'digit' +  '__' + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)
		image = Image.open('tmp/' + filename)
		
		ims_add = []
		labs_add = []
		angles = np.arange(-30, 30, 5)
		bbox = Image.eval(image, lambda px: 255-px).getbbox()

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

		for i in [min(widthlen, heightlen), max(widthlen, heightlen)]:
			for j in [min(widthlen, heightlen), max(widthlen, heightlen)]:
				resized_img = image.crop(bbox).resize((i, j), Image.NEAREST)
				resized_image = Image.new('L', (28,28), 255)
				resized_image.paste(resized_img, (wstart, hstart))

				angles_ = random.sample(set(angles), 6)
				for angle in angles_:
					transformed_image = transform.rotate(np.array(resized_image), angle, cval=255, preserve_range=True).astype(np.uint8)
					labs_add.append(int(label))
					#ims_add.append(Image.fromarray(np.uint8(transformed_image)))
					img_temp = Image.fromarray(np.uint8(transformed_image))
					imgdata = list(img_temp.getdata())
					normalized_img = [(255.0 - x) / 255.0 for x in imgdata]
					ims_add.append(normalized_img)
		image_array = np.array(ims_add)
		label_array = np.array(labs_add)
		return image_array, label_array
	
	def load_weights_amazon(self, filename):
		s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
		s3.download_file('digit_draw_recognize', filename, os.path.join('tmp/', filename))
		return np.load(os.path.join('tmp/', filename))[()]
	
	def save_weights_amazon(self, filename, file):
		#with open('tmp/' + filename, 'wb') as f:
		#	f.write(file)
		np.save(os.path.join('tmp/', filename), file)
		REGION_HOST = 's3-external-1.amazonaws.com'
		conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		bucket = conn.get_bucket('digit_draw_recognize')
		k = Key(bucket)
		fn = 'tmp/' + filename
		k.key = filename
		k.set_contents_from_filename(fn)
		
		return ('Weights saved')
	
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
		if img_array == None:
			return "Can't predict, when nothing is drawn"
		net = tln2(self.params, input_size=28*28, hidden_size=100, output_size=10)
		#net.params = self.params

		prediction = net.predict_single(img_array)
		return prediction
		
	def train(self, image, digit):
		net = tln2(self.params, input_size=28*28, hidden_size=100, output_size=10)
		#X = self.process_image(image)
		#y = np.array(int(digit))
		X, y = self.augment(image, digit)
		net.train(X, y)
		response = self.save_weights_amazon('updated_weights.npy', net.params)
		#np.save('models/updated_weights.npy', net.params)
		return response