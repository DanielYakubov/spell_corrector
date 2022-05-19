import csv
import pandas as pd
import re

from nltk import word_tokenize
from preprocessing import remove_numbers_and_links

class TypoEvaluator(object):

    def __init__(self, tsv_path: str):
        self.tsv_path = tsv_path

    @staticmethod
    def remove_quotation_marks(sentence):
        """need to do this due to word_tokenize weirdness"""
        return re.sub(r"``|''|\"", '', sentence)

    def evaluate(self, metric='token_error_rate', compare_to='pred') -> float:
        """Evaluates the accuracy of the model's output using a tsv file that contains a tsv with 3 rows
        gold, corrupted, and pred
        param metric can either be 'all_or_nothing or token_error_rate"""
        df = pd.read_csv(self.tsv_path, delimiter='\t')
        metric_count = 0
        denom = 0

        assert metric in ['token_error_rate', 'all_or_nothing'], \
            "metric must either be 'token_error_rate' or 'all_or_nothing'"

        assert compare_to in ['pred', 'corrupted']

        for _, row in df.iterrows():
            # preprocessing gold
            gold = remove_numbers_and_links(row['gold'].lower())
            gold_toks = word_tokenize(self.remove_quotation_marks(gold))

            compared_toks = word_tokenize(self.remove_quotation_marks(row[compare_to]))

            if metric == 'all_or_nothing':
                denom += 1
                if gold_toks == compared_toks:
                    metric_count += 1
                else:
                    continue

            elif metric == 'token_error_rate':
                denom += len(gold_toks)
                for g, p in zip(gold_toks, compared_toks):
                    if g == p:
                        metric_count += 1

        return metric_count/denom

    def display_full_eval(self) -> None:
        """displays all possible eval combinations"""
        print(f'file {self.tsv_path}')
        for metric in ['all_or_nothing', 'token_error_rate']:
            for compare_to in ['pred', 'corrupted']:
                print(f"{compare_to} vs gold, {metric}:"
                      f" {self.evaluate(metric=metric, compare_to=compare_to) * 100:.2f}")

    def calculate_avg_word_len(self) -> float:
        """Calculate the average word length in a file"""
        df = pd.read_csv(self.tsv_path, sep='\t')
        word_count = 0
        character_count = 0
        for _, data in df.iterrows():
            toks = word_tokenize(data['gold'])
            for t in toks:
                word_count += 1
                character_count += len(t)
        return round(character_count/word_count, 4)

    def calculate_avg_typo_word_len(self) -> float:
        """Calculate the average word length in a file"""
        df = pd.read_csv(self.tsv_path, sep='\t')
        word_count = 0
        character_count = 0
        for _, data in df.iterrows():
            gtoks = word_tokenize(data['gold'])
            ctoks = word_tokenize(data['pred'])
            for g, c in zip(gtoks, ctoks):
                if g != c:
                    word_count += 1
                    character_count += len(c)
        return round(character_count / word_count, 4)

    def write_errors(self, tsv_path: str) -> None:
        """Write a tsv containing the errors for manual analysis"""
        indf = pd.read_csv(self.tsv_path, sep='\t')

        with open(tsv_path, 'w') as dump:
            tsv_writer = csv.writer(dump, delimiter='\t')
            tsv_writer.writerow(['gold', 'corrupted', 'error_pred', 'bad_word'])

            for _, row in indf.iterrows():
                gold = remove_numbers_and_links(row['gold'].lower())
                gold_toks = word_tokenize(self.remove_quotation_marks(gold))
                pred_toks = word_tokenize(self.remove_quotation_marks(row['pred']))
                if pred_toks != gold_toks:
                    for p, g in zip(pred_toks, gold_toks):
                        if p != g:
                            bad_tok = g + ' / ' + p
                    tsv_writer.writerow([' '.join(gold_toks), row['corrupted'], ' '.join(pred_toks), bad_tok])


if __name__ == '__main__':
    en_evaluator = TypoEvaluator('en/en_typos_pred.tsv')
    en_evaluator.display_full_eval()
    print(f"EN AVG WORD LENGTH {en_evaluator.calculate_avg_word_len()}")
    print(f"EN AVG TYPO'D WORD LENGTH {en_evaluator.calculate_avg_typo_word_len()}")

    es_evaluator = TypoEvaluator('es/es_typos_pred.tsv')
    es_evaluator.display_full_eval()
    print(f"ES AVG WORD LENGTH {es_evaluator.calculate_avg_word_len()}")
    print(f"ES AVG TYPO'D WORD LENGTH {es_evaluator.calculate_avg_typo_word_len()}")


    ru_evaluator = TypoEvaluator('ru/ru_typos_pred.tsv')
    ru_evaluator.display_full_eval()
    print(f"RU AVG WORD LENGTH {ru_evaluator.calculate_avg_word_len()}")
    print(f"RU AVG TYPO'D WORD LENGTH {ru_evaluator.calculate_avg_typo_word_len()}")

    en_evaluator.write_errors('en/en_for_analysis.tsv')
    es_evaluator.write_errors('es/es_for_analysis.tsv')
    ru_evaluator.write_errors('ru/ru_for_analysis.tsv')
