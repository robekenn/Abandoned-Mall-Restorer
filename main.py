"""Launch from any working directory with Python 3.12+."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Abandoned Mall Restorer')
    parser.add_argument('--smoke-test', action='store_true',
                        help='Render a frame and exit using a headless display')
    parser.add_argument('--windowed', action='store_true',help='Start in a resizable window instead of fullscreen')
    parser.add_argument('--dev',action='store_true',help='Enable F3 developer playtest shortcuts')
    args = parser.parse_args()
    if args.smoke_test:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
    from game.game import Game
    if args.smoke_test:
        import pygame
        game = Game(start_screen=True,developer=args.dev)
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
            if args.dev:
                game.developer.open=True
                game.developer.act('cash_10000',game)
                game.draw()
                game.developer.open=False
            if owner_store.request_level != 3:
                raise RuntimeError('Owner request smoke test did not earn all improvements')
            # Render all four story encounters and exercise a real checkpoint in
            # source and frozen builds without touching a player's save directory.
            from tempfile import TemporaryDirectory
            from systems.saves import SaveStore
            from systems.story import CHAPTERS
            enabled=game.developer.enabled;game.developer.enabled=True
            for i in range(4):
                while i>len(game.mall.active_regions):game.developer.act('next',game)
                game.story.confirm(game,i,'begin')
                for point in (p for p in game.story.points if p.chapter==i and p.memory>=0):
                    game.player.rect.center=point.position
                    game.story.action(point,game);game.draw();game.story_menu.open=False
                if not all(game.story.memories[i]):raise RuntimeError('Keepsake discovery failed')
                if not game.story.prepare(game):raise RuntimeError('Story preparation failed')
                game.story_menu.visit(i,CHAPTERS[i].ending,'claim')
                game.draw();game.story_menu.open=False
                if not game.story.confirm(game,i,'claim'):raise RuntimeError('Story claim failed')
            game.developer.enabled=enabled
            if not game.story.confirm(game,3,'festival'):raise RuntimeError('Festival did not begin')
            game.draw();game.story_menu.open=False;game.story.update(0,game.mall)
            game.journal.open=True;game.journal.tab=2
            for i in range(4):
                game.journal.chapter=i
                for memories in (False,True):game.journal.memories_view=memories;game.draw()
            game.journal.open=False
            with TemporaryDirectory() as directory:
                game.save_store=SaveStore(directory,developer=args.dev,enabled=True)
                cash=game.cash
                if not game.save_store.save(game):raise RuntimeError('Checkpoint write failed')
                game.cash=0
                if not game.save_store.load(game) or game.cash!=cash or not game.story.festival:
                    raise RuntimeError('Checkpoint roundtrip failed')
            game.draw()
        finally:
            pygame.quit()
        return
    Game(fullscreen=not args.windowed,start_screen=True,developer=args.dev,persistence=True).run()


if __name__ == "__main__":
    main()
