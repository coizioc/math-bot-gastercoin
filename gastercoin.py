"""Implements methods related to a GasterCoin economy and the exchange of such currency."""
import asyncio
import discord
from discord.ext import commands
import random
import ujson

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
DEFAULT_ACCOUNT = {BALANCE_KEY: 0, FREE_MONEY_KEY: 0, SPECIAL_MOVE_KEY: 'being lame and not having a special move'}

with open(GASTERCOIN_CREATOR_ID_FILE, 'r') as f:
    MARKOV_MODULE_CREATORS_ID = int(f.readline())

with open(QUESTIONS_FILE, 'r', encoding='utf8') as f:
    file_string = f.read().splitlines()
    QUESTIONS = []
    for line in file_string:
        split_line = line.split(';')
        try:
            QUESTIONS.append((split_line[0], split_line[1], int(split_line[2])))
        except IndexError:
            print(line)

with open(DEATHMATCH_FILE, 'r', encoding='utf8') as f:
    file_string = f.read().splitlines()
    ATTACKS = []
    for line in file_string:
        split_line = line.split(';')
        try:
            ATTACKS.append((split_line[0], split_line[1]))
        except IndexError:
            print(line)

ATTACK_PROBABILITIES = [0] * 50 + [1] * 250 + [2] * 210 + [3]* 170 + [4] * 150 + [5] * 110 +\
                       [6] * 80 + [7] * 50 + [8] * 30 + [9] * 20 + [10] * 10 + [11]

DEATHMATCH_HEADER = '__**:anger:DEATHMATCH:anger:**__'

SUCCESS_STRING = 'SUCCESS'
PERMISSION_ERROR_STRING = f'Error: You do not have permission to use this command.'

AUTHORIZED_CHANNELS = [340426498764832768, 408424622648721410, 340426332859269140]


def parse_int(number_as_string):
    try:
        int(str(number_as_string)[:-1])
    except ValueError:
        raise ValueError
    last_char = str(number_as_string)[-1]
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


def update_account(userid, amount, key=BALANCE_KEY):
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
    userid = str(userid)
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = ujson.load(f)
        if userid not in accounts:
            accounts[userid] = DEFAULT_ACCOUNT
        return accounts[userid][key]
    except KeyError:
        return 0


