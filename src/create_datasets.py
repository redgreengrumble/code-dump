#!/usr/bin/env python
# Usage:
# ./create_datasets.py --corpus dataset.txt --dilute 80 -v 3600

from __future__ import print_function
import random
from argparse import ArgumentParser
import datetime
import os, gc, collections
from six.moves import cPickle

parser = ArgumentParser()
parser.add_argument("-d", "--dilute")
parser.add_argument("-c", "--corpus")
parser.add_argument("-v", "--vocab_size", type=int)
args = parser.parse_args()

CORPUS_PATH = args.corpus
DILUTION_RATE = float(args.dilute)

ts = datetime.datetime.now().strftime("%H%M")
DATA_DIR = os.path.join(os.getcwd(), "data/T.%s_D.%s" % (ts, args.dilute))

if os.path.exists(DATA_DIR):
	os.system("rm -rf %s" % DATA_DIR)
# os.mkdir(DATA_DIR)
os.makedirs(DATA_DIR)

TRAIN_PATH = os.path.join(DATA_DIR, "train.txt")
TEST_PATH = os.path.join(DATA_DIR, "test.txt")
VALID_PATH = os.path.join(DATA_DIR, "valid.txt")
VOCAB_PATH = os.path.join(DATA_DIR, 'vocab.pkl')

def create_dataset():
	infile=CORPUS_PATH
	# outfile=os.path.join(DATA_DIR, "corpus."+str(args.dilute)+".sample")
	valid_file = open(VALID_PATH, "w")
	train_file = open(TRAIN_PATH, "w")
	test_file = open(TEST_PATH, "w")

	line_count = { "valid": 0, "test": 0, "train": 0 }
	
	word_counter = collections.Counter([])

	with open(infile) as f:
		for line in f:
			rv = random.random()*100
			if rv < DILUTION_RATE:
				x = random.random()*100
				if x < 10: # 10% of set for validation
					valid_file.write(line)
					line_count['valid']+=1
				elif x < 30: # 20% of set for testing
					test_file.write(line)
					line_count['test']+=1
				else: # 70% of set for training
					train_file.write(line)
					word_counter.update(line.split())
					line_count['train']+=1
	
	valid_file.close()
	train_file.close()
	test_file.close()


	words = [x[0] for x in word_counter.most_common(args.vocab_size)]

	with open(VOCAB_PATH, 'wb') as d:
		cPickle.dump(words, d)

	print("Train set vocab size: "+str(len(words)))
	print("# of queries:", line_count)
	print("Wrote train set to:"+TRAIN_PATH)

	word_counter = None
  	words = None

	gc.collect()


def main():
	create_dataset()

if __name__ == '__main__':
	main()
