"""Implements methods related to a GasterCoin economy and the exchange of such currency."""
import asyncio
import discord
from discord.ext import commands
import random
import ujson
from collections import Counter

from subs.gastercoin import mathgen

RESOURCES_DIRECTORY = './subs/gastercoin/resources/'
GASTERCOIN_CREATOR_ID_FILE = f'{RESOURCES_DIRECTORY}markovcreatorid.txt'
ACCOUNTS_FILE = f'{RESOURCES_DIRECTORY}accounts.json'
DEATHMATCH_FILE = f'{RESOURCES_DIRECTORY}deathmatch.txt'
QUESTIONS_FILE = f'{RESOURCES_DIRECTORY}questions.txt'
GASTERCOIN_HEAD_PICTURE = f'{RESOURCES_DIRECTORY}gastercoinhead.png'
GASTERCOIN_TAILS_PICTURE = f'{RESOURCES_DIRECTORY}gastercointails.png'

BALANCE_KEY = 'balance'
FREE_MONEY_KEY = 'free_money'
SPECIAL_MOVE_KEY = 'special_move'
DEFAULT_ACCOUNT = {BALANCE_KEY: 0,
                   FREE_MONEY_KEY: 0,
                   SPECIAL_MOVE_KEY: 'being lame and not having a special move set by typing '
                                     '`~dm special edit [message]`'}

with open(GASTERCOIN_CREATOR_ID_FILE, 'r') as f:
    MARKOV_MODULE_CREATORS_ID = int(f.readline())

with open(QUESTIONS_FILE, 'r', encoding='utf8') as f:
    file_string = f.read().splitlines()
    QUESTIONS = []
    for line in file_string:
        split_line = line.split(';')
        try:
            QUESTIONS.append((int(split_line[0]), split_line[1], split_line[2], split_line[3:]))
        except:
            print(line)

QUESTION_CATEGORIES = []
for question in QUESTIONS:
    QUESTION_CATEGORIES.append(question[1])
print(Counter(QUESTION_CATEGORIES))
QUESTION_CATEGORIES = list(set(QUESTION_CATEGORIES))

with open(DEATHMATCH_FILE, 'r', encoding='utf8') as f:
    file_string = f.read().splitlines()
    ATTACKS = []
    for line in file_string:
        split_line = line.split(';')
        try:
            ATTACKS.append((split_line[0], split_line[1]))
        except:
            print(line)

QUIZ_TARGET_SCORE = 5
ATTACK_PROBABILITIES = [0] * 5 + [1] * 25 + [2] * 22 + [3] * 18 + [4] * 15 + [5] * 12 +\
                       [6] * 9 + [7] * 6 + [8] * 4 + [9] * 3 + [10] * 2 + [11]

QUIZ_RULES = 'The rules of the competition are as follows: (1) First person to get to 5 points wins. Each question ' \
             'answered correctly is worth a point. (2) You both have 10 seconds to answer the question. The first to ' \
             'answer correctly will win that round.'
DEATHMATCH_HEADER = '__**:anger:DEATHMATCH:anger:**__'

SUCCESS_STRING = 'SUCCESS'
PERMISSION_ERROR_STRING = f'Error: You do not have permission to use this command.'

AUTHORIZED_CHANNELS = [340426498764832768, 408424622648721410, 340426332859269140, 464902493818585108]


class AmbiguousInputError(Exception):
    """Error raised for input that refers to multiple users"""
    def __init__(self, output):
        self.output = output


def parse_int(number_as_string, return_bool=False):
    """Converts an string into an int if the string represents a valid integer"""
    try:
        if len(number_as_string) > 1:
            int(str(number_as_string)[:-1])
        else:
            if len(number_as_string) == 0:
                if return_bool:
                    return False
                else:
                    raise ValueError
            if len(number_as_string) == 1 and number_as_string.isdigit():
                if return_bool:
                    return True
                else:
                    return int(number_as_string)
            else:
                if return_bool:
                    return False
                else:
                    raise ValueError
    except ValueError:
        if return_bool is False:
            raise ValueError
        else:
            return False
    last_char = str(number_as_string)[-1]
    if not return_bool:
        if last_char.isdigit():
            return int(number_as_string)
        elif last_char == 'k':
            return int(number_as_string[:-1]) * 1000
        elif last_char == 'm':
            return int(number_as_string[:-1]) * 1000000
        elif last_char == 'b':
            return int(number_as_string[:-1]) * 1000000000
        else:
            raise ValueError
    if return_bool:
        if last_char.isdigit() or last_char in ['k', 'm', 'b']:
            return True
        else:
            return False


