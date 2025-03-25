from itertools import product
from random import choice, shuffle, randint
from time import sleep



class Card:
    def __init__(self, rank, suit):
        self.rank = rank

        if self.rank in range(2, 11):
            self.value = self.rank
        else:
            self.value = 11 if self.rank == 'A' else 10
        self.suit = suit
        self.hidden = True

    def __repr__(self):
        return f'Card({self.rank!r}, {self.suit!r})'

    def __str__(self):
        if self.hidden:
            return '[H]'
        return f"[{self.rank}{self.suit}]"

    def show(self):
        self.hidden = False


class FrenchDeck:
    ranks = [n for n in range(2, 11)] + list('JQKA')
    suits = ['♣', '♦', '♥', '♠']

    def __init__(self, cards=None):
        if cards:
            self._cards = cards
        else:
            self._cards = [Card(rank, suite) for rank, suite in product(self.ranks, self.suits)]

    def __len__(self):
        return len(self._cards)

    def __repr__(self):
        return f'FrenchDeck({len(self)}) [{self._cards}]'

    def __str__(self):
        str_cards = [str(card) for card in self._cards]
        return f'FrenchDeck[{len(self)}]({', '.join(str_cards)})'

    def __getitem__(self, i):
        return self._cards[i]

    def __add__(self, other):
        cards = self._cards + other._cards
        return FrenchDeck(cards)

    def pick_random_card(self):
        card: Card = choice(self._cards)
        self._cards.remove(card)
        return card

    def shuffle_deck(self):
        shuffle(self._cards)


class Hand:
    def __init__(self):
        self.cards = []

    def __repr__(self):
        return f'Hand[{abs(self)}]({self.cards})'

    def __abs__(self):
        c = 0
        for card in self.cards:
            c += card.value
        return c


class Player(Hand):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f'Player[{abs(self)}]({self.cards})'

    def __str__(self):
        return f'{'  '.join([f'{card}' for card in self.cards])}\n   Total: {abs(self)}'

    def pick_card_from(self, deck: FrenchDeck):
        card: Card = deck.pick_random_card()
        card.show()
        self.cards.append(card)


class Dealer(Hand):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f'Dealer[{abs(self)}]({self.cards})'

    def __str__(self):
        result = f'{'  '.join([f'{card}' for card in self.cards])}'
        try:
            result += f"\n   Total: {self.cards[0].value}+" if self.cards[1].hidden else f"\n   Total: {abs(self)}"
        except IndexError:
            result += f"\n   Total: {abs(self)}"
        return result

    def pick_card_from(self, deck: FrenchDeck):
        card: Card = deck.pick_random_card()

        if len(self.cards) != 1:
            card.show()
        self.cards.append(card)

    def show_second_card(self):
        self.cards[1].show()


class Table:
    played_cards = 0
    time_to_change_deck = False

    def __init__(self, dealer: Dealer, player: Player):
        self.deck = FrenchDeck() + FrenchDeck() + FrenchDeck() + FrenchDeck()
        self.deck.shuffle_deck()
        self.dealer = dealer
        self.player = player
        self.golden_card = randint(30, 200)

    def __repr__(self):
        return f'Table[deck: {len(self.deck)}, dealer: {self.dealer!r}, player: {self.player!r}]'

    def __str__(self):
        return self.__repr__()

    def change_deck(self):
        self.deck = FrenchDeck() + FrenchDeck() + FrenchDeck() + FrenchDeck()
        self.deck.shuffle_deck()
        self.time_to_change_deck = False

    def player_pick(self):
        self.player.pick_card_from(self.deck)
        self.golden_card += 1

    def dealer_pick(self):
        self.dealer.pick_card_from(self.deck)
        self.golden_card += 1

    def show_dealers_card(self):
        self.dealer.show_second_card()


def is_smaller_21(n: int):
    return False if n > 21 else True


class Game:
    def __init__(self, balance: int = 500):
        self.deck = FrenchDeck() + FrenchDeck() + FrenchDeck() + FrenchDeck()
        self.deck.shuffle_deck()
        self.balance = balance
        self.player = Player()
        self.dealer = Dealer()
        self.table = Table(self.dealer, self.player)
        self.bet = 0
        self.is_still_on = True

        print("WELCOME TO PYBLACKJACK!")
        sleep(3)

    def __repr__(self):
        return f'Game[deck: {self.deck}, balance: {self.balance}, player: {self.player!r}, dealer: {self.dealer!r}]'

    def __str__(self):
        return f"""
{'=' * 60}                                          
{f'     Bet: {self.bet}'}{'BlackJack Table':^38}{f'[ {f'{self.balance}'} ]'}
{'=' * 60}
   Dealer\'s Hand:{f'Cards remaining: {str(len(self.deck))}':>{55 - len('   Dealer\'s Hand:')}}
{str(self.dealer):^30}



   Your Hand:
{str(self.player):^30}
{'=' * 60}
{'[HIT(1)]                 [STAND(2)]':^60}
{'=' * 60}
"""

    def second_card_is_hidden(self):
        return self.dealer.cards[1].hidden

    def start_round(self):
        self.is_still_on = True

        print(self)
        sleep(2)

        turns = [self.player, self.dealer] * 2
        for hand in turns:
            hand.pick_card_from(self.deck)
            print(self)
            sleep(0.5)

        if abs(self.dealer) == 21:
            if self.second_card_is_hidden():
                self.dealer.show_second_card()
            self.lose_round()

    def summarize_round(self):
        if abs(self.player) > abs(self.dealer):
            self.win_round()
        elif abs(self.dealer) > abs(self.player):
            self.lose_round()
        else:
            self.draw()

    def dealers_turn(self):
        self.dealer.show_second_card()

        while abs(self.dealer) < 17:
            self.dealer.pick_card_from(self.deck)
            print(self)

        if abs(self.dealer) > 21:
            self.win_round()
        else:
            self.summarize_round()

    def betting(self):
        while True:
            amount = int(input("Enter the bet amount: "))
            if self.bet_is_valid(amount):
                break
        self.bet += amount
        self.balance -= amount
        self.start_round()

    def bet_is_valid(self, amount: int):
        return True if amount <= self.balance and amount % 10 == 0 else False

    def hit(self):
        self.player.pick_card_from(self.deck)
        print(self)
        if not is_smaller_21(abs(self.player)):
            self.lose_round()
        elif abs(self.player) == 21:
            self.win_round()
        else:
            pass

    def stand(self):
        self.dealers_turn()

    def clean_table(self):
        self.bet = 0
        self.player.cards = []
        self.dealer.cards = []

    def lose_round(self):
        print('YOU LOSE!')
        print(self)
        self.clean_table()
        self.is_still_on = False

    def win_round(self):
        print('YOU WIN!')
        print(self)
        self.balance += 2 * self.bet
        self.clean_table()
        self.is_still_on = False

    def draw(self):
        print('DRAW!')
        print(self)
        self.balance += self.bet
        self.clean_table()
        self.is_still_on = False
