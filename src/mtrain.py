#!/usr/bin/env python
# Usage:
# ./mtrain.py --corpus /Users/ericmanzi/Desktop/sqlact/query_dataset/queries_unique_87k.txt --dilute 30 --epochs 30

from __future__ import print_function
import numpy as np
import tensorflow as tf
import random, collections
import sys, os, subprocess
from argparse import ArgumentParser
import datetime
from utils import *
import gc
# import json



debug = False

WINDOW_SIZE = 4
step_size = 1

TRAIN_SIZE = 0.7
TEST_SIZE = 0.2
VALID_SIZE = 0.1

parser = ArgumentParser()
parser.add_argument("-c", "--corpus")
parser.add_argument("-d", "--dilute")
parser.add_argument("-e", "--epochs")
args = parser.parse_args()

CORPUS_PATH = args.corpus
DILUTION_RATE = float(args.dilute)/100
NUM_EPOCHS = int(args.epochs)

ts = datetime.datetime.now().strftime("%H%M")
DATA_DIR = os.path.join(os.getcwd(), "data/T.%s_D.%s_E.%s" % (ts, args.dilute, args.epochs))
TRAIN_PATH = os.path.join(DATA_DIR, "train.txt")
TEST_PATH = os.path.join(DATA_DIR, "test.txt")
VALID_PATH = os.path.join(DATA_DIR, "valid.txt")
ENCODING_MAP_PATH = os.path.join(DATA_DIR, 'encoding_map.json')
DECODING_MAP_PATH = os.path.join(DATA_DIR, 'decoding_map.json')

VOCAB_SIZE = 0


def transform_text_to_io(train_path, WINDOW_SIZE, step_size):
	inputs = []
	outputs = []
	with open(train_path) as train_set:
		for q in train_set:
			subsequence = q.split()
			inputs.extend(subsequence[i:i+WINDOW_SIZE] for i in range(len(subsequence) - WINDOW_SIZE)[::step_size])
			outputs.extend(subsequence[WINDOW_SIZE::step_size])

	# reshape each 
	x = np.asarray(inputs)
	inputs = None
	x.shape = (np.shape(x)[0:2])
	y = np.asarray(outputs)
	outputs = None
	y.shape = (len(y),1)
	gc.collect()
	return x, y


def encode_io(train_path,WINDOW_SIZE,step_size):    
    
    # cut up text into character input/output pairs
    inputs, outputs = transform_text_to_io(train_path,WINDOW_SIZE,step_size)
    input_size = len(inputs)
    print("len(inputs) ",input_size)
    # print("len(outputs) ",len(outputs))
    # create empty vessels for one-hot encoded input/output
    # x = np.zeros((input_size, WINDOW_SIZE, VOCAB_SIZE), dtype=np.int32)
    # y = np.zeros((input_size, VOCAB_SIZE), dtype=np.int32)

    # print("gc.get_stats:", gc.get_stats())
    # print("gc.garbage:", gc.garbage)
    gc.collect()
    # print("gc.get_stats:", gc.get_stats())
    # print("gc.garbage:", gc.garbage)

    x = np.zeros((input_size, WINDOW_SIZE, VOCAB_SIZE), dtype=np.bool)
    y = np.zeros((input_size, VOCAB_SIZE), dtype=np.bool)

    # peek(inputs, outputs)

    word_to_id = load_encoding(ENCODING_MAP_PATH)
    # loop over inputs/outputs and tranform and store in x/y
    for i, statement in enumerate(inputs):
        for t, token in enumerate(statement):
            x[i, t, word_to_id[token]] = 1
        y[i, word_to_id[outputs[i][0]]] = 1
    inputs = None
    outputs = None
    gc.collect()
    return x,y


def peek(x, y):
	# print out input/output pairs --> here input = x, corresponding output = y
	print('the shape of x is ' + str(np.shape(x)))
	print('the shape of y is ' + str(np.shape(y)))
	print('the type of x is ' + str(type(x)))
	print('the type of y is ' + str(type(y)))

	print('x[0][0] = ', x[0][0])
	print('y[0][0] = ', y[0])
	print('-----')
	print('x[2] = ', x[2])
	print('y[2] = ', y[2])
	print('-----')
	print('x[10] = ', x[10])
	print('y[10] = ', y[10])
	print('--------------')

def dilute_dataset(dilution_rate):
	infile=CORPUS_PATH
	outfile=os.path.join(DATA_DIR, "corpus."+str(args.dilute)+".sample")

	with open(infile) as f:
		with open(outfile, 'w') as o:
			# selected = random.sample(f.readlines(), sample_size)
			for line in f:
				rv = random.random()
				if rv < dilution_rate:
					o.write(line)

	print("Wrote sample to:"+outfile)
	return outfile


def create_datasets(corpus_path):
	valid_file = open(VALID_PATH, "w")
	train_file = open(TRAIN_PATH, "w")
	test_file = open(TEST_PATH, "w")
	# vocab = set()
	line_count = { "valid": 0, "test": 0, "train": 0 }

	with open(corpus_path) as corpus:
		for line in corpus:
			rv = random.random()
			if rv < 0.1: # 10% of set for validation
				valid_file.write(line)
				line_count['valid']+=1
			elif rv < 0.3: # 20% of set for testing
				test_file.write(line)
				line_count['test']+=1
			else: # 70% of set for training
				# vocab.update(line.split())
				train_file.write(line)
				line_count['train']+=1

	valid_file.close()
	train_file.close()
	test_file.close()
	print("# of queries:", line_count)
	gc.collect()


def build_vocab():
	global VOCAB_SIZE
	counter = collections.Counter([])
  	with open(TRAIN_PATH) as f:
  		for line in f:
  			counter.update(line.split())
  	count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
  	words, _ = list(zip(*count_pairs))
  	word_to_id = dict(zip(words, range(len(words))))
  	with open(ENCODING_MAP_PATH, 'w') as e:
  		json.dump(word_to_id, e)

  	# id_to_word = dict((i, c) for i, c in enumerate(word_to_id))
  	id_to_word = dict((v, k) for k, v in word_to_id.iteritems())
  	with open(DECODING_MAP_PATH, 'w') as d:
  		json.dump(id_to_word, d)

  	VOCAB_SIZE = len(words)
  	print("Train set vocab size:"+str(VOCAB_SIZE))

  	#cleanup
  	counter = None
  	count_pairs = None
  	words = None
  	_ = None
  	word_to_id = None
  	id_to_word = None
  	gc.collect()





def prepare_data():
	if os.path.exists(DATA_DIR):
		os.system("rm -rf %s" % DATA_DIR)
	os.mkdir(DATA_DIR)

	outfile = dilute_dataset(DILUTION_RATE)
	create_datasets(outfile)
	build_vocab()

	x,y = encode_io(TRAIN_PATH, WINDOW_SIZE, step_size)
	gc.collect()
	return x, y



def main():
	x,y = prepare_data()
	model = build_model(WINDOW_SIZE,VOCAB_SIZE)

	# train the model
	model.fit(x, y, batch_size=200, epochs=NUM_EPOCHS, verbose=1)

	stamp = 'T.%s_D.%s_V.%d_W.%d_E.%d' % (ts, args.dilute, VOCAB_SIZE, WINDOW_SIZE, NUM_EPOCHS)
	WEIGHTS_PATH = os.path.join(os.getcwd(), 'results/weights/%s.hdf5' % stamp)

	model.save_weights(WEIGHTS_PATH)


if __name__ == '__main__':
	main()
	gc.collect()