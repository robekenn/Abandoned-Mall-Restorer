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
            game.janitors.update(.21,game);game.draw()
            game.janitors.update(3.79,game)
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
            # Optional life content and pause UI are also exercised in frozen builds.
            game.life.chat(game,owner_store)
            game.journal.open=True;game.journal.tab=3;game.draw();game.journal.open=False
            for key,*_ in game.janitors.courts(game.mall):
                if not game.life.start(game,key):raise RuntimeError('Community event did not start: '+key)
                game.player.rect.center=game.life.spot.position;game.frame_camera(game.screen.get_size())
                game.community_menu.open=True;game.draw()
                for _ in range(3):
                    if game.life.tasks:
                        task=game.life.visible_tasks[0];game.player.rect.center=task.position
                        game.community_menu.open=False
                        if task.duration:game.life.work(task.duration,game,True,True)
                        else:game.life.touch(game,task)
                    else:game.life.choose(game,game.life.round if game.life.activity=='recipe' else game.life.event.guests[game.life.round][2])
                    game.draw()
                game.life.choose(game,0);game.community_menu.open=False
            game.life.cooldowns['north']=0
            if not game.life.start(game,'north'):raise RuntimeError('Recurring event did not start')
            game.life.choose(game,game.life.event.guests[0][2])
            game.pause.show();game.draw();game.pause.activate(game,2);game.draw()
            game.pause.activate(game,0);game.pause.open=False
            with TemporaryDirectory() as directory:
                game.save_store=SaveStore(directory,developer=args.dev,enabled=True)
                cash=game.cash
                if not game.save_store.save(game):raise RuntimeError('Checkpoint write failed')
                game.cash=0
                if not game.save_store.load(game) or game.cash!=cash or not game.story.festival or game.life.round!=1 or game.life.active!='north':
                    raise RuntimeError('Checkpoint roundtrip failed')
            game.draw()
            # A distinct scene shares equipment and cash, but never indoor rendering.
            game.player.rect.center=game.courtyard.door(game.mall).position
            if not game.enter_courtyard(save=False):raise RuntimeError('Courtyard entry failed')
            world=game.courtyard.world
            for trash in world.trash:world.clean_trash(trash)
            for store in world.stores:store.restored=True
            world.refresh_businesses()
            game.open_upgrade_shop(world.stores[0])
            for category in range(3):game.shop_menu.category=category;game.shop_menu.selection=0;game.draw()
            for key in ('courtyard_service','courtyard_comfort','courtyard_compost'):game.buy_upgrade(key)
            game.upgrades.decor.update(o.key for category in ('Furniture','Garden') for o in game.upgrades.offers(category,'courtyard'))
            game.shop_menu.open=False;game.update(.2,(0,0));game.draw()
            game.journal.open=True;game.draw();game.journal.open=False
            # Exercise every optional kitchen in source and frozen distributions.
            for store in world.stores[1:]:
                game.player.rect.center=store.position;game.frame_camera(game.screen.get_size())
                game.courtyard.kitchen_requests.waits[store.name]=0
                game.interact();game.draw()
                menu=game.cooking_menu
                if not menu.open:raise RuntimeError('Kitchen did not open: '+store.name)
                menu.primary(game);game.draw()
                while not menu.round.complete:
                    cooking=menu.round
                    if not cooking.order:game.update(cooking.target*cooking.sweep_seconds,(0,0))
                    menu.act(cooking.order[cooking.step] if cooking.order else 0,game);game.draw()
                if game.courtyard.cooking[store.name]['served']!=1:raise RuntimeError('Kitchen order not served')
                menu.open=False
            with TemporaryDirectory() as directory:
                game.save_store=SaveStore(directory,developer=args.dev,enabled=True)
                cash=game.cash
                if not game.save_store.save(game) or not game.save_store.load(game):raise RuntimeError('Courtyard checkpoint failed')
                if game.scene!='courtyard' or game.cash!=cash or not all(s.restored for s in game.courtyard.world.stores):raise RuntimeError('Courtyard state lost')
            game.leave_courtyard();game.draw()
        finally:
            pygame.quit()
        return
    game=Game(fullscreen=not args.windowed,start_screen=True,developer=args.dev,persistence=True)
    if args.windowed and game.fullscreen:game.toggle_fullscreen()
    game.run()


if __name__ == "__main__":
    main()
