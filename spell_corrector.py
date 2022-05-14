import pynini
import string
import nltk
import re

from typing import List
from preprocessing import remove_numbers_and_links, separate_by_tok, has_weird_characters
from pynini.lib import edit_transducer


class SpellCorrector(object):

    def __init__(self, sigma_string, sym_file, lm_file):
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

        ET = edit_transducer.EditTransducer(pynini.escape(self.sigma_string),
                                            bound=bound) # COULD BE A PROBLEM HERE
        candidates_lattice = ET.create_lattice(pynini.escape(token), self.sigma_star).optimize()
        candidates = candidates_lattice.paths().ostrings()
        valid_candidates = [pynini.accep(c, token_type=self.sym) for c in candidates
                            if self.sym.member(c)]
        return pynini.union(*valid_candidates).optimize()

    def make_lattice(self, tokens: List) -> pynini.Fst:
        tokens = [pynini.accep(token, token_type=self.sym) for token in tokens]
        confusion_sentences = []
        for i, tok in enumerate(tokens):
            one_confusion_set_sent = tokens.copy()
            one_confusion_set_sent[i] = self._make_subsausage(tok)
            sent = pynini.accep('', token_type=self.sym)
            for fst in one_confusion_set_sent:
                sent = sent + fst
            confusion_sentences.append(sent)
        return (pynini.union(*confusion_sentences) @ self.lm).optimize()

    def best_sentence(self, sentence: str) -> str:
        assert not has_weird_characters(sentence), \
            "The sentence contains characters not present in Sigma Star"
        sentence = sentence.lower()
        sentence = remove_numbers_and_links(sentence)
        # special case
        if " 1 " in sentence:
            sentence = re.sub(" 1 ", " one ", sentence)
        toks = nltk.word_tokenize(sentence)
        poss_sent_fst = self.make_lattice(toks)
        return pynini.shortestpath(poss_sent_fst).string(token_type=self.sym)


if __name__ == '__main__':
    SpellCorrector()