import random

STAND = 'stand'
HIT = 'hit'

CARDS = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
VALUES = {}
for i in range(len(CARDS)):
    if i == 0:
        VALUES[CARDS[i]] = -1
    elif i > 9:
        VALUES[CARDS[i]] = 10
    else:
        VALUES[CARDS[i]] = i + 1


def get_value(hand: list):
    total = 0
    for card in hand:
        if card != 'Ace':
            total += VALUES[card]
    if 'Ace' in hand:
        if total > 10:
            total += 1
        else:
            total += 11
    return total


def hit(hand: list):
    return hand + [random.choice(CARDS)]


def fill_dealer_hand(hand: list):
    if get_value(hand) < 17:
        return fill_dealer_hand(hit(hand))
    else:
        return hand


def is_winner(player_hand: list, dealer_hand: list):
    player_value = get_value(player_hand)
    dealer_value = get_value(dealer_hand)

    if player_value > 21:
        return False
    if player_value == dealer_value:
        return False
    elif player_value < dealer_value < 22:
        return False
    else:
        return True


def init_hands():
    dealer_hand = fill_dealer_hand(random.choices(CARDS, k=2))
    player_hand = random.choices(CARDS, k=2)
    return tuple((dealer_hand, player_hand))


def print_hands(dealer_hand: list, player_hand: list, name, dealer_cards: int, hide_dealer=False):
    if dealer_cards > len(dealer_hand):
        dealer_cards = len(dealer_hand)
    if hide_dealer:
        dealer_shown = f"{dealer_hand[0]}, " + (dealer_cards - 1)*'?, '
        dealer_shown = dealer_shown[:-2] + ' (value: ?)'
    else:
        dealer_shown = ', '.join(dealer_hand)
        dealer_shown += f' (value: {get_value(dealer_hand)})'
    out = f":heart: __**BLACKJACK**__ :clubs:\n" \
          f"**Dealer's Hand**: {dealer_shown}\n" \
          f"**{name}'s Hand**: {', '.join(player_hand)} (value: {get_value(player_hand)})\n\n"
    return out
