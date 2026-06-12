import pygame
from engine.core import Game
from game.menus import TitleScene, GameOverScene
from game.main import GameScene
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS


def main():
    game = Game(title="Voidflower", width=WINDOW_WIDTH, height=WINDOW_HEIGHT, fps=FPS)

    game.add_scene("title", TitleScene(game))
    game.add_scene("game", GameScene(game))
    game.add_scene("game_over", GameOverScene(game))

    game.run(start_scene="title")


if __name__ == "__main__":
    main()
