"""Broken seating, intentional arcade layout and walk-through courtyard passages."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
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

    def test_every_indoor_section_starts_broken_and_restores_its_own_seating(self):
        self.open_all();g=self.g
        g.shoppers.update(0,g.mall,g.upgrades,spawn=False)
        self.assertFalse(g.shoppers.table_seats(g.mall))
        for i,table in enumerate(g.mall.social_tables):
            section=('north','east','garden','commons')[i//2]
            self.assertEqual(table.fixture_key,f'bench_{i}')
            self.assertEqual(table.section,section)
            before=g.mall.furniture(g.upgrades)
            self.assertEqual(next(row[1] for row in before if row[2] is table.position),'social_table_broken')
            cash=g.cash;self.assertTrue(g.upgrades.purchase(f'bench_{i}',cash,section)[2])
            after=g.mall.furniture(g.upgrades)
            self.assertEqual(next(row[1] for row in after if row[2] is table.position),'social_table')
            self.assertEqual(after[1+len(g.mall.active_regions)+i][1],'bench_clean')
            self.assertEqual(sum(t is table for t,_ in g.shoppers.table_seats(g.mall)),2)
        restored=set(g.upgrades.decor);restore_state(snapshot(g),g)
        self.assertEqual(g.upgrades.decor,restored)
        self.assertTrue(all(name=='social_table' for _,name,_,_ in g.mall.furniture(g.upgrades) if name.startswith('social_table')))

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
        g.update(.1,(1,0));self.assertEqual(g.scene,'courtyard');self.assertEqual(g.cash,cash-50000)
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
        self.assertEqual(snapshot(g)['seating_layout'],2)

    def test_broken_art_is_distinct_from_restored_art(self):
        art=self.g.art
        for broken,restored in (('bench_dirty','bench_clean'),('social_table_broken','social_table')):
            self.assertNotEqual(pygame.image.tobytes(art.sprites[broken],'RGBA'),pygame.image.tobytes(art.sprites[restored],'RGBA'))
        self.g.screen=pygame.display.set_mode((800,600));self.g.draw()

if __name__=='__main__':unittest.main()
