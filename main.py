from Classes import Game
import keyboard
from time import sleep

game = Game()

while game.balance >= 20:
    keyboard.unhook_all()
    game.betting()

    while game.is_still_on:
        if keyboard.is_pressed('1'):
            game.hit()
            sleep(0.2)
        elif keyboard.is_pressed('0'):
            game.stand()
            sleep(0.2)

print("SEEMS LIKE YOU DON'T HAVE EVEN PENNY! SEE YOU LATER!")
