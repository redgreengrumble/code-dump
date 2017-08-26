#!/usr/bin/env python
# Usage:
# ./encode_text.py --data_dir data/T.0914_D.50/ -w 20

from __future__ import print_function
import os, gc, collections
from argparse import ArgumentParser
import numpy as np
from six.moves import cPickle
import json

parser = ArgumentParser()
parser.add_argument("-i", "--data_dir")
parser.add_argument("-w", "--window_size", type=int, default=20)
parser.add_argument("-s", "--step_size", type=int, default=1)
args = parser.parse_args()

# DATA_DIR = args.data_dir
DATA_DIR = args.data_dir if args.data_dir[-1]!="/" else args.data_dir[:-1]
TRAIN_PATH = os.path.join(DATA_DIR, 'train.txt')
VOCAB_PATH = os.path.join(DATA_DIR, 'vocab.pkl')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.pkl')

XTENSOR_PATH = os.path.join(DATA_DIR, 'xtensor.npy')
YTENSOR_PATH = os.path.join(DATA_DIR, 'ytensor.npy')

WINDOW_SIZE = args.window_size
step_size = args.step_size
ENCODING = None
VOCAB_SIZE = 0
INPUT_SIZE = 0

def load_encoding():
	global VOCAB_SIZE
	global ENCODING
	global UNK_ENCODING

	with open(VOCAB_PATH, 'rb') as f:
		words = cPickle.load(f)
	VOCAB_SIZE = len(words)
	ENCODING = dict(zip(words, range(VOCAB_SIZE)))
	UNK_ENCODING = ENCODING["<UNK>"]

def encode(token):
	if token in ENCODING:
		return ENCODING[token]
	else:
		return UNK_ENCODING

def encode_text(train_path, WINDOW_SIZE, step_size):
	global INPUT_SIZE
	inputs = []
	outputs = []
	with open(train_path) as train_set:
		for q in train_set:
			subsequence = [encode(token) for token in q.split()]
			inputs.extend(subsequence[i:i+WINDOW_SIZE] for i in range(len(subsequence) - WINDOW_SIZE)[::step_size])
			outputs.extend(subsequence[WINDOW_SIZE::step_size])

	# reshape each 
	x = np.asarray(inputs)
	x.shape = (np.shape(x)[0:2])
	y = np.asarray(outputs)
	y.shape = (len(y),1)

	INPUT_SIZE = len(x)
	print("len(x): ", INPUT_SIZE)

	np.save(XTENSOR_PATH, x)
	np.save(YTENSOR_PATH, y)

	inputs = None
	outputs = None
	gc.collect()


def save_config():
	config = {
		'window_size': WINDOW_SIZE, 
		'step_size': step_size,
		'vocab_size': VOCAB_SIZE,
		'input_size': INPUT_SIZE,
		}
	with open(CONFIG_PATH, "wb") as c:
		cPickle.dump(config, c)


def main():
	load_encoding()
	encode_text(TRAIN_PATH, WINDOW_SIZE, step_size)
	save_config()
	print("Input Tensor file saved to: %s" % XTENSOR_PATH)


if __name__ == '__main__':
	main()
