import numpy as np
import boto
import boto3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import tensorflow as tf
import os

class CNN(object):
	"""
	A two-layer fully-connected neural network. The net has an input dimension of
	N, a hidden layer dimension of H, and performs classification over C classes.
	We train the network with a softmax loss function and L2 regularization on the
	weight matrices. The network uses a ReLU nonlinearity after the first fully
	connected layer.

	In other words, the network has the following architecture:

	input - fully connected layer - ReLU - fully connected layer - softmax

	The outputs of the second fully-connected layer are the scores for each class.
	"""

	def __init__(self):
		"""
		Initialize the model. Weights are initialized to small random values and
		biases are initialized to zero. Weights and biases are stored in the
		variable self.params, which is a dictionary with the following keys:

		W1: First layer weights; has shape (D, H)
		b1: First layer biases; has shape (H,)
		W2: Second layer weights; has shape (H, C)
		b2: Second layer biases; has shape (C,)

		Inputs:
		- input_size: The dimension D of the input data.
		- hidden_size: The number of neurons H in the hidden layer.
		- output_size: The number of classes C.
		"""
		self.params = {}

	def model(self, X, w, w3, w4, w_o, p_keep_conv, p_keep_hidden):
		l1a = tf.nn.relu(tf.nn.conv2d(X, w, strides=[1, 1, 1, 1], padding='SAME') + b1)
		l1 = tf.nn.max_pool(l1a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		l1 = tf.nn.dropout(l1, p_keep_conv)

		l3a = tf.nn.relu(tf.nn.conv2d(l1, w3, strides=[1, 1, 1, 1], padding='SAME') + b3)
		l3 = tf.nn.max_pool(l3a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		l3 = tf.reshape(l3, [-1, w4.get_shape().as_list()[0]])    # reshape to (?, 2048)
		l3 = tf.nn.dropout(l3, p_keep_conv)

		l4 = tf.nn.relu(tf.matmul(l3, w4) + b4)
		l4 = tf.nn.dropout(l4, p_keep_hidden)

		pyx = tf.matmul(l4, w_o) + b5
		return pyx

	def train(self, image, digit):
		"""
		Train this neural network using stochastic gradient descent.

		Inputs:
		- X: A numpy array of shape (N, D) giving training data.
		- y: A numpy array f shape (N,) giving training labels; y[i] = c means that
		  X[i] has label c, where 0 <= c < C.
		- X_val: A numpy array of shape (N_val, D) giving validation data.
		- y_val: A numpy array of shape (N_val,) giving validation labels.
		- learning_rate: Scalar giving learning rate for optimization.
		- reg: Scalar giving regularization strength.
		- num_iters: Number of steps to take when optimizing.
		- batch_size: Number of training examples to use per step.
		- verbose: boolean; if true print progress during optimization.
		"""

		#f = 'data-all_2_updated.chkp'
		tf.reset_default_graph()
		init_op = tf.global_variables_initializer()
		#sess = tf.Session()

		X = tf.placeholder("float", [None, 28, 28, 1])
		Y = tf.placeholder("float", [None, 10])

		w = tf.get_variable("w", shape=[4, 4, 1, 16], initializer=tf.contrib.layers.xavier_initializer())
		b1 = tf.get_variable(name="b1", shape=[16], initializer=tf.zeros_initializer())
		#w2 = tf.get_variable("w2", shape=[5, 5, 32, 64],
		#           initializer=tf.contrib.layers.xavier_initializer())
		#b2 = tf.get_variable(name="b2", shape=[64], initializer=tf.zeros_initializer())
		w3 = tf.get_variable("w3", shape=[4, 4, 16, 32], initializer=tf.contrib.layers.xavier_initializer())
		b3 = tf.get_variable(name="b3", shape=[32], initializer=tf.zeros_initializer())
		w4 = tf.get_variable("w4", shape=[32 * 7 * 7, 625], initializer=tf.contrib.layers.xavier_initializer())
		w_o = tf.get_variable("w_o", shape=[625, 10], initializer=tf.contrib.layers.xavier_initializer())
		b4 = tf.get_variable(name="b4", shape=[625], initializer=tf.zeros_initializer())

		p_keep_conv = tf.placeholder("float")
		p_keep_hidden = tf.placeholder("float")
		b5 = tf.get_variable(name="b5", shape=[10], initializer=tf.zeros_initializer())
		l1a = tf.nn.relu(tf.nn.conv2d(X, w, strides=[1, 1, 1, 1], padding='SAME') + b1)
		l1 = tf.nn.max_pool(l1a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		l1 = tf.nn.dropout(l1, p_keep_conv)

		l3a = tf.nn.relu(tf.nn.conv2d(l1, w3, strides=[1, 1, 1, 1], padding='SAME') + b3)
		l3 = tf.nn.max_pool(l3a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		l3 = tf.reshape(l3, [-1, w4.get_shape().as_list()[0]])    # reshape to (?, 2048)
		l3 = tf.nn.dropout(l3, p_keep_conv)

		l4 = tf.nn.relu(tf.matmul(l3, w4) + b4)
		l4 = tf.nn.dropout(l4, p_keep_hidden)

		py_x = tf.matmul(l4, w_o) + b5
						
		reg_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
		reg_constant = 0.01

		cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=py_x, labels=Y)+ reg_constant * sum(reg_losses))

		train_op = tf.train.RMSPropOptimizer(0.00001).minimize(cost)
		predict_op = tf.argmax(py_x, 1)
		
		with tf.Session() as sess:
			# you need to initialize all variables
			saver = tf.train.Saver()
			saver.restore(sess, "./tmp/data-all_2_updated.chkp")
			trX = image.reshape(-1, 28, 28, 1)  # 28x28x1 input img
			trY = np.eye(10)[digit]
			sess.run(train_op, feed_dict={X: trX, Y: trY,
											  p_keep_conv: 1, p_keep_hidden: 1})
			all_saver = tf.train.Saver() 
			all_saver.save(sess, './tmp/data-all_2_updated.chkp')

	def predict(self, image, weights='original'):
		s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
		if weights == 'original':
			f = 'data-all_2.chkp'
		else:
			f = 'data-all_2_updated.chkp'
		fn = f + '.meta'
		s3.download_file('digit_draw_recognize', fn, os.path.join('tmp/', fn))
		fn = f + '.index'
		s3.download_file('digit_draw_recognize', fn, os.path.join('tmp/', fn))
		fn = f + '.data-00000-of-00001'
		s3.download_file('digit_draw_recognize', fn, os.path.join('tmp/', fn))
		tf.reset_default_graph()
		init_op = tf.global_variables_initializer()
		sess = tf.Session()

		X = tf.placeholder("float", [None, 28, 28, 1])
		Y = tf.placeholder("float", [None, 10])

		w = tf.get_variable("w", shape=[4, 4, 1, 16], initializer=tf.contrib.layers.xavier_initializer())
		b1 = tf.get_variable(name="b1", shape=[16], initializer=tf.zeros_initializer())
		#w2 = tf.get_variable("w2", shape=[5, 5, 32, 64],
		#           initializer=tf.contrib.layers.xavier_initializer())
		#b2 = tf.get_variable(name="b2", shape=[64], initializer=tf.zeros_initializer())
		w3 = tf.get_variable("w3", shape=[4, 4, 16, 32], initializer=tf.contrib.layers.xavier_initializer())
		b3 = tf.get_variable(name="b3", shape=[32], initializer=tf.zeros_initializer())
		w4 = tf.get_variable("w4", shape=[32 * 7 * 7, 625], initializer=tf.contrib.layers.xavier_initializer())
		w_o = tf.get_variable("w_o", shape=[625, 10], initializer=tf.contrib.layers.xavier_initializer())
		b4 = tf.get_variable(name="b4", shape=[625], initializer=tf.zeros_initializer())

		p_keep_conv = tf.placeholder("float")
		p_keep_hidden = tf.placeholder("float")
		b5 = tf.get_variable(name="b5", shape=[10], initializer=tf.zeros_initializer())
		l1a = tf.nn.relu(tf.nn.conv2d(X, w, strides=[1, 1, 1, 1], padding='SAME') + b1)
		l1 = tf.nn.max_pool(l1a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		l1 = tf.nn.dropout(l1, p_keep_conv)

		l3a = tf.nn.relu(tf.nn.conv2d(l1, w3, strides=[1, 1, 1, 1], padding='SAME') + b3)
		l3 = tf.nn.max_pool(l3a, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
		l3 = tf.reshape(l3, [-1, w4.get_shape().as_list()[0]])    # reshape to (?, 2048)
		l3 = tf.nn.dropout(l3, p_keep_conv)

		l4 = tf.nn.relu(tf.matmul(l3, w4) + b4)
		l4 = tf.nn.dropout(l4, p_keep_hidden)

		py_x = tf.matmul(l4, w_o) + b5
		#py_x = self.model(X, w, w3, w4, w_o, p_keep_conv, p_keep_hidden)

		reg_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
		reg_constant = 0.01

		cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=py_x, labels=Y)+ reg_constant * sum(reg_losses))

		train_op = tf.train.RMSPropOptimizer(0.00001).minimize(cost)
		predict_op = tf.argmax(py_x, 1)
		probs = tf.nn.softmax(py_x)
		saver = tf.train.Saver()
		saver.restore(sess, "./tmp/" + f)
		y_pred = sess.run(probs, feed_dict={X: image.reshape(-1, 28, 28, 1), p_keep_conv: 1.0, p_keep_hidden: 1.0})
		probs = y_pred
		top_3 = list(zip(np.argsort(probs)[0][::-1][:3], np.round(probs[0][np.argsort(probs)[0][::-1][:3]] * 100, 2)))
		sess.close()
		return top_3