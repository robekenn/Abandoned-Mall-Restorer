"""Player-facing regression checks for the opening, task revision and prop fixes."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from game.art import PALETTE
from mall.furniture import bench_footprint, fountain_footprint


class WelcomeAndErrandsTests(unittest.TestCase):
    def setUp(self):self.game=Game()

    def tearDown(self):pygame.quit()

    def unlock(self):
        g=self.game
        for trash in g.mall.trash:g.mall.clean_trash(trash)
        for store in g.mall.stores:store.restored=True
        g.mall.refresh_businesses();g.mall.unlock_east()
        for trash in g.mall.east.trash:g.mall.clean_trash(trash)
        for store in g.mall.stores:store.restored=True
        g.mall.refresh_businesses()

    def test_each_owner_collects_from_its_sections_signed_delivery_point(self):
        self.unlock();g=self.game;g.shoppers.walkways.refresh(g.mall)
        for store in (s for s in g.mall.stores if not s.upgrade_shop):
            with self.subTest(store=store.name):
                store.request_wait=0
                self.assertTrue(g.owner_requests.accept(store,g.mall))
                depot=g.mall.east.delivery if store in g.mall.east.stores else g.mall.delivery
                spot=g.owner_requests.spots[0]
                self.assertEqual(spot.position,depot.position)
                self.assertTrue(all(not wall.collidepoint(spot.position) for wall in g.mall.obstacles))
                self.assertGreater(min(spot.position.distance_to(b.position) for b in g.mall.trash_bins),100)
                self.assertTrue(g.shoppers.walkways.route(store.position,spot.position))
                with patch.object(g.art,'draw') as draw:
                    spot.draw(g.screen,g.camera,g.art,g.hud.small,False)
                    draw.assert_not_called()  # The package is on the permanent platform.
                g.upgrades.held=g.upgrades.capacity
                self.assertTrue(g.owner_requests.interact(spot))
                self.assertTrue(g.claim_request(store))
                self.assertEqual(g.upgrades.held,g.upgrades.capacity)

    def test_display_mouse_keyboard_undo_retry_and_exact_once_reward(self):
        self.unlock();g=self.game;store=g.mall.stores[1]
        store.request_wait=0;store.request_level=1;store.request_bonus=.5
        g.owner_requests.accept(store,g.mall)
        g.player.rect.center=g.owner_requests.spots[0].position
        g.interact();self.assertTrue(g.display_menu.open)
        g.display_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_1),g)
        g.display_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_1),g)
        self.assertEqual(g.display_menu.arrangement,[0])
        g.display_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_BACKSPACE),g)
        self.assertEqual(g.display_menu.arrangement,[])
        before=(g.cash,g.player.rect.center,g.rent_timer,g.shoppers.elapsed,store.request_wait)
        g.update(200,(1,0),True)
        self.assertEqual(before,(g.cash,g.player.rect.center,g.rent_timer,g.shoppers.elapsed,store.request_wait))
        g.display_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),g)
        self.assertFalse(g.owner_requests.ready)
        self.assertTrue(g.running)
        g.interact()
        for index in g.owner_requests.display_plan:
            rect=g.display_menu.geometry(g.screen)[1][index]
            g.display_menu.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center),g)
        self.assertTrue(g.owner_requests.ready)
        self.assertFalse(g.display_menu.open)
        self.assertFalse(g.owner_requests.arrange_display(g.owner_requests.display_plan))
        cash=g.cash
        self.assertTrue(g.claim_request(store))
        self.assertEqual((g.cash,store.request_level,store.request_bonus),(cash+100,2,1.5))
        self.assertFalse(g.claim_request(store))
        self.assertEqual(g.cash,cash+100)

    def test_each_store_has_its_own_products_and_a_valid_three_item_plan(self):
        self.unlock();g=self.game;catalogs=set()
        g.screen=pygame.display.set_mode((800,600))
        for store in (s for s in g.mall.stores if not s.upgrade_shop):
            store.request_level=1;store.request_wait=0
            self.assertTrue(g.owner_requests.accept(store,g.mall))
            items=g.owner_requests.display_items;catalogs.add(items)
            self.assertEqual(len(set(items)),3)
            self.assertEqual(sorted(g.owner_requests.display_plan),[0,1,2])
            self.assertFalse(g.owner_requests.arrange_display((0,0,0)))
            self.assertFalse(g.owner_requests.arrange_display(()))
            g.display_menu.visit();g.draw();g.display_menu.open=False
            self.assertTrue(g.owner_requests.arrange_display(g.owner_requests.display_plan))
            g.claim_request(store)
        self.assertEqual(len(catalogs),8)

    def test_benches_and_fountains_allow_walking_through_the_old_empty_margins(self):
        self.unlock();g=self.game
        for bench in g.mall.benches:
            with self.subTest(bench=bench):
                wall=bench_footprint(bench)
                g.player.rect.center=(bench.left-35,bench.centery+10)
                g.player.move((1,0),.2,g.mall.obstacles)
                self.assertGreater(g.player.rect.centerx,bench.left+10)
                g.player.move((1,0),1,g.mall.obstacles)
                self.assertAlmostEqual(g.player.rect.right,wall.left)
                # The tall backrest is visual, so a player can walk behind its base.
                g.player.rect.center=(bench.left-40,bench.top+6)
                g.player.move((1,0),1,g.mall.obstacles)
                self.assertGreater(g.player.rect.centerx,bench.right)
        for fountain in (g.mall.fountain,g.mall.east.fountain):
            wall=fountain_footprint(fountain)
            g.player.rect.center=(fountain.left-25,fountain.centery+30)
            g.player.move((1,0),.2,g.mall.obstacles)
            self.assertGreater(g.player.rect.centerx,fountain.left)
            g.player.move((1,0),1,g.mall.obstacles)
            self.assertAlmostEqual(g.player.rect.right,wall.left)
            g.player.rect.center=(fountain.left-40,fountain.top+25)
            g.player.move((1,0),1.5,g.mall.obstacles)
            self.assertGreater(g.player.rect.centerx,fountain.right)

    def test_floor_beneath_furniture_starts_dirty_cleans_and_gets_dirty_again(self):
        g=self.game
        # Activate both sections without cleaning away the floor being checked.
        for store in g.mall.stores:store.restored=True
        g.mall._initial_cleanup_complete=True;g.mall.unlock_east()
        fixtures=g.mall.benches+[g.mall.fountain,g.mall.east.fountain]
        samples=[p for p in g.mall.floor_tiles if any(rect.collidepoint(p) for rect in fixtures)]
        self.assertTrue(samples)
        for p in samples:self.assertFalse(g.mall.tile_restored(p))
        for t in g.mall.trash:g.mall.clean_trash(t)
        self.assertEqual(g.mall.cleanliness,1)
        self.assertEqual(g.mall.dirty_tiles,set())
        for p in samples:
            self.assertTrue(g.mall.tile_restored(p))
            pool=g.mall.north_trash if g.mall.opening_area.collidepoint(p) else g.mall.east.trash
            trash=min(pool,key=lambda t:t.position.distance_squared_to(p))
            self.assertLess(trash.position.distance_to(p),115)
            self.assertTrue(g.mall.respawn_trash(trash))
            self.assertFalse(g.mall.tile_restored(p))
            g.mall.clean_trash(trash)
            self.assertTrue(g.mall.tile_restored(p))
        self.assertEqual(g.mall.cleanliness,1)

    def test_player_and_fountain_render_in_correct_depth_order(self):
        g=self.game
        for y,behind in ((620,True),(750,False)):
            g.player.rect.center=(g.mall.fountain.centerx,y)
            with patch.object(g.art,'draw',wraps=g.art.draw) as draw:
                g.draw()
                names=[call.args[1] for call in draw.call_args_list]
                player=next(i for i,name in enumerate(names) if name.startswith('player_'))
                fountain=names.index('fountain_dirty')
                self.assertEqual(player<fountain,behind)

    def test_open_door_keeps_its_leaf_on_the_right(self):
        for kind in ('bookshop','cafe'):
            closed=self.game.art.sprites[kind+'_clean']
            self.assertEqual(closed.get_at((22,28)),pygame.Color(PALETTE['cream']))
            sprite=self.game.art.sprites[kind+'_clean_open']
            self.assertEqual(sprite.get_at((22,22)),pygame.Color(PALETTE['ink']))
            self.assertEqual(sprite.get_at((25,22)),pygame.Color(PALETTE['water']))
            self.assertEqual(sprite.get_at((26,22)),pygame.Color(PALETTE['light']))

    def test_intro_and_transition_freeze_world_then_allow_play(self):
        g=Game(start_screen=True)
        g.mall.stores[1].restored=True
        before=(g.cash,g.player.rect.center,g.litter_spawner.elapsed,g.rent_timer,g.mall.stores[1].request_wait)
        g.update(200,(1,0),True);g.interact()
        self.assertEqual(before,(g.cash,g.player.rect.center,g.litter_spawner.elapsed,g.rent_timer,g.mall.stores[1].request_wait))
        self.assertEqual(g.upgrades.held,0)
        g.welcome.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        g.update(.4,(1,0));self.assertTrue(g.welcome.open)
        g.update(.5,(1,0));self.assertFalse(g.welcome.open)
        self.assertEqual(g.player.rect.center,before[1])
        g.update(.1,(1,0))
        self.assertGreater(g.player.rect.centerx,before[1][0])
        self.assertLess(g.mall.stores[1].request_wait,180)

    def test_intro_click_start_quit_and_minimum_layout(self):
        g=Game(start_screen=True);g.screen=pygame.display.set_mode((800,600))
        g.update(1,(0,0));g.draw()
        panel,start,quit=g.welcome.geometry(g.screen)
        self.assertTrue(g.screen.get_rect().contains(panel))
        self.assertTrue(panel.contains(start));self.assertTrue(panel.contains(quit))
        g.welcome.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=start.center),g)
        self.assertTrue(g.welcome.leaving)
        g.update(.3,(0,0));g.draw()
        g.welcome.leaving=False
        g.welcome.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=quit.center),g)
        self.assertFalse(g.running)

    def test_fullscreen_start_and_toggle_preserve_the_session(self):
        g=Game(fullscreen=True,start_screen=True)
        self.assertTrue(g.fullscreen)
        self.assertTrue(g.screen.get_flags() & pygame.FULLSCREEN)
        g.cash=45;g.window_size=(800,600)
        g.toggle_fullscreen()
        self.assertFalse(g.fullscreen)
        self.assertEqual(g.screen.get_size(),(800,600))
        self.assertTrue(g.welcome.open)
        self.assertEqual(g.cash,45)
        g.toggle_fullscreen()
        self.assertTrue(g.fullscreen)
        self.assertEqual(g.cash,45)

    def test_launcher_defaults_fullscreen_with_optional_windowed_mode(self):
        import main
        for args,fullscreen in (([],True),(['--windowed'],False)):
            with patch('sys.argv',['main.py']+args),patch('game.game.Game') as game:
                main.main()
                game.assert_called_once_with(fullscreen=fullscreen,start_screen=True)
                game.return_value.run.assert_called_once()
