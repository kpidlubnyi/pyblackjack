from itertools import product
from random import choice, shuffle, randint
from time import sleep
from enum import StrEnum
import keyboard


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

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, i):
        return self.cards[i]


class Player:
    def __init__(self):
        self.hands = [Hand()]

    def __len__(self):
        return len(self.hands)

    def __repr__(self):
        return f'Player[{len(self)}]({self.hands})'

    def __str__(self):
        if len(self.hands) == 1:
            return f"""   Your Hand:
   {'  '.join([f'{card}' for card in self.hands[0]])}
   Total: {abs(self.hands[0])}"""

        str_hands = f"""   {f'First Hand:':<27}Second Hand:
   {f'{'  '.join([f'{card}' for card in self.hands[0]]):<27}'}{'  '.join([f'{card}' for card in self.hands[1]])}
   {f'{f'Total: {abs(self.hands[0])}':<27}'}Total: {abs(self.hands[1])}"""

        return str_hands

    def pick_card_from_to(self, deck: FrenchDeck, hand_no: int):
        card = deck.pick_random_card()
        card.show()
        self.hands[hand_no].cards.append(card)

    def split(self):
        self.hands.append(Hand())
        self.hands[1].cards.append(self.hands[0].cards.pop(1))


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

    def pick_card_from_to(self, deck: FrenchDeck, hand_no: int):
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

    def player_pick(self, hand_no: int = 0):
        self.player.pick_card_from_to(self.deck, hand_no)
        self.golden_card += 1

    def dealer_pick(self):
        self.dealer.pick_card_from_to(self.deck, 0)
        self.golden_card += 1

    def show_dealers_card(self):
        self.dealer.show_second_card()


def is_smaller_21(n: int):
    return False if n > 21 else True


class CommunicateWindow(StrEnum):
    WELCOME = f"""{f'+-------------------------------+':^60}
{f'|    WELCOME IN PYBLACKJACK!    |':^60}
{f'+-------------------------------+':^60}"""

    DEFAULT = f"""


"""
    BET = f"""{f'+-------------------------------+':^60}
             |      Enter your bet: """

    INVALID_BET = f"""{f'+-------------------------------+':^60}
{f'|  BET MUST BE DIVISIBLE BY 5!  |':^60}
{f'+-------------------------------+':^60}"""

    END = f"""{f'+-------------------------------+':^60}
{f'|       END OF THE ROUND        |':^60}
{f'+-------------------------------+':^60}"""

    EXIT = f"""{f'+-------------------------------+':^60}
{f'|        SEE YOU LATER!!        |':^60}
{f'+-------------------------------+':^60}"""

    INSUFFICIENT_BALANCE = f"""{f'+-------------------------------+':^60}
{f'|     INSUFFICIENT BALANCE!     |':^60}
{f'+-------------------------------+':^60}"""