def update_account(userid, amount, key=BALANCE_KEY):
    """Changes the value of a key within a user's account."""
    userid = str(userid)
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = ujson.load(f)

    if userid not in accounts:
        accounts[userid] = DEFAULT_ACCOUNT

    if key == BALANCE_KEY:
        accounts[str(userid)][BALANCE_KEY] += amount
    if key == FREE_MONEY_KEY:
        accounts[str(userid)][FREE_MONEY_KEY] = amount
    if key == SPECIAL_MOVE_KEY:
        accounts[str(userid)][SPECIAL_MOVE_KEY] = amount

    with open(ACCOUNTS_FILE, 'w') as f:
        ujson.dump(accounts, f)


def read_account(userid, key=BALANCE_KEY):
    """Reads the value of a key within a user's account."""
    userid = str(userid)
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = ujson.load(f)
        if userid not in accounts:
            accounts[userid] = DEFAULT_ACCOUNT
        return accounts[userid][key]
    except KeyError:
        return 0


def check_if_valid_transaction(userid, amount, username=None, zero_valid=False):
    """Determines whether a user can make a transaction or not based on the inputted amount."""
    try:
        amount = parse_int(amount)
        if amount <= 0 and not zero_valid or amount < 0 and zero_valid:
            return f'Error: G${amount} is not a valid transaction amount.'
        author_balance = read_account(userid)
        if author_balance < amount:
            if username is None:
                return f'Error: Insufficient funds. Your current balance is G${author_balance}.'
            else:
                return f"Error: Insufficient funds. {username}'s current balance is G${author_balance}."
        return SUCCESS_STRING
    except ValueError:
        return f'Error: G${amount} is not a valid number.'


def get_member_from_guild(guild_members, username):
    members = []
    for member in guild_members:
        if username.lower() in member.name.replace(' ', '').lower():
            members.append(member)

    members_len = len(members)
    if members_len == 0:
        raise NameError(username)
    elif members_len == 1:
        return members[0]
    else:
        raise AmbiguousInputError([member.name for member in members])


def parse_quiz_args(args):
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
    difficulty_and_category = parse_quiz_args(args)
    difficulty = difficulty_and_category[0]
    category = difficulty_and_category[1]

    arguments_right_type = type(difficulty) == int and type(category) == str
    category_exists = category in QUESTION_CATEGORIES or category == 'rand'

    if arguments_right_type and category_exists:
        is_rand_category = False
        if category == 'rand':
            category = random.choice(QUESTION_CATEGORIES)
            is_rand_category = True

        if difficulty > 3:
            difficulty = 3
        elif difficulty < 0:
            difficulty = 0
        if difficulty == 3 and category == 'riddles':
            difficulty = 2
        if difficulty > 2 and category == 'mathematics':
            difficulty = 2

        if category != 'mathematics':
            count = 1
            while True:
                question_and_answer = random.choice(QUESTIONS)
                if question_and_answer[0] == difficulty and question_and_answer[1] == category:
                    break
                count += 1
                if count % 100 == 99 and is_rand_category:
                    while True:
                        category = random.choice(QUESTION_CATEGORIES)
                        if category != 'mathematics':
                            break
            question = question_and_answer[2]
            answer = question_and_answer[3]
        else:
            if difficulty == 0:
                question_and_answer = mathgen.gen_arithmetic()
            elif difficulty == 1:
                if random.randint(0, 1) == 1:
                    question_and_answer = mathgen.gen_algebra()
                else:
                    question_and_answer = mathgen.gen_geometry()
            elif difficulty == 2:
                question_and_answer = mathgen.gen_algebra(simple=False)
            question = question_and_answer[0]
            answer = [question_and_answer[1]]

        return tuple((difficulty, category, question, answer))


