import numpy as np

class net(object):
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

	def __init__(self, weights, input_size, hidden_size, output_size):
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
		self.params['W1'] = weights['W1']
		self.params['b1'] = weights['b1']
		self.params['W2'] = weights['W2']
		self.params['b2'] = weights['b2']

	def loss(self, X, y=None, reg=0.0):
		"""
		Compute the loss and gradients for a two layer fully connected neural
		network.

		Inputs:
		- X: Input data of shape (N, D). Each X[i] is a training sample.
		- y: Vector of training labels. y[i] is the label for X[i], and each y[i] is
		  an integer in the range 0 <= y[i] < C. This parameter is optional; if it
		  is not passed then we only return scores, and if it is passed then we
		  instead return the loss and gradients.
		- reg: Regularization strength.

		Returns:
		If y is None, return a matrix scores of shape (N, C) where scores[i, c] is
		the score for class c on input X[i].

		If y is not None, instead return a tuple of:
		- loss: Loss (data loss and regularization loss) for this batch of training
		  samples.
		- grads: Dictionary mapping parameter names to gradients of those parameters
		  with respect to the loss function; has the same keys as self.params.
		"""
		# Unpack variables from the params dictionary
		W1, b1 = self.params['W1'], self.params['b1']
		W2, b2 = self.params['W2'], self.params['b2']
		X = X.reshape(1, -1)
		y = y.reshape(1, -1)
		N, D = X.shape

		# Compute the forward pass
		l1 = X.dot(W1) + b1
		l1[l1 < 0] = 0
		l2 = l1.dot(W2) + b2
		exp_scores = np.exp(l2)
		probs = exp_scores / np.sum(exp_scores)

		# Backward pass: compute gradients
		grads = {}
		probs[range(X.shape[0]),y] -= 1
		dW2 = np.dot(l1.T, probs)
		dW2 /= X.shape[0]
		dW2 += reg * W2
		grads['W2'] = dW2
		grads['b2'] = np.sum(probs, axis=0, keepdims=True) / X.shape[0]
		
		delta = probs.dot(W2.T)
		delta = delta * (l1 > 0)
		grads['W1'] = np.dot(X.T, delta)/ X.shape[0] + reg * W1
		grads['b1'] = np.sum(delta, axis=0, keepdims=True) / X.shape[0]

		return grads

	def train(self, X, y, learning_rate=0.095, reg=0.001, batch_size=24):
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
		num_train = X.shape[0]

		# Use SGD to optimize the parameters in self.model
		loss_history = []
		train_acc_history = []
		val_acc_history = []

		X_batch = X
		y_batch = y
		# Compute loss and gradients using the current minibatch
		grads = self.loss(X_batch, y=y_batch, reg=reg)

		self.params['W1'] -= learning_rate * grads['W1']
		self.params['b1'] -= learning_rate * grads['b1'][0]
		self.params['W2'] -= learning_rate * grads['W2']
		self.params['b2'] -= learning_rate * grads['b2'][0]

		# Every epoch, check train and val accuracy and decay learning rate.


	def predict(self, X):
		"""
		Use the trained weights of this two-layer network to predict labels for
		data points. For each data point we predict scores for each of the C
		classes, and assign each data point to the class with the highest score.

		Inputs:
		- X: A numpy array of shape (N, D) giving N D-dimensional data points to
		  classify.

		Returns:
		- y_pred: A numpy array of shape (N,) giving predicted labels for each of
		  the elements of X. For all i, y_pred[i] = c means that X[i] is predicted
		  to have class c, where 0 <= c < C.
		"""
		l1 = X.dot(self.params['W1']) + self.params['b1']
		l1[l1 < 0] = 0
		l2 = l1.dot(self.params['W2']) + self.params['b2']
		exp_scores = np.exp(l2)
		probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
		y_pred = np.argmax(probs, axis=1)

		return y_pred

	def predict_single(self, X):
		"""
		Use the trained weights of this two-layer network to predict labels for
		data points. For each data point we predict scores for each of the C
		classes, and assign each data point to the class with the highest score.

		Inputs:
		- X: A numpy array of shape (N, D) giving N D-dimensional data points to
		  classify.

		Returns:
		- y_pred: A numpy array of shape (N,) giving predicted labels for each of
		  the elements of X. For all i, y_pred[i] = c means that X[i] is predicted
		  to have class c, where 0 <= c < C.
		"""
		l1 = X.dot(self.params['W1']) + self.params['b1']
		l1[l1 < 0] = 0
		l2 = l1.dot(self.params['W2']) + self.params['b2']
		exp_scores = np.exp(l2)
		y_pred = np.argmax(exp_scores)
		if y_pred < 0.5:
			return ('Do you even draw, bro? This is hardly a digit!')
		else:
			return str(y_pred)

