#!/usr/bin/env python
# Usage:
# ./mtrain.py --data_dir data/T.1002_D.40 --num_epochs 50


from __future__ import print_function
import numpy as np
import tensorflow as tf
import sys, os, gc
from argparse import ArgumentParser
from utils import *
from six.moves import cPickle

parser = ArgumentParser()

parser.add_argument("-e", "--num_epochs", type=int)
parser.add_argument("-d", "--data_dir")
args = parser.parse_args()

# DATA_DIR = args.data_dir
DATA_DIR = args.data_dir if args.data_dir[-1]!="/" else args.data_dir[:-1] 
CONFIG_PATH = os.path.join(DATA_DIR, 'config.pkl')

XTENSOR_PATH = os.path.join(DATA_DIR, 'xtensor.npy')
YTENSOR_PATH = os.path.join(DATA_DIR, 'ytensor.npy')


def load_and_train():
	with open(CONFIG_PATH, "rb") as config_file:
		cfg = cPickle.load(config_file)

	window_size = cfg['window_size']
	vocab_size = cfg['vocab_size']

	x = np.zeros((cfg['input_size'], window_size, vocab_size), dtype=np.bool)
	y = np.zeros((cfg['input_size'], vocab_size), dtype=np.bool)

	inputs = np.load(XTENSOR_PATH)
	outputs = np.load(YTENSOR_PATH)

	# loop over inputs/outputs and tranform and store in x/y
	for i, statement in enumerate(inputs):
		for t, token in enumerate(statement):
			x[i, t, token] = 1.
		y[i, outputs[i][0]] = 1.

	inputs = None
	outputs = None
	gc.collect()

	model = build_model(window_size, vocab_size)
	# train the model
	model.fit(x, y, batch_size=1024, epochs=args.num_epochs, verbose=1)

	params = dict(map(lambda x: tuple(x.split(".")[:2]), DATA_DIR.split("/")[-1].split("_")))

	stamp = 'T.%s_D.%s_V.%d_W.%d_E.%d' % (
		params['T'], params['D'], vocab_size, window_size, args.num_epochs
		)

	WEIGHTS_PATH = 'results/weights/%s.hdf5' % stamp

	model.save_weights(WEIGHTS_PATH)


if __name__ == '__main__':
	load_and_train()
