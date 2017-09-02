#!/usr/bin/env python3

import sys, os
# import cPickle
import _pickle as cPickle
import gc
from sys import stdout
import lzma


TRIGRAM = None
SINGLE_WORD_ENCODING = None
WORD_PAIR_ENCODING = None
SINGLE_WORD_DECODING = None
WORD_PAIR_DECODING = None

TRIGRAMDICT_OUTFILE = "results/trigram_dict.pkl.xz"
VOCAB_OUTFILE = "results/trigram_vocab.pkl.xz"
RESULTS_DIR = "results"

def gen_trigram(train_set):
	import subprocess, collections, time
	output = subprocess.check_output("wc -l %s" % train_set, shell=True)
	numlines = int(output.split()[0])*2
	start_time = time.time()

	single_word_counter = collections.Counter([])
	word_pair_counter = collections.Counter([])

	with open(train_set) as f:
		chkpt = 0
		last_chkpt = 0
		for line in f:
			tokens = line.split()
			single_word_counter.update(tokens)
			bituple = list(zip(tokens, tokens[1:]))
			word_pair_counter.update(bituple)

			chkpt += 1
			if chkpt - last_chkpt == 1000:
				last_chkpt = chkpt
				stdout.write("\r%d/%d lines counted" % (chkpt, numlines))
				stdout.flush()
	stdout.write("\n")

	single_words = [x[0] for x in single_word_counter.most_common()]
	word_pairs = [x[0] for x in word_pair_counter.most_common()]
	V1 = len(single_words)
	V2 = len(word_pairs)
	single_word_encoding = dict(zip(single_words, range(V1)))
	word_pair_encoding = dict(zip(word_pairs, range(V2)))

	trigram = dict()
	with open(train_set) as f:
		c = chkpt
		c_prev = chkpt
		for line in f:
			tokens = line.split()
			trituple = list(zip(tokens, tokens[1:], tokens[2:]))
			for t1, t2, t3 in trituple:
				trikey = word_pair_encoding[(t1,t2)]
				trival = single_word_encoding[t3]
				if trikey not in trigram:
					trigram[trikey] = {}
				if trival not in trigram[trikey]:
					trigram[trikey][trival] = 0
				trigram[trikey][trival]+=1

			c+=1
			if c - c_prev == 1000:
				c_prev = c
				stdout.write("\r%d/%d lines processed" % (c, numlines))
				stdout.flush()
	stdout.write("\n")


	from sys import getsizeof
	print("trigram size: %f MB" % (getsizeof(trigram)/1000000.0))
	print("Runtime: %ds" % int(time.time()-start_time))
	print("single word vocab size: %d (%f MB)" % (len(single_words), getsizeof(single_words)/1000000.0))
	print("word pair vocab size: %d (%f MB)" % (len(word_pairs), getsizeof(word_pairs)/1000000.0))

	save_trigram(trigram, single_words, word_pairs)

	gc.collect()
	return


def save_trigram(trigram, single_words, word_pairs):
	if not os.path.exists(RESULTS_DIR):
		os.mkdir(RESULTS_DIR)

	with lzma.open(TRIGRAMDICT_OUTFILE, "w") as d:
		cPickle.dump(trigram, d)
	with lzma.open(VOCAB_OUTFILE, "w") as v:
		cPickle.dump({'single_words':single_words,'word_pairs':word_pairs}, v)



def load_trigram():
	global TRIGRAM, SINGLE_WORD_DECODING, WORD_PAIR_DECODING
	with lzma.open(TRIGRAMDICT_OUTFILE+'.'+compression) as d:
		TRIGRAM = cPickle.load(d)
	with lzma.open(VOCAB_OUTFILE) as v:
		vocab = cPickle.load(v)
		SINGLE_WORD_DECODING=vocab['single_words']
		WORD_PAIR_DECODING=vocab['word_pairs']
		vocab = None
	gc.collect()

	SINGLE_WORD_ENCODING = dict(zip(single_words, range(len(SINGLE_WORD_DECODING))))
	WORD_PAIR_ENCODING = dict(zip(word_pairs, range(len(WORD_PAIR_DECODING))))




def predict_next(context, n):
	lookup_key = WORD_PAIR_DECODING[tuple(context.split()[:2])]





def main():
	# if not os.path.exists(TRIGRAMDICT_OUTFILE):
	infile = sys.argv[1]
	gen_trigram(infile)

	# load_trigram()
	# predict_next("s.dec <", 5)



if __name__ == '__main__':
	main()