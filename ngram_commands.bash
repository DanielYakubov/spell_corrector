#!usr/bin/env python3
set -eou pipefail

ngramsymbols 2021_preprocessed.txt en.sym
farcompilestrings --fst_type=compact --symbols=en.sym --keep_symbols 2021_preprocessed.txt 2021_preprocessed.far
ngramcount --order=3 2021_preprocessed.far 2021.cnt