class Game:
    def __init__(self, balance: int = 500):
        self.deck = FrenchDeck() + FrenchDeck() + FrenchDeck() + FrenchDeck()
        self.deck.shuffle_deck()
        self.balance = balance
        self.player = Player()
        self.dealer = Dealer()
        self.table = Table(self.dealer, self.player)
        self.bets = [0, 0]
        self.last_bet = 0
        self.bet_field = ['_', '_', '_', '_']
        self.is_still_on = False
        self.communicate_window = CommunicateWindow.WELCOME
        self.is_split_round = False
        self.playing_hand = 0

        print(self)
        sleep(2)

    def __repr__(self):
        return f'Game[deck: {self.deck}, balance: {self.balance}, player: {self.player!r}, dealer: {self.dealer!r}]'

    def __str__(self):
        return f"""
{'=' * 60}                                          
{f'     Bet: {sum(self.bets)}'}{'BlackJack Table':^38}{f'[ {f'{int(self.balance)}'} ]'}
{'=' * 60}
   Dealer\'s Hand:{f'Cards remaining: {str(len(self.deck))}':>{55 - len('   Dealer\'s Hand:')}}
{str(self.dealer):^30}
{self.communicate_window + (f'{''.join(self.bet_field)}     |\n             ' +
                            '+-------------------------------+' if self.communicate_window == CommunicateWindow.BET
                            else '')}
{'' if not self.is_split_round else '       ↓' if self.playing_hand == 0 else '                                   ↓'}                            
{str(self.player):^30}
{'=' * 60}
{'[HIT(1)]                 [STAND(0)]':^60}
{'=' * 60}
"""

    def second_card_is_hidden(self):
        return self.dealer.cards[1].hidden

    def start_round(self):
        self.communicate_window = CommunicateWindow.DEFAULT
        self.is_still_on = True
        print(self)
        sleep(1)

        turns = [self.player, self.dealer] * 2

        for hand in turns:
            hand.pick_card_from_to(self.deck, self.playing_hand)
            print(self)
            sleep(0.25)

        if abs(self.dealer) == 21:
            self.dealer.show_second_card()
            self.end_the_round('l')
        elif abs(self.player.hands[0]) == 21:
            self.end_the_round('bl')

    def split(self):
        if (not self.is_split_round
                and self.player.hands[0].cards[0].value == self.player.hands[0].cards[1].value
                and self.balance >= self.bets[0]):
            self.player.split()
            self.is_split_round = True
            self.balance -= self.bets[0]
            self.bets = [self.last_bet, self.last_bet]
            self.player.pick_card_from_to(self.deck, 0)
            self.player.pick_card_from_to(self.deck, 1)
            print(self)

    def summarize_round(self):
        def results_of_split_round():
            return [2 if (abs(self.player.hands[i]) > abs(self.dealer) and is_smaller_21(abs(self.player.hands[i])))
                    or (abs(self.player.hands[i]) == 21)
                    or (is_smaller_21(abs(self.player.hands[i])) and abs(self.dealer) > 21)
                    else 1 if abs(self.player.hands[i]) == abs(self.dealer)
                    else 0
                    for i in range(len(self.player.hands))]

        if not self.is_split_round:
            if abs(self.player.hands[0]) > abs(self.dealer):
                self.end_the_round('w')
            elif abs(self.dealer) > abs(self.player.hands[0]):
                self.end_the_round('l')
            else:
                self.end_the_round('d')
        else:
            results_of_round = results_of_split_round()
            self.end_the_round('split', results_of_round)

    def end_the_round(self, message, results: list[int]=None):
        if message in ['w', 'd', 'l', 'bl']:
            match message:
                case 'bl':
                    self.balance += self.bets[0] * 2.5
                case 'w':
                    self.balance += self.bets[0] * 2
                case 'd':
                    self.balance += self.bets[0]
        else:
            for i, result in enumerate(results):
                if result == 2:
                    self.balance += self.bets[i] * 2
                elif result == 1:
                    self.balance += self.bets[i]


        self.communicate_window = CommunicateWindow.END
        print(self)
        sleep(2)
        self.clean_the_table()
        self.is_still_on = False

    def clean_the_table(self):
        self.bets = [0, 0]
        self.last_bet = 0
        for hand in self.player.hands:
            hand.cards = []
        self.dealer.cards = []

        if self.is_split_round:
            self.is_split_round = False
            self.is_still_on = False
            del self.player.hands[1]
            self.playing_hand = 0

    def dealers_turn(self):
        self.dealer.show_second_card()
        print(self)
        sleep(1)

        while abs(self.dealer) < 17:
            self.dealer.pick_card_from_to(self.deck, 0)
            print(self)
            sleep(0.5)

        if abs(self.dealer) > 21 and not self.is_split_round:
            self.end_the_round('w')
        else:
            self.summarize_round()

    def betting(self):
        self.clean_bet_field()
        self.communicate_window = CommunicateWindow.BET
        print(self)

        while True:
            self.clean_bet_field()
            self.communicate_window = CommunicateWindow.BET
            amount = self.input_bet()
            if self.bet_is_valid(amount):
                self.bets = [amount, 0]
                self.last_bet = amount
                self.balance -= amount
                break
            else:
                self.communicate_window = CommunicateWindow.INVALID_BET
                print(self)
                sleep(1)

        self.start_round()

    def bet_is_valid(self, amount: int):
        return True if amount <= self.balance and amount % 10 == 0 else False

    def hit(self):
        self.player.pick_card_from_to(self.deck, self.playing_hand)
        print(self)

        if not is_smaller_21(abs(self.player.hands[self.playing_hand])):
            if self.playing_hand == 0:
                if not self.is_split_round:
                    self.end_the_round('l')
                else:
                    self.playing_hand = 1
                    print(self)
            else:
                self.dealers_turn()

        elif abs(self.player.hands[self.playing_hand]) == 21:
            if self.playing_hand == 0 and not self.is_split_round:
                self.dealers_turn()
            elif self.is_split_round:
                self.playing_hand = 1 if self.playing_hand == 0 else self.dealers_turn()

    def stand(self):
        if self.is_split_round and self.playing_hand == 0:
            self.playing_hand = 1
            print(self)
        else:
            self.dealers_turn()

    def input_bet(self):
        def add_to_arr(n: str):
            if self.bet_field[0] != '_':
                return

            for i in range(len(self.bet_field) - 1):
                self.bet_field[i] = self.bet_field[i + 1]
            self.bet_field[-1] = n
            sleep(0.1)

        def remove_from_arr():
            if self.bet_field[-1] == '_':
                return

            for i in range(1, len(self.bet_field))[::-1]:
                self.bet_field[i] = self.bet_field[i - 1]
            self.bet_field[0] = '_'
            sleep(0.1)

        def parse_bet():
            underscores = list()

            if '_' in ''.join(self.bet_field):
                for i, symbol in enumerate(self.bet_field):
                    if symbol == '_':
                        underscores.append(i)

            for i in underscores[::-1]:
                del self.bet_field[i]

            return int(''.join(self.bet_field))

        while True:
            sleep(0.1)
            print(self)
            event = keyboard.read_event(suppress=True)

            if event.name.isdigit():
                if event.name == '0' and self.bet_field[-1] == '_':
                    pass
                else:
                    add_to_arr(event.name)
            elif event.name == 'backspace':
                remove_from_arr()
            elif event.name == 'enter':
                return parse_bet()
            elif event.name == 'esc':
                self.exit_game()

    def clean_bet_field(self):
        self.bet_field = ['_', '_', '_', '_']

    def double_down(self):
        def is_enough_on_balance(amount: int) -> bool:
            return amount <= self.balance

        def insufficient_balance():
            self.communicate_window = CommunicateWindow.INSUFFICIENT_BALANCE
            print(self)
            self.communicate_window = CommunicateWindow.DEFAULT
            sleep(1)
            print(self)

        def process_double():
            self.balance -= self.last_bet
            self.bets[self.playing_hand] += self.last_bet
            self.hit()

        if len(self.player.hands[self.playing_hand]) == 2:
            if not self.is_split_round:
                if is_enough_on_balance(self.last_bet):
                    process_double()
                    if self.is_still_on:
                        self.dealers_turn()
                else:
                    insufficient_balance()
            else:
                if is_enough_on_balance(self.last_bet):
                    if self.playing_hand == 0:
                        process_double()
                        self.playing_hand = 1
                        print(self)
                    else:
                        process_double()
                        if self.is_still_on:
                            self.dealers_turn()
                else:
                    insufficient_balance()

    def exit_game(self):
        self.communicate_window = CommunicateWindow.EXIT
        print(self)
        sleep(2)
        exit()
