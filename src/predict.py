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

DATA_DIR = os.path.join(os.getcwd(), "data/T.%s_D.%s_E.%s" % (ts, dilute, epochs))
ENCODING_MAP_PATH = os.path.join(DATA_DIR, 'encoding_map.json')
DECODING_MAP_PATH = os.path.join(DATA_DIR, 'decoding_map.json')

END_TOKEN = '<EOQ>'

# function that uses trained model to predict a desired number of future tokens
def predict_next_tokens(model, input_tokens, num_to_predict):     
    # create output
    word_to_id = load_encoding(ENCODING_MAP_PATH)
    id_to_word = load_decoding(DECODING_MAP_PATH)
    predicted_token_ids = []
    predicted_tokens = []
    for i in range(num_to_predict):
        # convert this round's predicted tokens to numerical input    
        x_test = np.zeros((1, window_size, vocab_size))
        for t, token in enumerate(input_tokens):
            x_test[0, t, word_to_id[token]] = 1.

        # make this round's prediction
        predictions = model.predict(x_test, verbose=0)[0]
        # print("np.shape(predictions):", np.shape(predictions)) = (3298,)

        # predict class of each test input
        r = np.argmax(predictions)
        # print("r:", r)

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
        print("top matches:", map(lambda x: (id_to_word[str(x)], predictions[x]*-1), rs))
        print("------------------------")

        # translate numerical prediction back to token
        d = id_to_word[str(r)]
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
    predicted_tokens = predict_next_tokens(model, input_tokens=args.prefix.split(" "), num_to_predict=args.num_predicted)
    print(args.prefix+" "+" ".join(predicted_tokens))
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
