#!usr/bin/env python

import nltk
import re
from string import printable


def separate_by_tok(line):
    return ' '.join(nltk.word_tokenize(line))


def remove_numbers_and_links(line):
    line = re.sub(r'\d+', 'NUM', line)
    line = re.sub(r'https:\/\/\S+', 'LINK', line)
    return re.sub('www\.\S+', 'LINK', line) # getting the stragglers from line 12


# from https://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters
def has_weird_characters(line):
    return bool(set(line) - set(printable))


def preprocess(output_file, *args):
    with open(output_file, 'w') as dump:
        for input_file in args:
            with open(input_file, 'r') as data:
                # we don't want numbers, newlines, upper case, or links
                # quotation marks and commas are being left, as they are meaningful separators
                for line in data:
                    line = line.lower()
                    line = remove_numbers_and_links(line.rstrip())
                   # if not has_weird_characters(line):
                    print(separate_by_tok(line), file=dump)


if __name__ == "__main__":
    preprocess('ru/ru_cleaned', 'ru/ru_2016')
