from Classes import Player, Dealer, Table

DEALER_TURN = False


def build_game():
    player = Player()
    dealer = Dealer()
    table = Table(dealer, player)

    return table


game = build_game()

game.player_pick()
game.player_pick()

game.dealer_pick()
game.dealer_pick()

print(game)
