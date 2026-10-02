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
                game.mall.clean_trash(trash)
            for store in game.mall.stores:
                store.restored = True
            game.mall.refresh_businesses()
            game.upgrades.decor.update(o.key for c in ('Furniture','Garden') for o in game.upgrades.offers(c))
            game.draw()
            game.shop_menu.open = True
            for category in range(3):
                game.shop_menu.category = category
                game.draw()
        finally:
            pygame.quit()
        return
    Game().run()


if __name__ == "__main__":
    main()
