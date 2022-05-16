import pynini
import pandas as pd
import string
import csv
import nltk
import re

from typing import List
from preprocessing import remove_numbers_and_links, separate_by_tok, has_weird_characters
from pynini.lib import edit_transducer

SPANISH_ALPHABET = 'ewgkclfusbáixúzanhtjmoórñíþqdvpéyü'
SPANISH_PUNCT = '¿¡'
RUSSIAN_ALPHABET = 'цуьфекдгмйтчспхювщонъжэяёирлбазш'


class SpellCorrector(object):

    def __init__(self, sigma_string, sym_file, lm_file):
        self.symbols_not_words = string.punctuation
        self.sigma_string = sigma_string
        self.sigma_star = pynini.union(*sigma_string).star
        self.sym = pynini.SymbolTable.read_text(sym_file)
        self.lm = pynini.Fst.read(lm_file)

    def _make_subsausage(self, token: str) -> pynini.Fst:

        if 'NUM' in token or 'LINK' in token:
            return token

        tok_len = len(token)
        if tok_len <= 4:
            bound = 1
        elif tok_len <= 8:
            bound = 2
        else:
            bound = 3

        token = pynini.escape(token)
        ET = edit_transducer.EditTransducer(self.sigma_string,
                                            bound=bound)
        candidates_lattice = ET.create_lattice(token, self.sigma_star).optimize()
        candidates = candidates_lattice.paths().ostrings()
        valid_candidates = [pynini.accep(c, token_type=self.sym) for c in candidates
                            if self.sym.member(c)]
        return pynini.union(*valid_candidates).optimize()

    def make_lattice(self, tokens: List) -> pynini.Fst:
        token_fsts = []
        for token in tokens:
            if not self.sym.member(token):
                self.sym.add_symbol(token)  # prevent a composition failure
            token_fsts.append(pynini.accep(token, token_type=self.sym))

        confusion_sentences = []
        for i, tok in enumerate(tokens):
            one_confusion_set_sent = token_fsts.copy()
            if not set(tok) - set(self.sigma_string) and len(token) < 15:  # can't correct something out of sigma star
                one_confusion_set_sent[i] = self._make_subsausage(tok)
            sent = pynini.accep('', token_type=self.sym)
            for fst in one_confusion_set_sent:
                sent = sent + fst
            confusion_sentences.append(sent.optimize())
        return (pynini.union(*confusion_sentences) @ self.lm).optimize()

    def best_sentence(self, sentence: str) -> str:
        sentence = remove_numbers_and_links(sentence)
        toks = nltk.word_tokenize(sentence)

        cleaned_toks = []
        for tok in toks:
            if 'NUM' in tok or 'LINK' in tok:
                cleaned_toks.append(tok)
            else:
                cleaned_toks.append(tok.casefold())

        poss_sent_fst = self.make_lattice(cleaned_toks)
        if poss_sent_fst.start() == -1:
            return sentence  # this means the lattice was empty, everything was OOV or punct
        return pynini.shortestpath(poss_sent_fst).string(token_type=self.sym)


if __name__ == '__main__':
    word_punct = "'-"

    # en_sp = SpellCorrector(string.ascii_lowercase + word_punct, 'en/en.sym', 'en/en_smaller.lm')
    # en_df = pd.read_csv('en/en_typos.tsv', delimiter='\t', header=0)
    # en_pred = []
    # for i, row in en_df.iterrows():
    #     print(row["corrupted"])
    #     pred = en_sp.best_sentence(row["corrupted"])
    #     print(pred)
    #     en_pred.append(pred)
    # en_df['pred'] = en_pred
    # en_df.to_csv('en/en_typos_pred', sep='\t')

    es_sp = SpellCorrector(SPANISH_ALPHABET + '-', 'es/es.sym', 'es/es_smaller.lm')
    es_df = pd.read_csv('es/es_typos.tsv', delimiter='\t', header=0)
    es_pred = []
    for i, row in es_df.iterrows():
        print(row["corrupted"])
        pred = es_sp.best_sentence(row["corrupted"])
        print(pred)
        es_pred.append(pred)
    es_df['pred'] = es_pred
    es_df.to_csv('es/es_typos_pred', sep='\t')

    ru_sp = SpellCorrector(RUSSIAN_ALPHABET + '-', 'ru/ru.sym', 'ru/ru_smaller.lm')
    ru_df = pd.read_csv('ru/ru_typos.tsv', delimiter='\t', header=0)
    ru_pred = []
    for i, row in ru_df.iterrows():
        print(row["corrupted"])
        pred = ru_sp.best_sentence(row["corrupted"])
        print(pred)
        ru_pred.append(pred)
    ru_df['pred'] = es_pred
    ru_df.to_csv('ru/ru_typos_pred', sep='\t')