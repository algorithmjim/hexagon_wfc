from gamestates import *

if __name__ == "__main__":
    game_state = GameStateEnum.GAME
    game_state_menu = GameStateMainMenu()
    game_state_game = GameStateMainGameMode()

    while True:
        if game_state == GameStateEnum.MAIN_MENU:
            game_state = game_state_menu.update()
        elif game_state == GameStateEnum.GAME:
            game_state = game_state_game.update()
        elif game_state == GameStateEnum.QUIT:
            break