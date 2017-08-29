#!/usr/bin/env python
import sys
import cPickle
import collections

#infile="unique.dataset.val.txt.VALARG.padded.280052"
infile = sys.argv[1]

with open(infile) as f:
	word_counter = collections.Counter([])
	for line in f:
		word_counter.update(line.split())
	words = [x[0] for x in word_counter.most_common()]                                                                                                                           
	print len(words)
	with open("vocab.pkl", 'wb') as d:                                                                                                                                    
		cPickle.dump(words, d)
