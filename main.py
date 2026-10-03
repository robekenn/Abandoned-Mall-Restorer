"""Launch from any working directory with Python 3.12+."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Abandoned Mall Restorer')
    parser.add_argument('--smoke-test', action='store_true',
                        help='Render a frame and exit using a headless display')
    parser.add_argument('--windowed', action='store_true',help='Start in a resizable window instead of fullscreen')
    args = parser.parse_args()
    if args.smoke_test:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
    from game.game import Game
    if args.smoke_test:
        import pygame
        game = Game(start_screen=True)
        try:
            game.update(.7,(0,0))
            game.draw()
            game.welcome.start()
            game.update(.45,(0,0))
            game.draw()
            game.update(.45,(0,0))
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
            for region in (game.mall.garden,game.mall.commons):
                if not game.mall.unlock_section(region):raise RuntimeError('Later area did not unlock')
                for trash in region.trash:game.mall.clean_trash(trash)
                for store in region.stores:store.restored=True
                game.mall.refresh_businesses()
            game.tutorial.skip()
            for shop in ('north','east','garden','commons'):
                game.upgrades.decor.update(o.key for c in ('Furniture','Garden') for o in game.upgrades.offers(c,shop))
            game.upgrades.capacity_level = len(game.upgrades.CAPACITY_PRICES)
            game.upgrades.advanced_capacity_level = len(game.upgrades.ADVANCED_CAPACITY_PRICES)
            game.upgrades.speed_level = len(game.upgrades.SPEED_PRICES)
            game.upgrades.value_level = len(game.upgrades.VALUE_PRICES)
            game.upgrades.advanced_value_level = len(game.upgrades.ADVANCED_VALUE_PRICES)
            for store in (s for s in game.mall.stores if s.upgrade_shop):
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
            game.owner_requests.update(180,game.mall)
            game.owner_menu.visit(owner_store)
            game.draw()
            game.owner_menu.action(game)
            game.player.rect.center = game.owner_requests.spots[0].position
            game.update(0,(0,0))
            game.draw()
            game.owner_requests.interact(game.owner_requests.spots[0])
            game.claim_request(owner_store)
            for level in (1,2):
                game.owner_requests.update(180,game.mall)
                game.owner_requests.accept(owner_store,game.mall)
                for spot in game.owner_requests.spots:
                    game.player.rect.center = spot.position
                    game.update(spot.duration,(0,0),True)
                    game.draw()
                if level == 1:
                    game.interact()
                    game.draw()
                    for index in game.owner_requests.display_plan:
                        game.display_menu.choose(index,game)
                if level == 2:
                    for _ in range(18):
                        game.shoppers.update(8,game.mall,game.upgrades,owner_store)
                        for person in game.shoppers.people:
                            game.owner_requests.greet(person)
                        if len(game.owner_requests.greetings)==3:break
                game.player.rect.center = owner_store.position
                game.update(0,(0,0))
                game.owner_menu.visit(owner_store)
                game.draw()
                game.owner_menu.action(game)
            game.owner_requests.update(180,game.mall)
            game.owner_requests.accept(owner_store,game.mall)
            game.owner_menu.visit(owner_store);game.draw();game.owner_menu.open=False
            for spot in game.owner_requests.visible_spots:
                game.player.rect.center=spot.position;game.update(0,(0,0));game.draw()
            game.journal.open = True
            for page in range((len([s for s in game.mall.stores if not s.upgrade_shop])+5)//6):game.journal.page=page;game.draw()
            game.cash=10000000
            for key,*_ in game.janitors.courts(game.mall):
                if not game.janitors.purchase(key,'hire',game)[0]:raise RuntimeError('Janitor hire failed')
                game.janitors.purchase(key,'walk',game);game.janitors.purchase(key,'clean',game)
            game.journal.tab=1;game.draw()
            game.journal.open=False
            for key,_,_,_,pool,_,_ in game.janitors.courts(game.mall):
                janitor=game.janitors.people[key]
                trash=next(t for t in pool if tuple(t.position) in janitor.paths.nodes)
                game.mall.respawn_trash(trash);janitor.position=trash.position.copy()
            game.janitors.update(4,game)
            if not all(j.cleaned for j in game.janitors.people.values()):raise RuntimeError('Janitor cleanup failed')
            game.draw()
            game.journal.open = False
            if owner_store.request_level != 3:
                raise RuntimeError('Owner request smoke test did not earn all improvements')
            game.draw()
        finally:
            pygame.quit()
        return
    Game(fullscreen=not args.windowed,start_screen=True).run()


if __name__ == "__main__":
    main()
