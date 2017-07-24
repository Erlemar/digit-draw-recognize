__author__ = 'Artgor'

import base64
import os
import uuid
import random
import numpy as np

import boto
import boto3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from codecs import open
from PIL import Image
from scipy.ndimage.interpolation import rotate, shift
from skimage import transform

from two_layer_net import FNN
from conv_net import CNN

class Model(object):
	def __init__(self):
		"""
		Load weights for FNN here. Original weights are loaded from local folder, updated - from Amazon.
		"""
		self.params_original = np.load('models/original_weights.npy')[()]
		self.params = self.load_weights_amazon('updated_weights.npy')
			
	def process_image(self, image):
		"""
		Processing image for prediction. Saving in temproral folder so that it could be opened by PIL. Cropping and scaling so that the longest side it 20. Then putting it in a center of 28x28 blank image. Returning array of normalized data.
		"""
	
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

		img_temp = img.crop(bbox).resize((widthlen, heightlen), Image.NEAREST)

		new_img = Image.new('L', (28,28), 255)
		new_img.paste(img_temp, (wstart, hstart))

		imgdata = list(new_img.getdata())
		img_array = np.array([(255.0 - x) / 255.0 for x in imgdata])
		return img_array
	
	def augment(self, image, label):
		"""
		Augmenting image for training. Saving in temproral folder so that it could be opened by PIL. Cropping and scaling so that the longest side it 20. The width and height of the scaled image are used to resize it again so that there would be 4 images with different combinatins of weight and height. Then putting it in a center of 28x28 blank image. 12 possible angles are defined and each image is randomly rotated by 6 of these angles. Images converted to arrays and normalized. 
		Returning these arrays and labels.
		"""
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
					img_temp = Image.fromarray(np.uint8(transformed_image))
					imgdata = list(img_temp.getdata())
					normalized_img = [(255.0 - x) / 255.0 for x in imgdata]
					ims_add.append(normalized_img)
		image_array = np.array(ims_add)
		label_array = np.array(labs_add)
		return image_array, label_array
	
	def load_weights_amazon(self, filename):
		"""
		Load weights from Amazon. This is npy. file, which neads to be read with np.load.
		"""
		s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
		s3.download_file('digit_draw_recognize', filename, os.path.join('tmp/', filename))
		return np.load(os.path.join('tmp/', filename))[()]
	
	def save_weights_amazon(self, filename, file):
		"""
		Save weights to Amazon.
		"""
		REGION_HOST = 's3-external-1.amazonaws.com'
		conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		bucket = conn.get_bucket('digit_draw_recognize')
		k = Key(bucket)
		k.key = filename
		k.set_contents_from_filename('tmp/' + filename)
		return ('Weights saved')
	
	def save_image(self, drawn_digit, image):
		"""
		Save image on Amazon. Only existing files can be uploaded, so the image is saved in a temporary folder.
		"""
		filename = 'digit' + str(drawn_digit) + '__' + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)
		REGION_HOST = 's3-external-1.amazonaws.com'
		conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		bucket = conn.get_bucket('digit_draw_recognize')
		k = Key(bucket)
		k.key = filename
		k.set_contents_from_filename('tmp/' + filename)
		return ('Image saved successfully with the name {0}'.format(filename))
	
	def predict(self, image):
		"""
		Predicting image. If nothing is drawn, returns a message; otherwise 4 models are initialized and they make predictions. They return a list of tuples with 3 top predictions and their probabilities. These lists are sent to "select_answer" method to select the best answer. Also tuples are converted into strings for easier processing in JS. The answer and lists with predictions and probabilities are returned.
		"""
	
		img_array = self.process_image(image)
		if img_array is None:
			return "Can't predict, when nothing is drawn"
		net = FNN(self.params)
		net_original = FNN(self.params_original)
		cnn = CNN()
		cnn_original = CNN()
		
		top_3 = net.predict_single(img_array)
		top_3_original = net_original.predict_single(img_array)
		top_3_cnn = cnn.predict(img_array, weights='original')
		top_3_cnn_original = cnn_original.predict(img_array, weights='updated')
		answer, top_3, top_3_original, top_3_cnn, top_3_cnn_original = self.select_answer(top_3, top_3_original, top_3_cnn, top_3_cnn_original)
		
		answers_dict = {'answer': str(answer), 'fnn_t': top_3, 'fnn': top_3_original, 'cnn_t': top_3_cnn, 'cnn': top_3_cnn_original}
		#return answer, top_3, top_3_original
		return answers_dict
		
	def train(self, image, digit):
		"""
		Models are trained. Weights on Amazon are updated.
		"""
		net = FNN(self.params)
		X, y = self.augment(image, digit)
		net.train(X, y)
		cnn = CNN()
		cnn.train(X, y)
		np.save('tmp/updated_weights.npy', net.params)
		response = self.save_weights_amazon('updated_weights.npy', './tmp/updated_weights.npy')
		
		response = self.save_weights_amazon('data-all_2_updated.chkp.meta', './tmp/data-all_2_updated.chkp')
		response = self.save_weights_amazon('data-all_2_updated.chkp.index', './tmp/data-all_2_updated.chkp')
		response = self.save_weights_amazon('data-all_2_updated.chkp.data-00000-of-00001', './tmp/data-all_2_updated.chkp')
		
		return response
	
	def select_answer(self, top_3, top_3_original, top_3_cnn, top_3_cnn_original):
		"""
		Selects best answer from all. In fact only from the trained models, as they are considered to be better than untrained.
		"""
		answer = ''
		
		if int(top_3[0][0]) == int(top_3_cnn[0][0]):
			answer = str(top_3[0][0])
		elif int(top_3[0][1]) < 50 and int(top_3_cnn[0][1]) < 50:
			answer = "Can't recognize this as a digit"
		elif int(top_3[0][0]) != int(top_3_cnn[0][0]):
			if int(top_3[0][1]) > int(top_3_cnn[0][1]):
				answer = str(top_3[0][0])
			else:
				answer = str(top_3_cnn[0][0])
		
		top_3 = ['{0} ({1})%'.format(i[0], i[1]) for i in top_3]
		top_3_original = ['{0} ({1})%'.format(i[0], i[1]) for i in top_3_original]
		top_3_cnn = ['{0} ({1})%'.format(i[0], i[1]) for i in top_3_cnn]
		top_3_cnn_original = ['{} ({:2.4})%'.format(i[0], i[1]) for i in top_3_cnn_original]
		
		return answer, top_3, top_3_original, top_3_cnn, top_3_cnn_original