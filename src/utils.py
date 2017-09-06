# utils.py
import json
# import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, Embedding, Dropout
import keras
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file

def build_model(window_size, vocab_size):
	# build the required RNN model: 
	# a single LSTM hidden layer with softmax activation,
	# categorical_crossentropy loss, and 200 units to unfold
	model = Sequential()
	units = 200
	model.add(LSTM(units, input_shape=(window_size, vocab_size)))
	model.add(Dense(vocab_size, activation='softmax'))
	optimizer = RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
	model.compile(loss='categorical_crossentropy', optimizer=optimizer)
	return model


def load_encoding(path):
	with open(path) as j:
  		return json.load(j)


def load_decoding(path):
	with open(path) as j:
  		return json.load(j)


def load_pentagram(PENTAGRAMDICT_OUTFILE):
	import cPickle
	with open(PENTAGRAMDICT_OUTFILE) as f:
		return cPickle.load(f)