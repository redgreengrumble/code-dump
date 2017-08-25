#!/usr/bin/env python
# 

import sys
import cPickle
from scipy import sparse
import collections
import numpy as np
import gc
from sys import stdout
import subprocess


MTX_OUTFILE = "results/matrix_bigram.pkl"
VOCAB_OUTFILE = "results/vocab.pkl"


GZIP_COMPRESSION = "gzip" # pgz
BZ2_COMPRESSION = "bzip2" # bz2
LZMA_COMPRESSION = "lzma" # xz

CORPUS = None


def gen_bigram_matrix(CORPUS, compression_algo):
	output = subprocess.check_output("wc -l %s" % CORPUS, shell=True)
	numlines = output.split()[0]

	word_counter = collections.Counter([])
	with open(CORPUS) as f:
		chkpt = 0
		last_chkpt = 0
		for line in f:
			word_counter.update(line.split())
			chkpt += 1
			if chkpt - last_chkpt == 1000:
				last_chkpt = chkpt
				stdout.write("\r%d/%s lines processed" % (chkpt, numlines))
				stdout.flush()

	stdout.write("\n")

	words = [x[0] for x in word_counter.most_common()]
	V = len(words)
	encoding = dict(zip(words, range(V)))

	H = sparse.dok_matrix((V, V), dtype='int32')

	with open(CORPUS) as f:
		c = 0
		c_prev = 0
		for line in f:
			tokens = line.split()
			for i in range(len(tokens)-1):
				H[encoding[tokens[i]], encoding[tokens[i+1]]] += 1
			
			c+=1
			if c - c_prev == 1000:
				c_prev = c
				stdout.write("\r%d/%s lines processed" % (c, numlines))
				stdout.flush()
	stdout.write("\n")
	save_bigram(H, words, compression=compression_algo)

def save_bigram(H, words, compression=None):
	# Compression options: gzip, bzip2, lzma

	mode = "wb" if compression is None else "w"

	if compression == GZIP_COMPRESSION:
		import gzip
		matrix_file = gzip.GzipFile(MTX_OUTFILE+'.'+compression, mode)
		vocab_file = gzip.GzipFile(VOCAB_OUTFILE+'.'+compression, mode)
	
	elif compression == BZ2_COMPRESSION:
		import bz2
		matrix_file = bz2.BZ2File(MTX_OUTFILE+'.'+compression, mode)
		vocab_file = bz2.BZ2File(VOCAB_OUTFILE+'.'+compression, mode)

	elif compression == LZMA_COMPRESSION:
		import lzma
		matrix_file = lzma.open(MTX_OUTFILE+'.'+compression, mode)
		vocab_file = lzma.open(VOCAB_OUTFILE+'.'+compression, mode)

	else:
		matrix_file = open(MTX_OUTFILE, mode)
		vocab_file = open(VOCAB_OUTFILE, mode)

	cPickle.dump(H, matrix_file)
	print "Sparse matrix bigram saved to %s.%s" % (MTX_OUTFILE, compression)
	cPickle.dump(words, vocab_file)
	print "Vocab saved to %s.%s" % (VOCAB_OUTFILE, compression)

	matrix_file.close()
	vocab_file.close()


def load_bigram(compression):
	# with lzma.open("file.xz") as f:

	# matrix_file =
	with open(MTX_OUTFILE+'.'+compression) as m:
		H = cPickle.load(m)
	with open(VOCAB_OUTFILE) as v:
		words = cPickle.load(v)


	if compression == GZIP_COMPRESSION:
		import gzip
		matrix_file = gzip.GzipFile(MTX_OUTFILE+'.'+compression)
		vocab_file = gzip.GzipFile(VOCAB_OUTFILE+'.'+compression)
	
	elif compression == BZ2_COMPRESSION:
		import bz2
		matrix_file = bz2.BZ2File(MTX_OUTFILE+'.'+compression)
		vocab_file = bz2.BZ2File(VOCAB_OUTFILE+'.'+compression)

	elif compression == LZMA_COMPRESSION:
		import lzma
		matrix_file = lzma.open(MTX_OUTFILE+'.'+compression)
		vocab_file = lzma.open(VOCAB_OUTFILE+'.'+compression)

	else:
		matrix_file = open(MTX_OUTFILE, mode)
		vocab_file = open(VOCAB_OUTFILE, mode)


	H = cPickle.load(matrix_file)
	words = cPickle.load(vocab_file)

	matrix_file.close()
	vocab_file.close()

	return H, words



def get_bestn(word, n, compression=None):
	H, id_to_word = load_bigram(compression)
	word_to_idx = dict(zip(id_to_word, range(len(id_to_word))))
	r = []
	row = word_to_idx[word]
	print row
	dist = H.getrow(idx).todense()[0]
	# print H.getrow(idx)
	_, cols = H.getrow(idx).nonzero()
	cols = list(cols)
	print cols
	# print H.getrow(idx).todense()
	# print dist
	# print dist[0]

	while len(r) < min(n, len(cols)):
		top_idx = np.argmax(dist)
		print "top_idx:", top_idx
		print "len(dist):", len(dist)
		r.append(id_to_word[top_idx])
		# dist[top_idx] *= -1
		dist[top_idx] = 0

	return r


def main():
	global CORPUS
	CORPUS = sys.argv[1]
	compression_algo = sys.argv[2]
	gen_bigram_matrix(CORPUS, compression_algo)

	# print str(get_bestn("<SOQ>", 5))



if __name__ == '__main__':
	main()