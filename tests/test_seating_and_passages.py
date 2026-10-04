"""Broken seating, intentional arcade layout and walk-through courtyard passages."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
import copy
from unittest.mock import patch
import pygame
from game.game import Game
from mall.furniture import bench_footprint
from systems.janitors import Janitor
from systems.saves import snapshot,restore_state
from systems.mall_life import EventSpot


class SeatingAndPassageTests(unittest.TestCase):
    def setUp(self):
        self.g=Game();self.g.welcome.open=False
    def tearDown(self):pygame.quit()

    def open_all(self):
        g=self.g
        for region in g.mall.regions:
            for t in g.mall.trash:g.mall.clean_trash(t)
            for s in g.mall.stores:s.restored=True
            g.mall.refresh_businesses();self.assertTrue(g.mall.unlock_section(region))
        for t in g.mall.trash:g.mall.clean_trash(t)
        for s in g.mall.stores:s.restored=True
        g.mall.refresh_businesses();g.cash=2000000

    def test_independent_bench_table_and_each_chair_in_all_four_sections(self):
        self.open_all();g=self.g
        g.shoppers.update(0,g.mall,g.upgrades,spawn=False)
        self.assertFalse(g.shoppers.table_seats(g.mall))
        for i,table in enumerate(g.mall.social_tables):
            section=('north','east','garden','commons')[i//2]
            self.assertEqual(table.fixture_key,f'table_{i}');self.assertEqual(table.section,section)
            price=(70,140,600,900)[i//2];cash=5000
            cash,_,bought=g.upgrades.purchase(f'bench_{i}',cash,section)
            self.assertTrue(bought);self.assertEqual(cash,5000-price)
            self.assertEqual(table.sprite(g.upgrades.decor),'social_table_broken')
            self.assertFalse(any(t is table for t,_ in g.shoppers.table_seats(g.mall)))
            before=cash;cash,_,bought=g.upgrades.purchase(table.seat_keys[0],cash,section)
            self.assertFalse(bought);self.assertEqual(cash,before)
            cash,_,bought=g.upgrades.purchase(table.fixture_key,cash,section)
            self.assertTrue(bought);self.assertEqual(cash,5000-2*price)
            self.assertEqual(table.sprite(g.upgrades.decor),'social_table_1_00')
            self.assertFalse(any(t is table for t,_ in g.shoppers.table_seats(g.mall)))
            for seat,key in enumerate(table.seat_keys):
                cash,_,bought=g.upgrades.purchase(key,cash,section)
                self.assertTrue(bought)
                self.assertEqual(sum(t is table for t,_ in g.shoppers.table_seats(g.mall)),seat+1)
                before=cash;cash,_,bought=g.upgrades.purchase(key,cash,section)
                self.assertFalse(bought);self.assertEqual(cash,before)
            self.assertEqual(table.sprite(g.upgrades.decor),'social_table')
        restored=set(g.upgrades.decor);restore_state(snapshot(g),g)
        self.assertEqual(g.upgrades.decor,restored)
        self.assertTrue(all(t.sprite(g.upgrades.decor)=='social_table' for t in g.mall.social_tables))

    def test_starting_layout_has_two_aligned_bays_and_clear_cleanup_and_store_routes(self):
        g=self.g;m=g.mall
        self.assertEqual(len(m.north_trash),63)
        self.assertEqual(tuple(m.north_trash[0].position),(240,480))
        self.assertEqual(tuple(m.north_trash[-1].position),(1671,903))
        worker=Janitor('north',m.opening_area,(240,430),m)
        for t in m.north_trash:
            self.assertIsNotNone(worker.route_to(t.position,m),tuple(t.position))
            rect=pygame.FRect(t.position.x-13,t.position.y-15,26,30)
            self.assertFalse(any(w.colliderect(rect) for w in m.obstacles),tuple(t.position))
        for area,table,bench in zip(m.seating_areas,m.social_tables,m.benches):
            self.assertTrue(area.contains(table.footprint));self.assertTrue(area.contains(bench_footprint(bench)))
            self.assertEqual(table.position.x,bench.centerx)
            self.assertLess(table.position.y,bench.centery)
            for seat in table.seats:self.assertIsNotNone(worker.paths.route(m.entrance,seat))
        for store in m.stores:self.assertIsNotNone(worker.paths.route(m.entrance,store.position))
        self.assertIsNotNone(worker.paths.route(m.entrance,m.delivery.position))

    def test_walk_through_both_openings_without_interaction_or_bouncing(self):
        self.open_all();g=self.g;y=g.courtyard.door(g.mall).position.y
        g.player.rect.center=(3520,y);cash=g.cash
        g.interact();self.assertEqual(g.scene,'courtyard');self.assertEqual(g.cash,cash-50000)
        g.update(.1,(1,0));self.assertEqual(g.scene,'courtyard')
        g.player.rect.center=(80,775);g.update(.1,(-1,0));self.assertEqual(g.scene,'mall')
        g.update(.1,(-1,0));self.assertEqual(g.scene,'mall')
        g.player.rect.center=(3520,y);cash=g.cash;g.update(.1,(1,0))
        self.assertEqual(g.scene,'courtyard');self.assertEqual(g.cash,cash)
        for world,x,y in ((g.mall,3560,y),(g.courtyard.world,0,775)):
            self.assertFalse(any(w.clipline((x-20,y),(x+60,y)) for w in world.obstacles))
            self.assertTrue(any(w.clipline((x-20,y+140),(x+60,y+140)) for w in world.obstacles))

    def test_locked_or_paused_crossing_does_not_charge_or_switch_maps(self):
        self.open_all();g=self.g;y=g.courtyard.door(g.mall).position.y
        g.cash=49999;g.player.rect.center=(3530,y);g.update(.05,(1,0))
        self.assertEqual(g.scene,'mall');self.assertEqual(g.cash,49999);self.assertFalse(g.courtyard.unlocked)
        g.cash=100000;g.pause.open=True;g.update(1,(1,0))
        self.assertEqual(g.scene,'mall');self.assertEqual(g.cash,100000)
        g.pause.open=False;g.player.rect.center=(3530,y+180);g.update(.1,(1,0))
        self.assertEqual(g.scene,'mall');self.assertEqual(g.cash,100000)

    def test_continue_preserves_passage_and_free_walk_in_both_directions(self):
        self.open_all();g=self.g;g.enter_courtyard(save=False);g.leave_courtyard()
        saved=snapshot(g);saved.pop('seating_layout')
        restore_state(saved,g);g.welcome.open=False
        g.player.rect.center=(3520,g.courtyard.door(g.mall).position.y);cash=g.cash
        g.update(.1,(1,0));self.assertEqual(g.scene,'courtyard');self.assertEqual(g.cash,cash)
        restore_state(snapshot(g),g);g.player.rect.center=(80,775)
        g.update(.1,(-1,0));self.assertEqual(g.scene,'mall')

    def test_legacy_worker_player_and_gathering_move_off_reorganized_furniture(self):
        self.open_all();g=self.g
        g.janitors.people['north']=Janitor('north',g.mall.opening_area,(240,430),g.mall)
        g.janitors.people['north'].position=pygame.Vector2(860,750)
        g.player.rect.center=(860,750)
        g.life.active='north';g.life.spot=EventSpot(pygame.Vector2(860,830),g.life.event.title)
        g.life.round=1;g.life.participants=['Alex']
        saved=snapshot(g);saved.pop('seating_layout');restore_state(saved,g)
        self.assertEqual(g.life.round,1);self.assertEqual(g.life.participants,['Alex'])
        self.assertNotEqual(g.life.spot.position,pygame.Vector2(860,830))
        self.assertNotEqual(g.player.rect.center,(860,750))
        self.assertNotEqual(g.janitors.people['north'].position,pygame.Vector2(860,750))
        self.assertEqual(snapshot(g)['seating_layout'],3)

    def test_table_purchase_leaves_bench_and_other_chairs_broken(self):
        g=self.g;table=g.mall.social_tables[0]
        self.assertTrue(g.upgrades.purchase('table_0',100,'north')[2])
        self.assertNotIn('bench_0',g.upgrades.decor)
        self.assertTrue(g.upgrades.purchase('table_0_seat_0',100,'north')[2])
        self.assertEqual(table.sprite(g.upgrades.decor),'social_table_1_10')
        self.assertNotIn('table_0_seat_1',g.upgrades.decor)
        self.assertEqual(g.mall.social_tables[1].sprite(g.upgrades.decor),'social_table_broken')
        before=set(g.upgrades.decor)
        self.assertFalse(g.upgrades.purchase('table_2',1000,'north')[2]);self.assertEqual(g.upgrades.decor,before)

    def test_old_bundle_purchases_migrate_but_new_bench_only_saves_do_not(self):
        self.open_all();g=self.g
        g.upgrades.decor.update(('bench_0','bench_2','bench_4','bench_6'))
        saved=snapshot(g);legacy=copy.deepcopy(saved);legacy['seating_layout']=2
        restore_state(legacy,g)
        for i in (0,2,4,6):
            self.assertTrue({f'table_{i}',f'table_{i}_seat_0',f'table_{i}_seat_1'}<=g.upgrades.decor)
            self.assertNotIn(f'table_{i+1}',g.upgrades.decor)
        restore_state(saved,g);self.assertEqual(g.upgrades.decor,{'bench_0','bench_2','bench_4','bench_6'})
        bad=copy.deepcopy(saved);bad['fixtures'].append('table_0_seat_0')
        before=snapshot(g)
        with self.assertRaises(ValueError):restore_state(bad,g)
        self.assertEqual(snapshot(g),before)

    def test_every_fountain_mosaic_tracks_the_fountain_position(self):
        self.open_all();g=self.g
        g.upgrades.decor.update(('mosaic','mosaic_east','mosaic_garden','mosaic_commons'))
        g.mall.fountain.move_ip(13,17)
        with patch.object(g.art,'draw',wraps=g.art.draw) as draw:
            g.mall.draw(g.screen,g.camera,g.hud.font,g.art,None,g.upgrades)
        points=[tuple(call.args[2]) for call in draw.call_args_list if call.args[1]=='mosaic']
        expected=[tuple(g.camera.point((f.centerx,f.bottom+90))) for f in [g.mall.fountain]+[r.fountain for r in g.mall.regions]]
        self.assertCountEqual(points,expected)

    def test_scrolling_shop_reaches_every_purchase_at_minimum_resolution(self):
        self.open_all();g=self.g;g.screen=pygame.display.set_mode((800,600))
        shop=g.shop_menu;shop.open=True;shop.category=1
        for section in ('north','east','garden','commons'):
            shop.shop=section;shop.selection=shop.scroll=0;seen=set()
            for _ in range(len(shop.offers(g))):
                rows=shop.rows(g);seen.update(o.key for o,_ in rows)
                panel,_=shop.geometry(g.screen)
                self.assertTrue(all(rect.bottom<panel.bottom-100 for _,rect in rows))
                shop.draw(g);shop.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN),g)
            self.assertEqual(seen,{o.key for o in shop.offers(g)})
            shop.handle(pygame.event.Event(pygame.MOUSEWHEEL,y=-9),g)
            rows=shop.rows(g);key,rect=rows[-1]
            shop.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center),g)
            before=set(g.upgrades.decor);shop.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=shop.purchase_rect(g).center),g)
            self.assertEqual(g.upgrades.decor,before|{key.key})

    def test_courtyard_sign_unlock_cost_is_explicit_and_persists(self):
        self.open_all();g=self.g;y=g.courtyard.door(g.mall).position.y
        g.player.rect.center=(3530,y);cash=g.cash;g.update(.1,(1,0))
        self.assertEqual(g.scene,'mall');self.assertEqual(g.cash,cash)
        self.assertFalse(g.courtyard.unlocked);self.assertIn('$50,000',g.message)
        g.cash=49999;g.interact();self.assertEqual(g.cash,49999);self.assertEqual(g.scene,'mall')
        g.cash=50000;g.interact();self.assertEqual(g.cash,0);self.assertEqual(g.scene,'courtyard')
        g.leave_courtyard();restore_state(snapshot(g),g)
        g.player.rect.center=(3530,y);g.update(.1,(1,0))
        self.assertEqual(g.scene,'courtyard');self.assertEqual(g.cash,0)

    def test_broken_art_is_distinct_from_restored_art(self):
        art=self.g.art
        for broken,restored in (('bench_dirty','bench_clean'),('social_table_broken','social_table')):
            self.assertNotEqual(pygame.image.tobytes(art.sprites[broken],'RGBA'),pygame.image.tobytes(art.sprites[restored],'RGBA'))
        self.g.screen=pygame.display.set_mode((800,600));self.g.draw()

if __name__=='__main__':unittest.main()
