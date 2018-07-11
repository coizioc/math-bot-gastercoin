"""Generates mathematics questions."""
import math
import random
import string


def add_term_to_question(coef, variable=None, there_is_preceeding_term=False, power=1):
    """Converts values into a term in an equation."""
    term_as_string = ''

    if there_is_preceeding_term:
        if coef > 0:
            term_as_string += '+ '
        elif coef < 0:
            term_as_string += '- '
    if variable is None:
        if coef > 0:
            term_as_string += f'{coef}'
        elif coef < 0:
            term_as_string += f'{-coef}'
    else:
        if not there_is_preceeding_term:
            if coef < 0:
                term_as_string += f'-'
        if coef < -1 or coef > 1:
            if coef > 0:
                term_as_string += f'{coef}'
            elif coef < 0:
                term_as_string += f'{-coef}'

    if variable is not None and coef != 0:
        term_as_string += variable

    if not (power == 1 or power == 0) and coef != 0:
        term_as_string += f'^{power} '
    else:
        term_as_string += ' '

    return term_as_string


def gen_arithmetic(simple=False):
    """Generates arithmetic problems."""
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)

    if not simple:
        operation = random.randint(0, 4)
    else:
        operation = random.randint(0, 1)

    if operation == 0:   # +
        return tuple((f'What is the sum of {num1} and {num2}?', str(num1 + num2)))
    elif operation == 1:   # -
        return tuple((f'What is the number you get when you subtract {num2} from {num1}?', str(num1 - num2)))
    elif operation == 2:   # *
        return tuple((f'What is the product of {num1} and {num2}?', str(num1 * num2)))
    elif operation == 3:   # /
        dividend = num1 * num2
        return tuple((f'What is the number you get when you divide {dividend} by {num1}?', str(num2)))
    elif operation == 4:   # ^
        return tuple((f'What is {num1} squared?', str(num1 ** 2)))


def gen_algebra(simple=True):
    """Generates algebra problems."""
    if simple:
        while True:
            variable = random.choice(string.ascii_lowercase)
            coef1 = random.randint(-100, 100)
            coef2 = random.randint(-100, 100)
            const1 = random.randint(-100, 100)
            const2 = random.randint(-100, 100)

            #   ax + b = cx + d
            # (a - c)x = d - b
            #        x = (d - b)/(a - c), a - c != 0
            if coef1 - coef2 != 0 and not (coef1 == 0 or coef1 == 0):
                solution = (const2 - const1) / (coef1 - coef2)
                if solution == int(solution):
                    break

        question = f'What is the value of {variable}: `'

        question += add_term_to_question(coef1, variable=variable)
        question += add_term_to_question(const1, there_is_preceeding_term=True)

        question += ' = '

        question += add_term_to_question(coef2, variable=variable)
        question += add_term_to_question(const2, there_is_preceeding_term=True)

        question += '`?'

        return tuple((question, str(int(solution))))
    else:
        solution = ''
        while True:
            # ax^2 + bx + c = 0
            a = random.randint(-10, 10)
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)

            try:
                if a != 0:
                    # Quadratic formula
                    sol1 = (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
                    sol2 = (-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)

                    if sol1 == int(sol1) and sol2 == int(sol2):
                        break
            except ValueError:
                if random.randint(0, 50) == 0:
                    solution = 'no solution'
                    break

        question = f'What are the value(s) of x where the parabola `y = '

        question += add_term_to_question(a, variable='x', power=2)
        question += add_term_to_question(b, variable='x', there_is_preceeding_term=True)
        question += add_term_to_question(c, there_is_preceeding_term=True)

        question += '` equals 0? If there is more than one solution, ' \
                    'write them as an ordered pair `a, b` where a < b. ' \
                    'If there is no solution, answer `no solution`.'

        if solution != 'no solution':
            if sol1 == sol2:
                solution = f'{int(sol1)}'
            elif sol1 < sol2:
                solution = f'{int(sol1)}, {int(sol2)}'
            else:
                solution = f'{int(sol2)}, {int(sol1)}'

        return tuple((question, solution))


def gen_geometry():
    """Generates geometry problems."""
    shape = random.randint(0,2)

    if shape == 0:   # circle
        radius = random.randint(1, 50)
        calcarea = random.randint(0, 1)
        if calcarea == 1:
            return tuple((f'What is the area of a circle with radius {radius} expressed as units of pi?',
                          f'{radius ** 2}pi'))
        else:
            return tuple((f'What is the circumference of a circle with radius {radius} expressed as units of pi?',
                          f'{radius * 2}pi'))
    elif shape == 1:   # square/rectangle/parallelagram
        length = random.randint(1, 50)
        width = random.randint(1, 50)
        calcarea = random.randint(0, 1)
        if length == width:
            name = 'square'
        else:
            if random.randint(0,1) == 1:
                name = 'rectangle'
            else:
                name = 'parallelagram'
        if calcarea == 1:
            return tuple((f'What is the area of a {name} with length {length} and width {width}?',
                          str(length * width)))
        else:
            return tuple((f'What is the perimeter of a {name} with length {length} and width {width}?',
                          str(length * 2 + width * 2)))
    elif shape == 2:   # triangle
        base = random.randint(1, 25) * 2
        height = random.randint(1, 25) * 2

        return tuple((f'What is the area of a triangle with base {base} and height {height}?',
                      str(int(base * height / 2))))


if __name__ == '__main__':
    for _ in range(20):
        print(gen_algebra(simple=False))