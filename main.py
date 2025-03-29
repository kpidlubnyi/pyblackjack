from Classes import Game
import keyboard
from time import sleep

game = Game()

while game.balance >= 20:
    keyboard.unhook_all()
    game.betting()

    while game.is_still_on:
        event = keyboard.read_event(suppress=True)

        match event.name:
            case '1':
                game.hit()
                sleep(0.2)
            case '0':
                game.stand()
                sleep(0.2)
            case '2':
                game.double_down()
                sleep(0.2)
            case '3':
                game.split()
                sleep(0.2)
            case 'esc':
                game.exit_game()

