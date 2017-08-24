#!/usr/bin/env python

import sys

QUERY_LOG_PATH=sys.argv[1]


def post_pad_lines(max_length, pad_token):
        with open(QUERY_LOG_PATH) as f:
                with open(QUERY_LOG_PATH+'.padded', 'w') as o:
                        for line in f:
                                if len(line.split()) < max_length-1:
                                        padded_line = line.strip()+pad_token*(max_length-len(line.split()))+"\n"
                                        o.write(padded_line)

def pre_pad_lines(fixed_seq_length, pad_token):
        with open(QUERY_LOG_PATH) as f:
                with open(QUERY_LOG_PATH+'.padded', 'w') as o:
                        for line in f:
                        	padded_line = pad_token*fixed_seq_length + line
                        	o.write(padded_line)


# post_pad_lines(201, " ?")

pre_pad_lines(20, "? ")

