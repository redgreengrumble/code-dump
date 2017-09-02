#!/usr/bin/env python
# validator.py -q dataset.unique.val.txt

import re
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-q", "--queryfile", help="Path to input file")
args = parser.parse_args()
import sqlparser

q="../sync_mtext_gen/dataset.unique.val.txt"

with open(args.queryfile) as f:
    validset=[]
    invalidset=[]
    parser = sqlparser.Parser()
    for line in f:
		line = r'<VAL>'.sub("10", line)
		line = r'<ARG>'.sub("10", line)
		line = r'<UNK>'.sub("x", line)

		if parser.check_syntax(line) == 0:
			validset.append(line)
		else:
			invalidset.append(line)

print "Valid:" % len(validset)
print "Invalid:" % len(invalidset)


with open(args.queryfile+".valid", "w") as v:
	v.writelines(validset)
with open(args.queryfile+".invalid", "w") as v:
	v.writelines(invalidset)