def calculate_damage(power):
    """Calculates the amount of damage done based on its power from 0-10."""
    if power < 1:
        return 0
    if power > 10:
        return 100
    else:
        damage = power * 3 + random.randint((-1 * power), power)
        if damage < 0:
            damage = 0
        return damage


def do_deathmatch(fighter1, fighter2, bet=None):
    """Simulates each turn in a deathmatch and outputs the turns in the deathmatch as a list of strings."""
    fighter1name = fighter1.name
    fighter2name = fighter2.name
    is_fighter1turn = False
    fighter1_health = 100
    fighter2_health = 100

    deathmatch_messages = []

    current_message = f'{DEATHMATCH_HEADER}' \
                      f'\n\n\n\n' \
                      f'**{fighter1name}**: {fighter1_health}/100\n**{fighter2name}**: {fighter2_health}/100'

    previous_attack = '\n'
    deathmatch_messages.append(current_message)

    fighter1_turn_replace_list = [":arrow_right:", fighter1name, fighter2name, read_account(fighter1.id, key=SPECIAL_MOVE_KEY)]
    fighter2_turn_replace_list = [":arrow_left:", fighter2name, fighter1name, read_account(fighter2.id, key=SPECIAL_MOVE_KEY)]

    while True:
        # Chooses an appropriately powered attack.
        power = random.choice(ATTACK_PROBABILITIES)
        while True:
            attack = random.choice(ATTACKS)
            if int(attack[1]) == power:
                break
        current_attack = attack[0]

        if random.randint(0, 20) == 0:   # Randomly set attacks to miss.
            damage = 0
        elif "Infinity Gauntlet" in current_attack and random.randint(0, 1) == 0:   # Determines if Thanos spares you.
            damage = 0
        else:
            damage = calculate_damage(power)

        # Determine whose turn it is and replaces the names in the attack accordingly.
        if is_fighter1turn:
            replace_list = fighter1_turn_replace_list
            fighter2_health -= damage
            if fighter2_health < 0:
                fighter2_health = 0
        else:
            replace_list = fighter2_turn_replace_list
            fighter1_health -= damage
            if fighter1_health < 0:
                fighter1_health = 0

        current_attack = current_attack.replace('$P1', replace_list[1])
        current_attack = current_attack.replace('$P2', replace_list[2])
        if '$SPECIAL' in current_attack:
            current_attack = current_attack.replace('$SPECIAL', replace_list[3])
        current_attack = replace_list[0] + current_attack

        is_fighter1turn ^= True
        if damage == 0 and power != 0:
            current_attack = current_attack[:-1] + ', but it misses!'
        current_attack += ' It does ' + str(damage) + ' damage.\n' # f' It does __{damage}__ damage.\n'

        # Prints the current turn and appends it to the list of turns.
        current_message = f'{DEATHMATCH_HEADER}\n\n{previous_attack}{current_attack}\n' \
                          f'**{fighter1name}**: {fighter1_health}/100\n**{fighter2name}**: {fighter2_health}/100'
        deathmatch_messages.append(current_message)
        previous_attack = current_attack

        # Checks if either fighter is dead and breaks the loop.
        if fighter2_health < 1:
            current_message += f'\n:trophy: **{fighter1name} has won'
            if bet is not None:
                current_message += f' G${bet}!**'
            else:
                current_message += f'!**'
            deathmatch_messages.append(current_message)
            deathmatch_messages.append(fighter1.id)
            break
        if fighter1_health < 1:
            current_message += f'\n:trophy: **{fighter2name} has won'
            if bet is not None:
                current_message += f' G${bet}!**'
            else:
                current_message += f'!**'
            deathmatch_messages.append(current_message)
            deathmatch_messages.append(fighter2.id)
            break
    return deathmatch_messages


