#!/usr/bin/env python

from __future__ import print_function
import sys, os
import cPickle
# import _pickle as cPickle
import gc
from sys import stdout
# import lzma
# import gzip

PENTAGRAM = None
# SINGLE_WORD_ENCODING = None
# QUAD_WORD_ENCODING = None
# SINGLE_WORD_DECODING = None
# QUAD_WORD_DECODING = None

PENTAGRAMDICT_OUTFILE = "results/pentagram_dict.pkl"
# VOCAB_OUTFILE = "results/pentagram_vocab.pkl"
RESULTS_DIR = "results"

def gen_pentagram(train_set):
	import subprocess, collections, time
	output = subprocess.check_output("wc -l %s" % train_set, shell=True)
	numlines = int(output.split()[0])*2
	start_time = time.time()

	# single_word_counter = collections.Counter([])
	# quad_word_counter = collections.Counter([])

	# with open(train_set) as f:
	# 	chkpt = 0
	# 	last_chkpt = 0
	# 	for line in f:
	# 		tokens = line.split()
	# 		if len(tokens) < 5:
	# 			continue
	# 		single_word_counter.update(tokens)
	# 		quadtuple = list(zip(tokens, tokens[1:], tokens[2:], tokens[3:]))
	# 		quad_word_counter.update(quadtuple)

	# 		chkpt += 1
	# 		if chkpt - last_chkpt == 1000:
	# 			last_chkpt = chkpt
	# 			stdout.write("\r%d/%d lines counted" % (chkpt, numlines))
	# 			stdout.flush()
	# stdout.write("\n")

	# single_words = [x[0] for x in single_word_counter.most_common()]
	# quad_words = [x[0] for x in quad_word_counter.most_common()]
	# V1 = len(single_words)
	# V4 = len(quad_words)
	# single_word_encoding = dict(zip(single_words, range(V1)))
	# quad_word_encoding = dict(zip(quad_words, range(V4)))

	PENTAGRAM = dict()
	with open(train_set) as f:
		c = chkpt
		c_prev = chkpt
		for line in f:
			tokens = line.split()
			pentuple = list(zip(tokens, tokens[1:], tokens[2:], tokens[3:], tokens[4:]))
			for t1, t2, t3, t4, t5 in pentuple:
				# pentkey = quad_word_encoding[(t1,t2,t3,t4)]
				# pentval = single_word_encoding[t5]
				pentkey = (t1,t2,t3,t4)
				pentval = t5
				if pentkey not in PENTAGRAM:
					PENTAGRAM[pentkey] = {}
				if pentval not in PENTAGRAM[pentkey]:
					PENTAGRAM[pentkey][pentval] = 0
				PENTAGRAM[pentkey][pentval]+=1

			c+=1
			if c - c_prev == 1000:
				c_prev = c
				stdout.write("\r%d/%d lines processed" % (c, numlines))
				stdout.flush()
	stdout.write("\n")


	from sys import getsizeof
	print("PENTAGRAM size: %f MB" % (getsizeof(PENTAGRAM)/1000000.0))
	print("Runtime: %ds" % int(time.time()-start_time))
	# print("single word vocab size: %d (%f MB)" % (len(single_words), getsizeof(single_words)/1000000.0))
	# print("4 word vocab size: %d (%f MB)" % (len(quad_words), getsizeof(quad_words)/1000000.0))

	save_PENTAGRAM(PENTAGRAM)

	gc.collect()
	return


def save_PENTAGRAM(PENTAGRAM, single_words=None, quad_words=None):
	if not os.path.exists(RESULTS_DIR):
		os.mkdir(RESULTS_DIR)

	with open(PENTAGRAMDICT_OUTFILE, "w") as d:
		cPickle.dump(PENTAGRAM, d)
		
	# with gzip.GzipFile(PENTAGRAMDICT_OUTFILE, "w") as d:
		# cPickle.dump(PENTAGRAM, d)
	# with gzip.GzipFile(VOCAB_OUTFILE, "w") as v:
		# cPickle.dump({'single_words':single_words,'quad_words':quad_words}, v)



def load_PENTAGRAM():
	global PENTAGRAM, SINGLE_WORD_DECODING, QUAD_WORD_DECODING
	with gzip.GzipFile(PENTAGRAMDICT_OUTFILE+'.'+compression) as d:
		PENTAGRAM = cPickle.load(d)
	with gzip.GzipFile(VOCAB_OUTFILE) as v:
		vocab = cPickle.load(v)
		SINGLE_WORD_DECODING=vocab['single_words']
		QUAD_WORD_DECODING=vocab['quad_words']
		vocab = None
	gc.collect()

	SINGLE_WORD_ENCODING = dict(zip(single_words, range(len(SINGLE_WORD_DECODING))))
	QUAD_WORD_ENCODING = dict(zip(quad_words, range(len(QUAD_WORD_DECODING))))




def predict_next(context, n):
	lookup_key = QUAD_WORD_DECODING[tuple(context.split()[:2])]





def main():
	infile = sys.argv[1]
	gen_pentagram(infile)

	# load_pentagram()
	# predict_next("s.dec <", 5)



if __name__ == '__main__':
	main()