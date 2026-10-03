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
            game.mall.unlock_east()
            for trash in game.mall.east.trash:
                game.mall.clean_trash(trash)
            for store in game.mall.stores:
                store.restored = True
            game.mall.refresh_businesses()
            for shop in ('north','east'):
                game.upgrades.decor.update(o.key for c in ('Furniture','Garden') for o in game.upgrades.offers(c,shop))
            game.upgrades.capacity_level = len(game.upgrades.CAPACITY_PRICES)
            game.upgrades.advanced_capacity_level = len(game.upgrades.ADVANCED_CAPACITY_PRICES)
            game.upgrades.speed_level = len(game.upgrades.SPEED_PRICES)
            for store in (game.mall.stores[0],game.mall.east.stores[0]):
                game.shop_menu.open = False
                game.player.rect.center = store.position
                game.update(0.13,(1,0))
                game.draw()
                game.open_upgrade_shop(store)
                for category in range(3):
                    game.shop_menu.category = category
                    game.draw()
            game.shop_menu.open = False
            owner_store = game.mall.stores[1]
            game.player.rect.center = owner_store.position
            game.update(8,(0,0))
            game.owner_menu.visit(owner_store)
            game.draw()
            game.owner_menu.action(game)
            game.player.rect.center = game.owner_requests.spots[0].position
            game.update(0,(0,0))
            game.draw()
            game.owner_requests.interact(game.owner_requests.spots[0])
            game.claim_request(owner_store)
            for level in (1,2):
                game.owner_requests.accept(owner_store,game.mall)
                for spot in game.owner_requests.spots:
                    game.player.rect.center = spot.position
                    game.update(spot.duration,(0,0),True)
                    game.draw()
                if level == 2:
                    for _ in range(3):
                        game.shoppers.update(8,game.mall,game.upgrades,owner_store)
                    for person in game.shoppers.people[:3]:
                        game.owner_requests.greet(person)
                game.player.rect.center = owner_store.position
                game.update(0,(0,0))
                game.owner_menu.visit(owner_store)
                game.draw()
                game.owner_menu.action(game)
            if owner_store.request_level != 3:
                raise RuntimeError('Owner request smoke test did not earn all improvements')
            game.draw()
        finally:
            pygame.quit()
        return
    Game().run()


if __name__ == "__main__":
    main()
