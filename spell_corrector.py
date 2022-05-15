import pynini
import string
import csv
import nltk
import re

from typing import List
from preprocessing import remove_numbers_and_links, separate_by_tok, has_weird_characters
from pynini.lib import edit_transducer

SPANISH_ALPHABET = 'ùewàgkclëfusìòbáixúzanhtjïmîoórñíþqdvpéèy'
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
                self.sym.add_symbol(token) # prevent a composition failure
            token_fsts.append(pynini.accep(token, token_type=self.sym))

        confusion_sentences = []
        for i, tok in enumerate(tokens):
            one_confusion_set_sent = token_fsts.copy()
            if tok not in string.punctuation and tok[-1] not in string.punctuation\
                    and tok[0] not in string.punctuation and \
                    tok not in ['LINK', 'NUM']: # not trying to correct punctuation, only words
                one_confusion_set_sent[i] = self._make_subsausage(tok)
            sent = pynini.accep('', token_type=self.sym)
            for fst in one_confusion_set_sent:
                sent = sent + fst
            confusion_sentences.append(sent.optimize())
        return (pynini.union(*confusion_sentences) @ self.lm).optimize()

    def best_sentence(self, sentence: str) -> str:
        assert not has_weird_characters(sentence), \
            "The sentence contains characters not present in Sigma Star"
        sentence = sentence.lower()
        sentence = remove_numbers_and_links(sentence)
        # special case
        sentence = re.sub("^1| 1 ", " one ", sentence)
        toks = nltk.word_tokenize(sentence)
        poss_sent_fst = self.make_lattice(toks)
        if poss_sent_fst.start() == -1:
            return sentence # this means the lattice was empty, everything was OOV or punct
        return pynini.shortestpath(poss_sent_fst).string(token_type=self.sym)


if __name__ == '__main__':
    word_punct = "'-`"
    en_alpha = string.ascii_letters
    en_sp = SpellCorrector(string.ascii_lowercase + word_punct, 'en/en.sym', 'en/en_smaller.lm')
    print(en_sp.best_sentence("that spy received us all!"))
    # with open('eng_typos.tsv', 'r') as en_typos:
    #     tsv_reader = csv.reader(en_typos, delimiter='\t')
    #     for row in tsv_reader:
    #         print(row[1], en_sp.best_sentence(row[1]))