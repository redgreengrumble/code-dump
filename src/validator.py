#!/usr/bin/env python
# validator.py -q dataset.unique.val.txt

import re
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-q", "--queryfile", help="Path to input file")
args = parser.parse_args()
import sqlparser

q="../sync_mtext_gen/dataset.unique.val.txt"

delimiter = re.compile('(<SOQ> | <EOQ>)')
valarg_regex = re.compile('(<VAL>|<ARG>)')
# arg_regex = re.compile('<ARG>')
unk_regex = re.compile('<UNK>')


with open(args.queryfile) as f:
    validset=[]
    invalidset=[]
    parser = sqlparser.Parser()
    for line in f:
		line = re.sub(valarg_regex, "10", line)
		# line = re.sub(arg_regex, "10", line)
		line = re.sub(unk_regex, "x", line)
		line = re.sub(delimiter, "", line)

		if parser.check_syntax(line) == 0:
			validset.append(line)
		else:
			invalidset.append(line)

print "Valid:%d" % len(validset)
print "Invalid:%d" % len(invalidset)


with open(args.queryfile+".valid", "w") as v:
	v.writelines(validset)
with open(args.queryfile+".invalid", "w") as v:
	v.writelines(invalidset)

