"""Matching indoor seating bays, stable cleanup progress and compact wall signs."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import copy
import hashlib
import json
import unittest
from unittest.mock import Mock
from types import SimpleNamespace
import pygame
from game.game import Game
from mall.furniture import bench_footprint
from systems.janitors import Janitor
from systems.saves import snapshot,restore_state


class RegionalSeatingTests(unittest.TestCase):
    def setUp(self):self.g=Game();self.g.welcome.open=False
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

    def test_all_three_sections_have_matching_aligned_bays_and_clear_routes(self):
        self.open_all();g=self.g
        hashes={'east':'36b01da0c2a0985e1abaad0c3a03398ad0223bb09161fcd4ca756fd7d0fb41f4',
                'garden':'ac5fcdbaf3851259ead6fe94dce13d971476921ea9daa02ff5a6d9bc554b5474',
                'commons':'ffbcf83c61deee8c32f24a317609c1ea9a72badc96d78afe7bab8b20837fed44'}
        for r in g.mall.regions:
            with self.subTest(section=r.key):
                positions=[list(t.position) for t in r.trash]
                self.assertEqual(hashlib.sha256(json.dumps(positions).encode()).hexdigest(),hashes[r.key])
                self.assertEqual(len(r.social_tables),2);self.assertEqual(len(r.seating_areas),2)
                self.assertEqual(r.social_tables[0].position.y,r.social_tables[1].position.y)
                self.assertEqual(r.benches[0].centery,r.benches[1].centery)
                self.assertLess(r.social_tables[0].position.x,r.fountain.centerx)
                self.assertLess(r.fountain.centerx,r.social_tables[1].position.x)
                self.assertLess(r.bins[0].position.x,r.fountain.centerx)
                self.assertLess(r.fountain.centerx,r.bins[1].position.x)
                worker=Janitor(r.key,r.area,r.entrance,g.mall)
                for area,table,bench in zip(r.seating_areas,r.social_tables,r.benches):
                    self.assertEqual(table.position.x,bench.centerx)
                    self.assertLess(table.position.y,bench.centery)
                    self.assertTrue(area.contains(table.footprint));self.assertTrue(area.contains(bench_footprint(bench)))
                    self.assertIn(table,g.mall.social_tables)
                    for seat in table.seats:self.assertIsNotNone(worker.paths.route(r.entrance,seat))
                    self.assertIsNotNone(worker.paths.route(r.entrance,(bench.centerx,bench.bottom+40)))
                for t in r.trash:
                    self.assertIsNotNone(worker.route_to(t.position,g.mall),tuple(t.position))
                    body=pygame.FRect(t.position.x-13,t.position.y-15,26,30)
                    self.assertFalse(any(w.colliderect(body) for w in g.mall.obstacles))
                for store in r.stores:self.assertIsNotNone(worker.paths.route(r.entrance,store.position))
                self.assertIsNotNone(worker.paths.route(r.entrance,r.delivery.position))
        g.shoppers.walkways.refresh(g.mall)
        self.assertIsNotNone(g.shoppers.walkways.route(g.mall.entrance,g.courtyard.door(g.mall).position))

    def test_old_regional_workers_players_and_gatherings_relocate_without_losing_progress(self):
        self.open_all();g=self.g
        g.upgrades.decor.update(('bench_2','table_2','table_2_seat_0'))
        baseline=snapshot(g)
        for key in ('east','garden','commons'):
            region=next(r for r in g.mall.regions if r.key==key)
            saved=copy.deepcopy(baseline);saved['seating_layout']=3
            worker=list(region.bins[0].position);event=list(region.bins[1 if key=='garden' else 0].position)
            saved['player']=worker
            saved['janitors']={key:{'position':worker,'walk':1,'clean':1,'cleaned':17,'earnings':42,'target':None,'progress':0}}
            saved['life'].update(active=key,position=event,round=1,participants=['Alex'],activity='match',tasks=[])
            restore_state(saved,g)
            self.assertNotEqual(list(g.janitors.people[key].position),worker)
            self.assertNotEqual(list(g.player.rect.center),worker)
            self.assertNotEqual(list(g.life.spot.position),event)
            self.assertEqual(g.life.round,1);self.assertEqual(g.life.participants,['Alex'])
            self.assertEqual(g.janitors.people[key].cleaned,17);self.assertEqual(g.janitors.people[key].earnings,42)
            self.assertEqual(g.upgrades.decor,set(baseline['fixtures']))
            self.assertEqual(snapshot(g)['trash'],baseline['trash'])
            current=snapshot(g);restore_state(current,g);self.assertEqual(snapshot(g),current)

    def test_legacy_gathering_tasks_move_off_new_tables_and_keep_completion(self):
        self.open_all();g=self.g;saved=snapshot(g);saved['seating_layout']=3
        r=g.mall.garden;points=[list(t.position) for t in r.social_tables]+[list(r.bins[1].position)]
        saved['life']['completed']['garden']=3
        saved['life'].update(active='garden',position=[900,2450],round=1,participants=['Alex'],activity='hunt',
                             tasks=[[point,'Find the toolkit','toolkit',0,0,i==0] for i,point in enumerate(points)])
        restore_state(saved,g)
        self.assertEqual(g.life.round,1);self.assertEqual([t.completed for t in g.life.tasks],[True,False,False])
        self.assertTrue(all(list(t.position)!=old for t,old in zip(g.life.tasks,points)))
        current=snapshot(g);restore_state(current,g);self.assertEqual(snapshot(g),current)

    def test_small_destination_sign_clears_commons_board_and_uses_only_its_name(self):
        self.open_all();g=self.g
        point=next(p for p in g.story.points if p.chapter==3 and p.memory<0)
        board=pygame.Rect(point.position.x-36,point.position.y-52,72,72)
        sign=g.courtyard.sign_rect(g)
        self.assertEqual(sign.height,30);self.assertLess(sign.width,120)
        self.assertEqual(sign.right,g.mall.size[0]-40)
        self.assertFalse(sign.inflate(8,30).colliderect(board))
        font=g.hud.small;render=Mock(wraps=font.render)
        g.hud.small=SimpleNamespace(render=render,size=font.size)
        g.courtyard.draw_passage(g,g.courtyard.door(g.mall))
        self.assertEqual([call.args[0] for call in render.call_args_list],['Courtyard'])
        g.hud.small=font
        self.assertTrue(g.enter_courtyard(save=False));outside=g.courtyard.sign_rect(g)
        self.assertEqual(outside.height,30);self.assertLess(outside.width,190);self.assertEqual(outside.left,40)
        render.reset_mock();g.hud.small=SimpleNamespace(render=render,size=font.size)
        g.courtyard.draw_passage(g,g.courtyard.return_door)
        self.assertEqual([call.args[0] for call in render.call_args_list],['Community Commons'])
        g.hud.small=font
        g.screen=pygame.display.set_mode((800,600));g.player.rect.center=(120,775);g.frame_camera(g.screen.get_size());g.draw()
        g.leave_courtyard();g.player.rect.center=(3490,2212);g.frame_camera(g.screen.get_size());g.draw()

if __name__=='__main__':unittest.main()
