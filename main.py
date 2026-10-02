"""Launch from any working directory with Python 3.12+."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Abandoned Mall Restorer')
    parser.add_argument('--smoke-test', action='store_true',
                        help='Render a frame and exit using a headless display')
    args = parser.parse_args()
    if args.smoke_test:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
    from game.game import Game
    if args.smoke_test:
        import pygame
        game = Game()
        try:
            game.update(0.13, (1, 0))
            game.draw()
            for trash in game.mall.trash:
                trash.cleaned = True
            game.mall.stores[0].restored = True
            game.change_decor()
            game.change_decor()
            game.draw()
        finally:
            pygame.quit()
        return
    Game().run()


if __name__ == "__main__":
    main()
