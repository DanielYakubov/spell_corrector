import jsonlines
import re

import csv


def remove_comment_sym_and_html(text: str) -> str:
    """"
    Given a text, removes comment markers and html tags
    """
    return re.sub(r'[*#/]+|:.*:|<.*>|--|]\[|\"\|', '', text).strip()


def create_language_json(typo_corpus, language='eng'):
    """
    Writes a json file with typo pairs using the github typo corpus
    :param typo_corpus: path to the github typo corpus
    :param language: the language to extract typo pairs in
    :return: None, creates a json file
    """
    with jsonlines.open(typo_corpus) as corpus:
        with open(f'{language}_typos.tsv', 'w') as outfile:
            tsv_writer = csv.writer(outfile, delimiter='\t')
            tsv_writer.writerow(['lang', 'src', 'tgt'])
            for line in corpus.iter(type=dict, skip_invalid=True):
                edits = line.get('edits', False)
                for edit in edits:
                    src = edit.get('src', False)
                    tgt = edit.get('tgt', False)
                    is_typo = edit.get('is_typo',
                                       True)  # making the default true, as this key isn't present in all langs

                    if src:
                        src_text = src.get('text', '').strip()
                        src_lang = src.get('lang', None)
                    if tgt:
                        tgt_text = tgt.get('text', '').strip()
                        tgt_lang = tgt.get('lang', None)

                    if not set('{}+@[];()=').intersection(set(src_text)) and \
                            not set('{}+@[];()=').intersection(set(tgt_text)) \
                            and is_typo:
                        src_text = remove_comment_sym_and_html(src_text)
                        tgt_text = remove_comment_sym_and_html(tgt_text)
                        # some assumptions below,
                        # 1) if texts are 5 or more chars apart, it's not just a typo fix
                        # 2) have to check if the two texts are identical after removing symbols
                        if abs(len(tgt_text) - len(src_text)) < 5 and \
                                src_text and src_text != tgt_text and \
                                src_lang == tgt_lang == language:
                            tsv_writer.writerow([src_lang, src_text, tgt_text])


if __name__ == '__main__':
    create_language_json('typo_corpus/github-typo-corpus.v1.0.0.jsonl', language='eng')
    create_language_json('typo_corpus/github-typo-corpus.v1.0.0.jsonl', language='rus')
    create_language_json('typo_corpus/github-typo-corpus.v1.0.0.jsonl', language='spa')

