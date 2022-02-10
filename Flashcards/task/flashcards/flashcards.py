import json
import sys
import random
import logging
import shutil
from io import StringIO
import argparse


class Flashcards:
    def __init__(self):
        self.arguments = self.import_export_argparser()
        self.stream = StringIO()
        self.logger_input = self.input_logger()
        self.logger_output = self.output_logger()
        self.flashcards = {}

    def input_action(self):
        if self.arguments[0] is not None:
            self.cards_import(args=True)
        repetition = 0
        input_string = 'Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):'
        action_mapping = {'add': self.add, 'remove': self.remove, 'ask': self.ask, 'import': self.cards_import,
                          'export': self.export, 'hardest card': self.hardest_card, 'reset stats': self.reset_stats,
                          'log': self.log}

        while True:
            if repetition == 0:
                self.logger_output.info(input_string)
            else:
                self.logger_output.info(f'\n{input_string}')
            repetition += 1
            action = input()
            self.logger_input.info(action)
            if action in action_mapping.keys():
                action_mapping[action]()
            elif action == 'exit':
                if self.arguments[1] is None:
                    self.logger_output.info('Bye bye!')
                    break
                else:
                    self.export(args=True)
                    break
            else:
                sys.exit()

    def add(self):
        self.logger_output.info('The card:')
        card = input()
        self.logger_input.info(card)

        while card in self.flashcards.keys():
            self.logger_output.info(f'The card "{card}" already exists. Try again:')
            card = input()
            self.logger_input.info(card)
        self.logger_output.info(f'The definition of the card:')
        definition = input()
        self.logger_input.info(definition)
        definitions = [value['definition'] for value in self.flashcards.values()]
        while definition in definitions:
            self.logger_output.info(f'The definition "{definition}" already exists. Try again:')
            definition = input()
            self.logger_input.info(definition)
        self.flashcards[card] = {'definition': definition, 'mistakes': 0}
        self.logger_output.info(f'The pair ("{card}":"{definition}") has been added.')

    def remove(self):
        self.logger_output.info('Which card?')
        card = input()
        self.logger_input.info(card)
        if card in self.flashcards.keys():
            self.flashcards.pop(card)
            print('The card has been removed')
        else:
            self.logger_output.info(f"Can't remove \"{card}\": there is no such card.")

    def export(self, args=False):
        if not args:
            self.logger_output.info('File name:')
            filename = input()
            self.logger_input.info(filename)
        else:
            filename = self.arguments[1]
        with open(filename, 'w') as file:
            file.write(json.dumps(self.flashcards))
            self.logger_output.info(f'{len(self.flashcards)} cards have been saved.')

    def cards_import(self, args=False):
        if not args:
            self.logger_output.info('File name:')
            filename = input()
            self.logger_input.info(filename)
        else:
            filename = self.arguments[0]
        try:
            with open(filename, 'r') as file:
                import_content = json.loads(file.readlines()[0])
            self.logger_output.info(f'{len(import_content)} cards have been loaded.')
            self.flashcards.update(import_content)
        except FileNotFoundError:
            self.logger_output.info('File not found')

    def ask(self):
        self.logger_output.info('How many times to ask?')
        question_count = int(input())
        self.logger_input.info(question_count)
        definitions = [value['definition'] for value in self.flashcards.values()]
        random_questions = [random.choice(list(self.flashcards)) for i in range(question_count)]
        for card in random_questions:
            print(f'Print the definition of "{card}":')
            answer = input()
            self.logger_input.info(answer)
            correct_answer = self.flashcards[card]['definition']
            if answer == correct_answer:
                self.logger_output.info('Correct!')
            elif answer != correct_answer and answer in definitions:
                correct_term = [[card, values['definition']] for card, values in self.flashcards.items()
                                if answer == values['definition']]
                self.flashcards[card]['mistakes'] += 1
                self.logger_output.info(f'Wrong. The right answer is "{correct_term[0][1]}", '
                      f'but your definition is correct for "{correct_term[0][0]}".')
            else:
                self.flashcards[card]['mistakes'] += 1
                self.logger_output.info(f'Wrong. The right answer is "{correct_answer}".')

    def hardest_card(self):
        mistake_counts = [value['mistakes'] for value in self.flashcards.values()]
        if not self.flashcards or sum(mistake_counts) == 0:
            self.logger_output.info('There are no cards with errors.')
            return False
        else:
            max_errors = 0
            for mistake in mistake_counts:
                if mistake > max_errors:
                    max_errors = mistake
            cards_max_error = [card for card, values in self.flashcards.items() if values['mistakes'] == max_errors]
            if len(cards_max_error) == 1:
                self.logger_output.info(f'The hardest card is "{cards_max_error[0]}". You have {max_errors} errors answering it.')
            else:
                hardest_cards = '", "'.join(cards_max_error)
                self.logger_output.info(f'The hardest cards are "{hardest_cards}". You have {max_errors} errors answering them.')

    def reset_stats(self):
        for value in self.flashcards.values():
            value['mistakes'] = 0
        self.logger_output.info('Card statistics have been reset.')

    def input_logger(self):
        # create a logger object instance
        logger = logging.getLogger('input')
        # specify the lowest boundary for logging
        logger.setLevel(logging.INFO)

        # set a destination for your logs or a handler
        handler = logging.StreamHandler(self.stream)

        # set the logging format for a handler
        log_format = '%(message)s'
        handler.setFormatter(logging.Formatter(log_format))

        # finally, add the handler to the logger
        logger.addHandler(handler)
        return logger

    def output_logger(self):
        # create a logger object instance
        logger_output = logging.getLogger('output')
        # specify the lowest boundary for logging
        logger_output.setLevel(logging.INFO)
        log_format = '%(message)s'
        # set a destination for your logs or a handler
        handler_console = logging.StreamHandler(sys.stdout)
        handler_console.setFormatter(logging.Formatter(log_format))
        handler_stream = logging.StreamHandler(self.stream)
        handler_stream.setFormatter(logging.Formatter(log_format))
        # finally, add the handler to the logger
        logger_output.addHandler(handler_console)
        logger_output.addHandler(handler_stream)
        return logger_output

    def log(self):
        self.logger_output.info('File name:')
        file = input()
        self.logger_input.info(file)
        with open(file, 'w') as f:
            self.stream.seek(0)
            shutil.copyfileobj(self.stream, f)
        self.logger_output.info('The log has been saved.')

    def import_export_argparser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--import_from", help="import_from=IMPORT where IMPORT is the file name.")
        parser.add_argument("--export_to", help="export_to=EXPORT where EXPORT is the file name.")
        args = parser.parse_args()
        self.arguments = [args.import_from, args.export_to]
        return self.arguments


if __name__ == "__main__":
    Flashcards().input_action()