class Gastercoin():
    """Defines Gastercoin commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def freemoney(self, ctx):
        """Gives the user 1000 free GasterCoins. One time use only."""
        if read_account(ctx.author.id, key=FREE_MONEY_KEY):
                await ctx.send(f'Error: {ctx.author.name} has already accepted their free GasterCoins.')
        else:
            update_account(ctx.author.id, 1000)
            update_account(ctx.author.id, 1, key=FREE_MONEY_KEY)
            await ctx.send(f"Added 1000 GasterCoins to {ctx.author.name}'s account!")

    @commands.command()
    async def balance(self, ctx, name=None):
        """Checks the user's balance."""
        if name is None:
            amount = '{:,}'.format(read_account(ctx.author.id))
            await ctx.send(f'{ctx.author.name} has G${amount}')
        elif name == 'universe':
            await ctx.send('As all things should be.')
        else:
            try:
                person_member = get_member_from_guild(ctx.message.guild.members, name)
                amount = '{:,}'.format(read_account(person_member.id))
                await ctx.send(f'{person_member.name} has G${amount}')
            except NameError:
                await ctx.send(f'Error: {name} not found in server.')
            except AmbiguousInputError as members:
                await ctx.send(f'Error: input {name} can refer to multiple people ({members})')

    @commands.command()
    async def give(self, ctx, person, amount):
        """Donates GasterCoins from the user's account to another user's account."""
        out = check_if_valid_transaction(ctx.author.id, amount)
        if out == SUCCESS_STRING:
            amount = parse_int(amount)
            amount_formatted = '{:,}'.format(amount)
            person = person.lower()
            try:
                person_member = get_member_from_guild(ctx.message.guild.members, person)
                update_account(ctx.author.id, -amount)
                update_account(person_member.id, amount)
                await ctx.send(f'G${amount_formatted} given to {person_member.name}!')
            except NameError:
                await ctx.send(f'Error: {person} not found in server.')
            except AmbiguousInputError as members:
                await ctx.send(f'Error: input {person} can refer to multiple people ({members})')
        else:
            ctx.send(out)

    @commands.command(aliases=['flip'])
    async def flip_coin(self, ctx, bet, coin_side='h'):
        """Bets GasterCoins on a coin flip."""
        out = check_if_valid_transaction(ctx.author.id, bet)
        if out == SUCCESS_STRING:
            if 'h' in coin_side or 't' in coin_side:
                bet = parse_int(bet)
                coin = random.randint(0, 1)

                if coin == 0:
                    picture = GASTERCOIN_HEAD_PICTURE
                else:
                    picture = GASTERCOIN_TAILS_PICTURE

                if 'h' in coin_side and coin == 0 or 't' in coin_side and coin == 1:
                    update_account(ctx.author.id, bet)
                    out = "You won! "
                else:
                    update_account(ctx.author.id, -bet)
                    out = "You lost. "
                amount = '{:,}'.format(read_account(ctx.author.id))
                out += f"{ctx.author.name}'s balance is now G${amount}."
                if ctx.channel.id in AUTHORIZED_CHANNELS:
                    await ctx.send(out, file=discord.File(picture))
                else:
                    if coin == 0:
                        await ctx.send('Coin is heads. ' + out)
                    else:
                        await ctx.send('Coin is tails. ' + out)
            else:
                await ctx.send(f'Error: {coin_side} is not a valid coin side.')
        else:
            await ctx.send(out)

    @commands.group(invoke_without_command=True)
    async def quiz(self, ctx, *args):
        """Gives users GasterCash in exchange for correct answers."""
        question_args = get_question(args)
        difficulty = question_args[0]
        category = question_args[1]
        question = question_args[2]
        answer = question_args[3]

        await ctx.send(f"This {category} question of difficulty {difficulty} is for {ctx.author.name}. " + question)

        while True:
            message = await self.bot.wait_for('message')
            if message.author == ctx.author:
                if any([message.content.lower() == x.lower() for x in answer]):
                    amount_won = 10 ** (difficulty + 3)
                    amount_formatted = '{:,}'.format(amount_won)
                    update_account(ctx.author.id, amount_won)
                    await ctx.send(f"Answer {answer[0]} is correct! "
                                   f"{ctx.author.name}'s balance has increased by G${amount_formatted}!")
                else:
                    await ctx.send(f"Answer {message.content} is incorrect. Correct answer was {answer[0]}.")
                    break

    @quiz.command(name='categories')
    async def _categories(self, ctx):
        await ctx.send(QUESTION_CATEGORIES)

    @quiz.command(name='challenge')
    async def _challenge(self, ctx, opponent, bet='0'):
        out = check_if_valid_transaction(ctx.author.id, bet, zero_valid=True)
        if out == SUCCESS_STRING:
            bet = parse_int(bet)
            try:
                opponent_member = get_member_from_guild(ctx.message.guild.members, opponent)
            except NameError:
                await ctx.send(f'Error: {person} not found in server.')
                return
            except AmbiguousInputError as members:
                await ctx.send(f'Error: input {person} can refer to multiple people ({members})')
                return
            out = check_if_valid_transaction(opponent_member.id, bet, username=opponent_member.name, zero_valid=True)
            if out == SUCCESS_STRING:
                bet_formatted = '{:,}'.format(bet)
                update_account(ctx.author.id, -bet)
                out = f'A competition has been set up between {ctx.author.name} and {opponent_member.name} ' \
                      f'with bet G${bet_formatted}! To confirm this, {opponent_member.name} ' \
                      f'must react to this message with a :thumbsup: in the next minute. ' \
                      f'If a minute passes or if the challenger reacts to this message, ' \
                      f'the competition will be cancelled and the deposit refunded.'
                msg = await ctx.send(out)
                await msg.add_reaction('\N{THUMBS UP SIGN}')
                match_accepted = False
                while True:
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                        if str(reaction.emoji) == '👍' and user == opponent_member:
                            update_account(opponent_member.id, -bet)
                            match_accepted = True
                            break
                        elif user == ctx.author:
                            update_account(ctx.author.id, bet)
                            await msg.edit(content=f'{opponent_memmber.name} has declined their challenge '
                                                   f'and the deposit of G${bet_formatted} has been returned.')
                            break
                    except asyncio.TimeoutError:
                        update_account(ctx.author.id, bet)
                        await msg.edit(content=f'One minute has passed and the competition has been cancelled. '
                                               f'The deposit of G${bet_formatted} has been returned.')
                        break

                if match_accepted:
                    author_score = 0
                    opponent_score = 0
                    round_number = 1

                    while True:
                        question_and_answer = get_question()
                        question = question_and_answer[0]
                        answer = question_and_answer[1]
                        header = f'__**Quiz Game Show Thing**__\n**' \
                                 f'Round {round_number}**\n\n' \
                                 f'__Current Score__:\n' \
                                 f'__{ctx.author.name}__: {author_score}\n' \
                                 f'__{opponent_member.name}__: {opponent_score}\n\n'
                        question_message = header + question

                        msg = await ctx.send(question_message)

                        while True:
                            try:
                                message = await self.bot.wait_for('message', timeout=10)
                                if message.author == ctx.author or message.author == opponent_member:
                                    if any([message.content.lower() == x.lower() for x in answer]):
                                        if message.author == ctx.author:
                                            author_score += 1
                                        else:
                                            opponent_score += 1
                                        await msg.edit(content=f"{question_message} Answer {answer[0]} is correct! "
                                                       f"{message.author.name}'s score has increased by 1!")
                                        break
                            except asyncio.TimeoutError:
                                await msg.edit(content=f'{question_message} Nobody has correctly answered this question. '
                                                       f'The correct answer was {answer[0]}.')
                                break
                        if author_score == QUIZ_TARGET_SCORE:
                            update_account(ctx.author.id, (2 * bet))
                            await ctx.send(f'**{ctx.author.name} has won G${bet_formatted}!**')
                            break
                        elif opponent_score == QUIZ_TARGET_SCORE:
                            update_account(opponent_member.id, (2 * bet))
                            await ctx.send(f'**{opponent_member.name} has won G${bet}!**')
                            break
                        round_number += 1
            else:
                await ctx.send(out)
        else:
            await ctx.send(out)

    @commands.group(aliases=['dm'], invoke_without_command=True)
    async def deathmatch(self, ctx, opponent, bet=None):
        """Allows users to duke it out in a 1v1 match."""
        if bet is not None:
            out = check_if_valid_transaction(ctx.author.id, bet)
            if out == SUCCESS_STRING:
                bet = parse_int(bet)
                try:
                    opponent_member = get_member_from_guild(ctx.message.guild.members, opponent)
                except NameError:
                    await ctx.send(f'Error: {person} not found in server.')
                    return
                except AmbiguousInputError as members:
                    await ctx.send(f'Error: input {person} can refer to multiple people ({members})')
                    return
                out = check_if_valid_transaction(opponent_member.id, bet, username=opponent_member.name)
                if out == SUCCESS_STRING:
                    bet_formatted = '{:,}'.format(bet)
                    update_account(ctx.author.id, -bet)
                    out = f'Deathmatch set up between {ctx.author.name} and {opponent_member.name} with bet G${bet_formatted}! ' \
                          f'To confirm this match, {opponent_member.name} must react to this message with a :thumbsup: ' \
                          f'in the next minute. If a minute passes or if the challenger reacts to this message, ' \
                          f'the deathmatch will be cancelled and the deposit refunded.'
                    msg = await ctx.send(out)
                    await msg.add_reaction('\N{THUMBS UP SIGN}')

                    while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                            if str(reaction.emoji) == '👍' and user == opponent_member:
                                deathmatch_messages = do_deathmatch(ctx.author, opponent_member, bet=bet_formatted)
                                update_account(deathmatch_messages[-1], (2 * bet))
                                for message in deathmatch_messages[:-1]:
                                    await msg.edit(content=message)
                                    await asyncio.sleep(1)
                                break
                            elif user == ctx.author:
                                update_account(ctx.author.id, bet)
                                await msg.edit(content=f'{opponent_memmber.name} has declined their challenge '
                                                       f'and the deposit of G${bet_formatted} has been returned.')
                                return
                        except asyncio.TimeoutError:
                            update_account(ctx.author.id, bet)
                            await msg.edit(content=f'One minute has passed and the deathmatch has been cancelled. '
                                                   f'The deposit of G${bet_formatted} has been returned.')
                            return
                else:
                    await ctx.send(out)
            else:
                await ctx.send(out)
        else:
            try:
                opponent_member = get_member_from_guild(ctx.message.guild.members, opponent)
            except NameError:
                await ctx.send(f'Error: {opponent} not found in server.')
                return
            except AmbiguousInputError as members:
                await ctx.send(f'Error: input {opponent} can refer to multiple people ({members})')
                return
            msg = await ctx.send(DEATHMATCH_HEADER)
            deathmatch_messages = do_deathmatch(ctx.author, opponent_member)
            for message in deathmatch_messages[:-1]:
                await msg.edit(content=message)
                await asyncio.sleep(1)

    @deathmatch.command(name='special')
    async def _special(self, ctx, *args):
        """Lets user add a custom special attack in deathmatches."""
        if args != ():
            if args[0].lower() == 'edit':
                attack = ' '.join(args[1:])
                update_account(ctx.author.id, attack, key=SPECIAL_MOVE_KEY)
                await ctx.send(f"{ctx.author.name}'s special move updated to: $P1 KO's $P2 by __**{attack}**__!!!")
            else:
                await ctx.send(f"{ctx.author.name}'s current special move: $P1 KO's $P2 by "
                               f"__**{read_account(ctx.author.id, key=SPECIAL_MOVE_KEY)}**__!!!")
        else:
            await ctx.send(f"{ctx.author.name}'s current special move: $P1 KO's $P2 by "
                           f"__**{read_account(ctx.author.id, key=SPECIAL_MOVE_KEY)}**__!!!")


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Gastercoin(bot))