def check_if_valid_transaction(userid, amount, username=None):
    """Determines whether a user can make a transaction or not based on the inputted amount."""
    try:
        amount = parse_int(amount)
        if amount <= 0:
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
    is_fighter1turn = True
    fighter1_health = 100
    fighter2_health = 100

    deathmatch_messages = []

    current_message = f'{DEATHMATCH_HEADER}' \
                      f'\n\n\n\n' \
                      f'**{fighter1name}**: {fighter1_health}/100\n**{fighter2name}**: {fighter2_health}/100'

    previous_attack = '\n'
    deathmatch_messages.append(current_message)

    while True:
        # Determines power of attack and damage dealt.
        power = random.choice(ATTACK_PROBABILITIES)
        damage = calculate_damage(power)

        # Chooses an appropriately powered attack.
        while True:
            attack = random.choice(ATTACKS)
            if int(attack[1]) == power:
                break
        current_attack = attack[0]
        if "Infinity Gauntlet" in current_attack and random.randint(0, 1):
            damage = 0

        # Determine whose turn it is and replaces the names in the attack accordingly.
        if is_fighter1turn:
            current_attack = current_attack.replace('$P1', fighter1name)
            current_attack = current_attack.replace('$P2', fighter2name)
            if '$SPECIAL' in current_attack:
                current_attack = current_attack.replace('$SPECIAL', read_account(fighter1.id, key=SPECIAL_MOVE_KEY))
            current_attack = ":arrow_right:" + current_attack
            fighter2_health -= damage
            if fighter2_health < 0:
                fighter2_health = 0
        else:
            current_attack = current_attack.replace('$P2', fighter1name)
            current_attack = current_attack.replace('$P1', fighter2name)
            current_attack = ":arrow_left:" + current_attack
            if '$SPECIAL' in current_attack:
                current_attack = current_attack.replace('$SPECIAL', read_account(fighter2.id, key=SPECIAL_MOVE_KEY))
            fighter1_health -= damage
            if fighter1_health < 0:
                fighter1_health = 0
        is_fighter1turn ^= True
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
            break
        if fighter1_health < 1:
            current_message += f'\n:trophy: **{fighter2name} has won'
            if bet is not None:
                current_message += f' G${bet}!**'
            else:
                current_message += f'!**'
            deathmatch_messages.append(current_message)
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
            await ctx.send(f'{ctx.author.name} has G${read_account(ctx.author.id)}')
        elif name == 'universe':
            await ctx.send('As all things should be.')
        else:
            guild_members = ctx.message.guild.members
            for member in guild_members:
                if member.name.lower() == name.lower():
                    await ctx.send(f'{member.name} has G${read_account(member.id)}')
                    break
            else:
                await ctx.send(f'Error: {name} not found in server.')

    @commands.command()
    async def give(self, ctx, person, amount):
        """Donates GasterCoins from the user's account to another user's account."""
        out = check_if_valid_transaction(ctx.author.id, amount)
        if out == SUCCESS_STRING:
            amount = parse_int(amount)
            person = person.lower()
            guild_members = ctx.message.guild.members
            for member in guild_members:
                if member.name.lower() == person:
                    update_account(ctx.author.id, (-1 * amount))
                    update_account(member.id, amount)
                    await ctx.send(f'G${amount} given to {member.name}!')
                    break
            else:
                await ctx.send(f'Error: {person} not found in server.')
        else:
            ctx.send(out)

    @commands.command(aliases=['flip'])
    async def flip_coin(self, ctx, bet, coin_side):
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
                    update_account(ctx.author.id, (-1 * bet))
                    out = "You lost. "

                out += f"{ctx.author.name}'s balance is now G${read_account(ctx.author.id)}."
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

    @commands.command()
    async def quiz(self, ctx, difficulty=0):
        """Gives users GasterCash in exchange for correct answers."""
        if difficulty > 3:
            difficulty = 3
        if difficulty < 0:
            difficulty = 0
        while True:
            question_and_answer = random.choice(QUESTIONS)
            if question_and_answer[2] == difficulty:
                break

        question = question_and_answer[0]
        answer = question_and_answer[1]
        # question_in_progress[ctx.author.id] = (answer, difficulty)
        await ctx.send(f"This question of difficulty {difficulty} is for {ctx.author.name}. " + question)

        while True:
            try:
                message = await self.bot.wait_for('message', timeout=60)
                if message.author == ctx.author:
                    if message.content.lower()in answer.lower() or answer.lower() in message.content.lower():
                        amount_won = (difficulty + 1) * 1000
                        update_account(ctx.author.id, amount_won)
                        await ctx.send(f"Answer {answer} is correct! "
                                       f"{ctx.author.name}'s balance has increased by G${amount_won}!")
                    else:
                        await ctx.send(f"Answer {message.content} is incorrect. Correct answer was {answer}.")
                    break
            except asyncio.TimeoutError:
                await ctx.send('Answer took too long. Type `~quiz [difficulty]` to receive another question.')

    @commands.group(aliases=['dm'], invoke_without_command=True)
    async def deathmatch(self, ctx, opponent, bet=None):
        if bet is not None:
            out = check_if_valid_transaction(ctx.author.id, bet)
            if out == SUCCESS_STRING:
                bet = parse_int(bet)
                guild_members = ctx.message.guild.members
                opponent_member = ctx.author
                for member in guild_members:
                    if member.name.lower() == opponent.lower():
                        opponent_member = member
                        break
                else:
                    await ctx.send(f'Error: {opponent} not found in server.')
                out = check_if_valid_transaction(member.id, bet, username=member.name)
                if out == SUCCESS_STRING:
                    update_account(ctx.author.id, (-1 * bet))
                    out = f'Deathmatch set up between {ctx.author.name} and {opponent_member.name} with bet G${bet}! ' \
                          f'To confirm this match, {opponent_member.name} must react to this message with a :thumbsup: ' \
                          f'in the next minute. If a minute passes or if the challenger reacts to this message, ' \
                          f'the deathmatch will be cancelled and the deposit refunded.'
                    msg = await ctx.send(out)

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60)
                        if str(reaction.emoji) == '👍' and user == member:
                            deathmatch_messages = do_deathmatch(ctx.author, opponent_member, bet=bet)
                            for message in deathmatch_messages:
                                await msg.edit(content=message)
                                await asyncio.sleep(1)
                        elif user == ctx.author:
                            update_account(ctx.author.id, bet)
                            await msg.edit(content=f'{opponent_memmber.name} has declined their challenge and the deposit '
                                                   f'of G${bet} has been returned.')
                    except asyncio.TimeoutError:
                        update_account(ctx.author.id, bet)
                        await msg.edit(content=f'One minute has passed and the deathmatch has been cancelled. '
                                               f'The deposit of G${bet} has been returned.')
                else:
                    await ctx.send(out)
            else:
                await ctx.send(out)
        else:
            guild_members = ctx.message.guild.members
            for member in guild_members:
                if member.name.lower() == opponent.lower():
                    msg = await ctx.send(DEATHMATCH_HEADER)
                    deathmatch_messages = do_deathmatch(ctx.author, member)
                    for message in deathmatch_messages:
                        await msg.edit(content=message)
                        await asyncio.sleep(1)
                    break
            else:
                await ctx.send(f'Error: {opponent} not found in server.')

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
