#!/usr/bin/env python
# Usage:
# ./predict.py -m results/weights/T.1604_D.5_V.3298_W.4.hdf5 -x "<SOQ> SELECT <W> FROM" -n 2
# ./src/predict.py -m results/weights/T.1604_D.50_V.7477_W.4_E.50.hdf5 -x "<SOQ> SELECT <W> FROM" -n 5
from __future__ import print_function
import numpy as np
import random, collections, json
import sys, os, subprocess
from argparse import ArgumentParser
from utils import *


import os, gc, collections
from argparse import ArgumentParser
import numpy as np
from six.moves import cPickle
import json


parser = ArgumentParser()
parser.add_argument("-m", "--model", default="results/weights/T.1604_D.5_V.3298_W.4_E.100.hdf5")
parser.add_argument("-x", "--prefix")
parser.add_argument("-n", "--num_predicted", type=int, default=4)
args = parser.parse_args()

input_prefix = args.prefix
model_path = args.model

params = dict(map(lambda x: tuple(x.split(".")[:2]), model_path.split("/")[-1].split("_")))
ts = params['T']
dilute = params['D']
epochs = params['E']
window_size = int(params['W'])
vocab_size = int(params['V'])


# DATA_DIR = os.path.join(os.getcwd(), "data/T.%s_D.%s_E.%s" % (ts, dilute, epochs))
# ENCODING_MAP_PATH = os.path.join(DATA_DIR, 'encoding_map.json')
# DECODING_MAP_PATH = os.path.join(DATA_DIR, 'decoding_map.json')

DATA_DIR = os.path.join(os.getcwd(), "data/T.%s_D.%s" % (ts, dilute))
# TRAIN_PATH = os.path.join(DATA_DIR, 'train.txt')
VOCAB_PATH = os.path.join(DATA_DIR, 'vocab.pkl')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.pkl')

SEQ_LENGTH = 20
END_TOKEN = '<EOQ>'
UNK_TOKEN = '<EOQ>'
PAD_TOKEN = "?"

OMIT_TOKENS = ["<EOQ>", "<SOQ>"]
FORMAT_TOKENS = ["<W>"]
REPLACE_TOKENS = ["<VAL>", "<ARG>", "<UNK>"]



PENTAGRAM_FILE = 'ngrams/results/pentagram_dict.pkl'
pentagram = load_pentagram(PENTAGRAM_FILE)


def load_encoding():
    with open(VOCAB_PATH, 'rb') as f:
        words = cPickle.load(f)
    VOCAB_SIZE = len(words)
    encoding = dict(zip(words, range(VOCAB_SIZE)))
    return encoding, words


def ngram_predict_next(context, n):
    return sorted(list(pentagram[context].iteritems()), key=lambda x: (-x[1], x[0]))[:n]

# function that uses trained model to predict a desired number of future tokens
def predict_next_tokens(model, input_tokens, num_to_predict, ngram_assist=False):     
    # create output
    # word_to_id = load_encoding(ENCODING_MAP_PATH)
    # id_to_word = load_decoding(DECODING_MAP_PATH)
    word_to_id, id_to_word = load_encoding()
    # id_to_word = 
    predicted_token_ids = []
    predicted_tokens = []

    replace_token_ids = map(lambda x: word_to_id[x], REPLACE_TOKENS)


    # Append pad tokens
    input_tokens = ([PAD_TOKEN]*(SEQ_LENGTH - len(input_tokens))) + input_tokens

    for i in range(num_to_predict):
        # convert this round's predicted tokens to numerical input    
        x_test = np.zeros((1, window_size, vocab_size))
        for t, token in enumerate(input_tokens):
            if token not in word_to_id:
                token = UNK_TOKEN
            x_test[0, t, word_to_id[token]] = 1.
            # print("word_to_id[%s]=%d" % (token, word_to_id[token]))
            # print("id_to_word[%d]=%s" % (word_to_id[token], id_to_word[word_to_id[token]]))
        # make this round's prediction
        predictions = model.predict(x_test, verbose=0)[0]
        # print("np.shape(predictions):", np.shape(predictions)) = (3298,)

        # predict class of each test input
        r = np.argmax(predictions)
        # print("r:", r)

        substitutions = []
        context=tuple(input_tokens[-4:])
        # print("context: "+str(context))
        
        if r in replace_token_ids: # Check if "<VAL>", "<ARG>", "<UNK>"
            # print("special token: "+id_to_word[r])
            if context in pentagram:
                # do the thing
                substitutions = filter(lambda s: s not in REPLACE_TOKENS, ngram_predict_next(context, 5))
            else:
                print("context: "+str(context)+" not in pentagram")

        if ngram_assist and len(substitutions) > 0:
            print("----------------------")
            print("5-GRAM(%s): %s"%(str(context), pentagram[context] if context in pentagram else "NO ENTRY" ))
            print("ngram_predict_next(%s): %s"%(str(context), str(ngram_predict_next(context, 5))))
            print("substitutions: "+str(substitutions))
            print("replacing special token: "+id_to_word[r]+" with "+substitutions[0][0])
            r = word_to_id[substitutions[0][0]] if substitutions[0][0] in word_to_id else r


        # peek runner ups
        rs=[r]
        rn=r
        dbg = ""
        while len(rs) < 5:
            predictions[rn] *= -1
            rn=np.argmax(predictions)

            if rn not in rs:
                rs.append(rn)
            else:
                dbg += " rn seen. %d |" % rn
        # print("top matches:", map(lambda x: (id_to_word[x], predictions[x]*-1), rs))
        # print("------------------------")

        # translate numerical prediction back to token
        d = id_to_word[r]
        # update predicted_tokens
        predicted_tokens.append(d)

        if d == END_TOKEN:
            break

        # update input
        input_tokens.append(d)
        input_tokens = input_tokens[1:]
        predicted_token_ids = predicted_token_ids[1:]

    return predicted_tokens



def load_model(model_path):
	model = build_model(window_size, vocab_size)
	model.load_weights(model_path)
	return model

def main():
    # print("args.prefix:", args.prefix)
    model = load_model(model_path)
    predicted_tokens = predict_next_tokens(model, input_tokens=args.prefix.split(), num_to_predict=args.num_predicted)
    print("no ngram: "+args.prefix+" "+" ".join(predicted_tokens))
    predicted_tokens = predict_next_tokens(model, input_tokens=args.prefix.split(), num_to_predict=args.num_predicted, ngram_assist=True)
    print("W/ ngram: "+args.prefix+" "+" ".join(predicted_tokens))
    model = None
    
    

if __name__ == '__main__':
    try:
        from keras import backend as K
        with K.get_session():
            main()
            import gc
            gc.collect()
    except AttributeError as e:
        pass
