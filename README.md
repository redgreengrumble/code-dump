# code-dump

`./src/create_datasets.py --corpus dataset.unique.len100.txt.padded --dilute 20 --vocab_size 3000`
`./src/encode_text.py --data_dir data/T.0914_D.50/ --window_size 20`
`./src/train.py --data_dir data/T.1320_D.40 -e 5`
`./src/predict.py -m results/weights/T.1604_D.5_V.3298_W.4.hdf5 -n 5 -x "<SOQ> SELECT <W> FROM"`
