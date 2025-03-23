from itertools import product
from random import choice, shuffle, randint


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
        result += f"\n   Total: {self.cards[0].value}+" if self.cards[1].hidden else f"\n   Total: {abs(self)}"
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
        return f"""
{'='*60}                                          
{'BlackJack Table':^60}
{'='*60}
   Dealer\'s Hand:{f'Cards remaining: {str(len(self.deck))}':>{55 - len('   Dealer\'s Hand:')}}
{str(self.dealer):^30}



   Your Hand:
{str(self.player):^30}
{'='*60}
{'[HIT(1)]                 [STAND(2)]':^60}
{'='*60}
"""

    def change_deck(self):
        self.deck = FrenchDeck() + FrenchDeck() + FrenchDeck() + FrenchDeck()
        self.deck.shuffle_deck()
        self.time_to_change_deck = False

    def player_pick(self):
        self.player.pick_card_from(self.deck)

    def dealer_pick(self):
        self.dealer.pick_card_from(self.deck)

    def show_dealers_card(self):
        self.dealer.show_second_card()


