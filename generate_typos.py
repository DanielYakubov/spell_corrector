import csv
import random
import string
import nltk
import pynini

from pynini.lib import edit_transducer
from preprocessing import remove_numbers_and_links
from spell_corrector import SPANISH_ALPHABET, SPANISH_PUNCT, RUSSIAN_ALPHABET

class TypoGenerator:
    """generates toy typos, useful for evaluating the spell checker"""
    def __init__(self, sigma_string, extra_punct=''):
        self.disallowed_punct = """!"#$%&()*+,./:;<=>?@[\]^_`{|}~'""" + extra_punct # - might appear word internally
        self.sigma_string = sigma_string
        self.sigma_star = pynini.union(*sigma_string).star

    def make_word_typo(self, token: str) -> str:
        """given a word, randomly switches the letters, if the word contain NUM or link, it is returned"""

        if 'NUM' in token or 'LINK' in token:
            return token

        tok_len = len(token)
        if tok_len <= 4:
            bound = 1
        elif tok_len <= 8:
            bound = 2
        else:
            bound = 3
        print(token)

        token = pynini.escape(token)
        ET = edit_transducer.EditTransducer(self.sigma_string,
                                            bound=bound)
        candidates_lattice = ET.create_lattice(token, self.sigma_star).optimize()
        try:
            candidates = [candidate for candidate in candidates_lattice.paths().ostrings()]
        except:
            return token
        return random.choice(candidates)

    def corrupt_sentence(self, sentence: str) -> str:
        """Corrupts one word in the sentence using the allowed characters in sigma string, if it can't find a viable
        word to corrupt in 3 tries, the original sentence is returned"""
        sentence = remove_numbers_and_links(sentence.lower())
        toks = nltk.word_tokenize(sentence)
        typo_word_index = random.randint(0, len(toks)-1)
        typo_candidate = toks[typo_word_index]

        for tries in range(3):
            if not set(typo_candidate).intersection(set(self.disallowed_punct)) \
            and not set(typo_candidate) - set(self.sigma_string):
                break
            typo_word_index = random.randint(0, len(toks)-1)
            typo_candidate = toks[typo_word_index]
        else:
            return sentence # failsafe, for super rare but possible cases

        if set(typo_candidate).intersection(set(self.disallowed_punct)) \
                or set(typo_candidate) - set(self.sigma_string):
            return sentence

        toks[typo_word_index] = self.make_word_typo(typo_candidate)
        return ' '.join(toks)

    def corrupt_document(self, input_file: str, output_file: str, lines_lim=300) -> None:
        """Given a file path to a text file, writes a tsv file with corrupted versions
        in parallel with gold versions of the sentence"""
        with open(input_file) as gold:
            with open(output_file, 'w') as corrupted:
                tsv_writer = csv.writer(corrupted, delimiter='\t')
                tsv_writer.writerow(['gold', 'corrupted'])
                for i, sentence in enumerate(gold):
                    tsv_writer.writerow([sentence, self.corrupt_sentence(sentence)])
                    print(i)
                    if i == lines_lim:
                        break

if __name__ == '__main__':
    # en_tg = TypoGenerator(string.ascii_lowercase + '-')
    # en_tg.corrupt_document('en/test_en', 'en/en_typos.tsv')

    # sp_tg = TypoGenerator(SPANISH_ALPHABET, extra_punct=SPANISH_PUNCT)
    # sp_tg.corrupt_document('es/test_es', 'es/es_typos.tsv')

    ru_tg = TypoGenerator(RUSSIAN_ALPHABET)
    ru_tg.corrupt_document('ru/test_ru', 'ru/ru_typos.tsv')