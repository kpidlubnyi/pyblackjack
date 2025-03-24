from Classes import Game

game = Game()

while game.balance >= 20:
    game.betting()

    while game.is_still_on:
        while True:
            action = int(input("Choose your action: "))
            if action not in (1, 2):
                print("ONLY 1 OR 2")
            else:
                break

        match action:
            case 1:
                game.hit()
            case 2:
                game.stand()
    print("IT'S OVER OF THE ROUND")
print("SEEMS LIKE YOU DON'T HAVE EVEN PENNY! SEE YOU LATER!")


