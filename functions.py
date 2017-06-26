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


class Model(object):
	def __init__(self):
		#self.model = joblib.load()
		self.nothing = 0

	def save_image(self, drawn_digit, image):
		filename = 'digit' + str(drawn_digit) + '__' + str(uuid.uuid1()) + '.jpg'
		with open('tmp/' + filename, 'wb') as f:
			f.write(image)
			
		print('Image written')
		
		REGION_HOST = 's3-external-1.amazonaws.com'
		conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], host=REGION_HOST)
		bucket = conn.get_bucket('digit_draw_recognize')
		
		k = Key(bucket)
		fn = 'tmp/' + filename
		k.key = filename
		k.set_contents_from_filename(fn)
		print('Done')

		return ('Image saved successfully with the name {0}'.format(filename))
