#!/usr/bin/env python

import datetime
import gc 
import sys

QUERY_LOG_PATH = sys.argv[1]
vocab = {}

def gen_unique_queries():
	global vocab
	unique_set = set()
	outfile = "unique.%s.%s"%(QUERY_LOG_PATH, datetime.datetime.now().strftime("%d%H%M"))
	with open(QUERY_LOG_PATH) as f:
		for line in f:
			unique_set.add(line)
			for token in line.strip().split():
				if token not in vocab:
					vocab[token] = 0
				vocab[token] += 1
	print("Vocab size: %d" % len(vocab.keys()))
	with open(outfile, "w") as o:
		o.writelines(unique_set)
	print("Wrote %d unique queries to %s" % (len(unique_set), outfile))
	unique_set = None
	gc.collect()



def zipfian_distribution(word_count):
	def fmt(w):
		return '\"' + str(w) + '\"'
	cardinality = 100000000
	primer={'token': 'primer', 'frequency': cardinality, 'rank': 0}
	dist=[primer]

	for w in word_count:
		dist.append({'token': fmt(w), 'frequency': word_count[w], 'rank':0})
	
	dist = sorted(dist, key=lambda x: x['frequency'], reverse=True)
	
	for idx, entry in enumerate(dist):
		entry['rank'] = fmt(idx)
		entry['frequency'] = fmt(entry['frequency'])

	fields=['token', 'frequency', 'rank']
	with open('zipfian_distribution.csv', 'w') as outfile:
		writer = csv.DictWriter(outfile, fieldnames=fields)
		writer.writeheader()
		writer.writerows(dist)

	cmd1 = "sed -i .del1 's/token,frequency,rank/\"token\",\"frequency\",\"rank\"/g' zipfian_distribution.csv"
	cmd2 = "sed -i .del2 -E 's/\"+/\"/g' zipfian_distribution.csv"
	clean_temp_files = "rm *.del*"
	import subprocess
	ok = subprocess.check_output(cmd1, shell=True)
	ok = subprocess.check_output(cmd2, shell=True)
	ok = subprocess.check_output(clean_temp_files, shell=True)




gen_unique_queries()

zipfian_distribution(vocab)
