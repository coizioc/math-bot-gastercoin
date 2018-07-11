"""Implements methods related to the quiz commands of mathbot.subs.gastercoin."""
import os
import random

from subs.gastercoin import mathgen
from subs.gastercoin.account import parse_int

QUESTIONS_DIRECTORY = f'./subs/gastercoin/resources/questions/'
QUESTION_FILES = [f for f in os.listdir(QUESTIONS_DIRECTORY)]

QUESTION_CATEGORIES = [filename[:-4] for filename in QUESTION_FILES]

QUIZ_TARGET_SCORE = 5

QUIZ_RULES = 'The rules of the competition are as follows: (1) First person to get to 5 points wins. Each question ' \
             'answered correctly is worth a point. (2) You both have 10 seconds to answer the question. The first to ' \
             'answer correctly will win that round.'


def parse_quiz_args(args):
    """Inputs a tuple of string arguments and outputs a 2-tuple."""
    difficulty = 0
    category = 'rand'

    if args != ():
        try:
            if len(args) > 1:
                difficulty = int(args[1])
                category = args[0]
            elif parse_int(args[0], return_bool=True):
                difficulty = int(args[0])
                category = 'rand'
            else:
                difficulty = 0
                category = args[0]
        except ValueError:
            pass
    return tuple((difficulty, category))


def get_question(args):
    """Inputs a tuple of string arguments and outputs a 4-tuple."""
    difficulty_and_category = parse_quiz_args(args)
    difficulty = difficulty_and_category[0]
    category = difficulty_and_category[1].lower()

    if type(difficulty) != int:
        difficulty = 0
    else:
        if difficulty > 3:
            difficulty = 3
        elif difficulty < 0:
            difficulty = 0
        if difficulty > 2 and category == 'mathematics':
            difficulty = 2

    for x in QUESTION_CATEGORIES:
        if category in x.lower():
            category = x
            break
    else:
        category = 'rand'

    if category == 'rand':
        category = random.choice(QUESTION_CATEGORIES)

    questions = []
    with open(f'{QUESTIONS_DIRECTORY}{category}.txt') as f:
        file_string = f.read().splitlines()
        for line in file_string:
            split_line = line.split(';')
            try:
                #(difficulty, question, answer)
                questions.append((int(split_line[0]), split_line[1], split_line[2:]))
            except:
                print(line)

    while True:
        question_and_answer = random.choice(questions)
        if question_and_answer[0] == difficulty:
            break

    question = question_and_answer[1]
    answer = question_and_answer[2]
    if question == '$QUESTION':
        if difficulty == 0:
            question_and_answer = mathgen.gen_arithmetic()
        elif difficulty == 1:
            if random.randint(0, 1) == 1:
                question_and_answer = mathgen.gen_algebra()
            else:
                question_and_answer = mathgen.gen_geometry()
        else:
            question_and_answer = mathgen.gen_algebra(simple=False)
        question = question_and_answer[0]
        answer = [question_and_answer[1]]

    return tuple((difficulty, category, question, answer))
