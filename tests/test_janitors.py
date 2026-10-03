"""Court boundaries, hiring transactions, timed work and automatic-sale economics."""
import os
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.favors import FAVORS
from systems.requests import OWNERS


class JanitorTests(unittest.TestCase):
    def setUp(self):self.game=Game()
    def tearDown(self):pygame.quit()

    def open_all(self):
        g=self.game
        for region in g.mall.regions:
            for trash in g.mall.trash:g.mall.clean_trash(trash)
            for store in g.mall.stores:store.restored=True
            g.mall.refresh_businesses();self.assertTrue(g.mall.unlock_section(region))

    def hire(self,key='north'):
        g=self.game;g.cash=1000000
        self.assertTrue(g.janitors.purchase(key,'hire',g)[0])
        return g.janitors.people[key]

    def isolated_work(self):
        g=self.game;j=self.hire()
        for t in g.mall.trash:g.mall.clean_trash(t)
        trash=next(t for t in g.mall.north_trash if tuple(t.position) in j.paths.nodes)
        g.mall.respawn_trash(trash);j.position=trash.position.copy()
        return j,trash

    def test_ten_businesses_on_opposite_sides_and_safe_doors(self):
        g=self.game;self.open_all()
        self.assertEqual(len(g.mall.stores),40)
        self.assertEqual(len(OWNERS),36)
        g.shoppers.walkways.refresh(g.mall)
        for key,_,area,stores,pool,_,_ in g.janitors.courts(g.mall):
            self.assertEqual(len(stores),10)
            self.assertEqual([s.facing for s in stores],['down']*5+['up']*5)
            for store in stores:
                self.assertTrue(area.contains(store.rect))
                self.assertFalse(any(w.collidepoint(store.position) for w in g.mall.obstacles))
                self.assertEqual(g.shoppers.walkways.nearest(store.position) in g.shoppers.walkways.nodes,True)
            self.assertTrue(all(area.collidepoint(t.position) for t in pool))
        # Five original shops alone no longer reveal the next gate.
        north=Game();
        for t in north.mall.trash:north.mall.clean_trash(t)
        for store in north.mall.north_stores[:5]:store.restored=True
        self.assertFalse(north.mall.east.ready(north.mall))

    def test_opposite_storefront_is_visible_when_approached(self):
        g=self.game;g.screen=pygame.display.set_mode((800,600))
        store=g.mall.north_stores[-1];g.player.rect.center=store.position;g.update(0,(0,0))
        visible=g.camera.rect(store.rect)
        self.assertGreater(visible.top,160)
        self.assertLess(visible.bottom,g.screen.get_height()-58)

    def test_hire_price_locked_courts_cash_and_one_per_court(self):
        g=self.game
        self.assertEqual([g.janitors.hire_cost(c[0],g.mall) for c in g.janitors.courts(g.mall)],[6400,50000,132000,346000])
        g.cash=1000000
        for key in ('east','garden','commons'):
            self.assertFalse(g.janitors.purchase(key,'hire',g)[0]);self.assertEqual(g.cash,1000000)
        self.assertFalse(g.janitors.purchase('north','walk',g)[0])
        g.cash=6399;self.assertFalse(g.janitors.purchase('north','hire',g)[0]);self.assertEqual(g.cash,6399)
        g.cash=6400;self.assertTrue(g.janitors.purchase('north','hire',g)[0]);self.assertEqual(g.cash,0)
        person=g.janitors.people['north'];g.cash=1000000
        self.assertFalse(g.janitors.purchase('north','hire',g)[0]);self.assertIs(g.janitors.people['north'],person)
        self.assertEqual(g.cash,1000000)

    def test_five_second_pickup_and_fractional_sale_at_current_value(self):
        g=self.game;j,trash=self.isolated_work();cash=g.cash;g.upgrades.held=1
        g.janitors.update(4.99,g)
        self.assertFalse(trash.cleaned);self.assertEqual(g.cash,cash)
        g.janitors.update(.01,g)
        self.assertTrue(trash.cleaned);self.assertEqual(g.cash,cash+.75)
        self.assertEqual((j.cleaned,j.earnings,g.upgrades.held,g.total_collected,g.total_sold),(1,.75,1,0,0))
        g.mall.respawn_trash(trash);j.position=trash.position.copy();g.janitors.update(4,g)
        g.upgrades.value_level=2  # Value at completion, including upgraded contracts.
        g.janitors.update(1,g);self.assertEqual(g.cash,cash+.75+3)
        self.assertEqual(g.message_timer,0)

    def test_player_claiming_or_respawning_target_resets_work_without_duplicate_pay(self):
        g=self.game;j,trash=self.isolated_work();cash=g.cash
        g.janitors.update(4,g);g.mall.clean_trash(trash)
        g.janitors.update(1,g);self.assertEqual(g.cash,cash);self.assertEqual(j.cleaned,0)
        g.mall.respawn_trash(trash);j.position=trash.position.copy();g.janitors.update(4,g)
        g.mall.clean_trash(trash);g.mall.respawn_trash(trash)
        g.janitors.update(1,g);self.assertFalse(trash.cleaned);self.assertEqual(j.progress,1)
        g.janitors.update(4,g);self.assertTrue(trash.cleaned);self.assertEqual(g.cash,cash+.75)

    def test_upgrade_costs_limits_and_each_janitor_is_independent(self):
        self.open_all();g=self.game;g.cash=10000000
        for key,_,_,_,_,_,_ in g.janitors.courts(g.mall):self.assertTrue(g.janitors.purchase(key,'hire',g)[0])
        g.cash=1599;self.assertFalse(g.janitors.purchase('north','clean',g)[0]);self.assertEqual(g.cash,1599)
        g.cash=10000000
        for action in ('walk','clean'):
            for price in (1600,3200,6400):
                before=g.cash;self.assertTrue(g.janitors.purchase('north',action,g)[0]);self.assertEqual(before-g.cash,price)
            before=g.cash;self.assertFalse(g.janitors.purchase('north',action,g)[0]);self.assertEqual(g.cash,before)
        north=g.janitors.people['north'];east=g.janitors.people['east']
        self.assertEqual((north.speed,north.clean_seconds),(96,2));self.assertEqual((east.speed,east.clean_seconds),(48,5))
        self.assertLess(north.speed,240)

    def test_all_janitors_have_local_collision_safe_paths_to_every_litter_point(self):
        self.open_all();g=self.game
        for key,_,area,_,pool,_,_ in g.janitors.courts(g.mall):
            j=self.hire(key)
            for trash in pool:
                path=j.route_to(trash.position,g.mall)
                self.assertIsNotNone(path,(key,trash.position))
                self.assertTrue(all(area.collidepoint(p) for p in path))
                for a,b in zip([j.position]+path,path):
                    self.assertFalse(any(w.inflate(20,24).clipline(a,b) for w in g.mall.obstacles))

    def test_wandering_stays_local_and_helpers_clean_initial_sweeps(self):
        self.open_all();g=self.game
        for t in g.mall.trash:g.mall.respawn_trash(t)
        for key,_,_,_,_,_,_ in g.janitors.courts(g.mall):self.hire(key)
        store=g.mall.stores[1];store.request_level=3;store.request_wait=0
        store.recurring_completed=(2-list(OWNERS).index(store.name))%len(FAVORS)
        self.assertTrue(g.owner_requests.accept(store,g.mall))
        for _ in range(2200):
            g.janitors.update(.5,g)
            for key,j in g.janitors.people.items():
                area=next(c[2] for c in g.janitors.courts(g.mall) if c[0]==key)
                self.assertTrue(area.collidepoint(j.position))
            if g.mall.active_litter_count==0:break
        self.assertEqual(g.mall.active_litter_count,0);self.assertEqual(g.mall.cleanliness,1)
        self.assertEqual(g.owner_requests.progress,0)
        positions={k:j.position.copy() for k,j in g.janitors.people.items()}
        for _ in range(100):g.janitors.update(.5,g)
        self.assertTrue(any(j.position!=positions[k] for k,j in g.janitors.people.items()))

    def test_modal_pauses_janitor_walking_and_work(self):
        g=self.game;j,trash=self.isolated_work();g.janitors.update(2,g);cash=g.cash
        for modal in (g.journal,g.shop_menu,g.owner_menu,g.display_menu,g.welcome):
            modal.open=True;before=(j.position.copy(),j.progress,j.cleaned)
            g.update(100,(0,0));self.assertEqual((j.position,j.progress,j.cleaned),before);modal.open=False
        self.assertEqual(g.cash,cash);self.assertFalse(trash.cleaned)

    def test_journal_mouse_keyboard_hiring_and_upgrades(self):
        g=self.game;g.cash=100000;g.journal.open=True
        g.journal.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_2),g)
        self.assertEqual(g.journal.tab,1)
        g.journal.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        self.assertEqual(len(g.janitors.people),1)
        g.journal.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_c),g)
        self.assertEqual(g.janitors.people['north'].clean_seconds,4)
        row=g.journal.staff_rows(g.screen)[0]
        g.journal.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=g.journal.staff_buttons(row)['walk'].center),g)
        self.assertEqual(g.janitors.people['north'].speed,64)
        g.screen=pygame.display.set_mode((800,600));g.draw()
        panel,_=g.journal.geometry(g.screen)
        self.assertTrue(all(panel.contains(r) for r in g.journal.staff_rows(g.screen)))
        g.journal.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_1),g);self.assertEqual(g.journal.tab,0)

    def test_north_janitor_cannot_pick_up_east_litter(self):
        self.open_all();g=self.game
        for trash in g.mall.trash:g.mall.clean_trash(trash)
        foreign=g.mall.east.trash[0];g.mall.respawn_trash(foreign)
        j=self.hire();before=g.cash
        for _ in range(50):g.janitors.update(1,g)
        self.assertFalse(foreign.cleaned);self.assertEqual(j.cleaned,0);self.assertEqual(g.cash,before)
