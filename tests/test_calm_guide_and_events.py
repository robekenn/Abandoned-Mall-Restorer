import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.saves import snapshot,restore_state


class CalmGuideTests(unittest.TestCase):
    def setUp(self):self.g=Game()
    def tearDown(self):pygame.quit()
    def key(self,key):self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))

    def open_all(self):
        g=self.g
        for region in [None]+g.mall.regions:
            if region:g.mall.unlock_section(region)
            for t in g.mall.trash:g.mall.clean_trash(t)
            for s in g.mall.stores:s.restored=True
            g.mall.refresh_businesses()
        return g

    def test_explanation_freezes_world_and_consumes_interaction(self):
        g=self.g;g.tutorial.start(g);before=snapshot(g)
        g.update(100,(1,0),True);self.key(pygame.K_e);g.interact()
        self.assertEqual(snapshot(g),before)
        self.key(pygame.K_j);self.assertFalse(g.journal.open)
        self.key(pygame.K_RETURN);g.update(.2,(1,0))
        self.assertEqual(g.tutorial.step,1);self.assertTrue(g.tutorial.paused)
        position=g.player.rect.center;g.update(10,(1,0));self.assertEqual(g.player.rect.center,position)
        self.key(pygame.K_t);self.assertFalse(g.tutorial.active)

    def test_explanation_and_practice_both_survive_continue(self):
        g=self.g;g.tutorial.start(g)
        h=Game();restore_state(snapshot(g),h);self.assertTrue(h.tutorial.paused)
        self.key(pygame.K_RETURN);restore_state(snapshot(g),h);self.assertFalse(h.tutorial.paused)
        legacy=snapshot(g);del legacy['tutorial']['explaining']
        restore_state(legacy,h);self.assertTrue(h.tutorial.paused)

    def test_recurring_wait_drawn_once_after_third_project_and_each_favor(self):
        g=self.open_all();s=g.mall.stores[1];s.request_level=2;s.request_wait=0
        g.owner_requests.accept(s,g.mall)
        for spot in g.owner_requests.spots:spot.completed=True
        g.owner_requests.greetings={1,2,3}
        with patch('systems.requests.random.uniform',return_value=599) as draw:
            self.assertTrue(g.claim_request(s));draw.assert_called_once_with(180,600)
        self.assertEqual(s.request_wait,599)
        g.owner_requests.update(180,g.mall);self.assertFalse(g.owner_requests.eligible(s))
        h=Game();restore_state(snapshot(g),h)
        self.assertEqual(h.mall.stores[1].request_wait,419)
        g.owner_requests.update(419,g.mall);self.assertTrue(g.owner_requests.accept(s,g.mall))
        for spot in g.owner_requests.spots:spot.completed=True
        g.owner_requests.progress=99;g.owner_requests.greetings=set(range(20));g.owner_requests.parcel=True
        with patch('systems.requests.random.uniform',return_value=180):self.assertTrue(g.claim_request(s))
        self.assertEqual(s.request_wait,180)
        data=snapshot(g);data['stores'][s.name][4]=601
        with self.assertRaises(ValueError):restore_state(data,h)

    def test_events_have_distinct_activities_routes_and_saved_task_progress(self):
        g=self.open_all();activities=set();positions=[]
        for key in ('north','east','garden','commons'):
            g.player.rect.center=g.mall.entrance
            self.assertTrue(g.life.start(g,key));activities.add(g.life.activity);positions.append(g.life.spot.position.copy())
            for task in g.life.tasks:
                self.assertIsNotNone(g.shoppers.walkways.route(g.mall.entrance,task.position))
            if g.life.tasks:
                self.assertFalse(g.life.choose(g,0));self.assertEqual(g.life.round,0)
                task=g.life.tasks[0];g.player.rect.center=task.position
                if task.duration:
                    g.life.work(1,g,True,True);self.assertFalse(task.completed)
                    g.life.work(1,g,True,True)
                else:g.life.touch(g,task)
                data=snapshot(g);h=Game();restore_state(data,h)
                self.assertEqual(h.life.round,1)
                self.assertEqual([t.position for t in h.life.tasks],[t.position for t in g.life.tasks])
                self.assertEqual(h.life.activity,g.life.activity)
                for task in g.life.visible_tasks:
                    g.player.rect.center=task.position
                    if task.duration:g.life.work(2,g,True,True)
                    else:g.life.touch(g,task)
            else:
                while g.life.round<3:
                    answer=g.life.round if g.life.activity=='recipe' else g.life.guest(g.life.round)[2]
                    self.assertTrue(g.life.choose(g,answer))
            cash=g.cash;self.assertTrue(g.life.choose(g,0));self.assertGreater(g.cash,cash)
            self.assertFalse(g.life.choose(g,0));self.assertEqual(g.life.tasks,[])
        self.assertEqual(activities,{'match','recipe','plant','hunt'})

    def test_event_marker_interaction_takes_priority_over_litter_on_its_tile(self):
        g=self.open_all();g.life.completed['north']=3
        self.assertTrue(g.life.start(g,'north'))
        task=g.life.tasks[0];trash=g.mall.trash[0]
        trash.position=task.position.copy();trash.cleaned=False
        g.player.rect.center=task.position
        self.assertIs(g.target(),task);g.interact()
        self.assertTrue(task.completed);self.assertFalse(trash.cleaned)
        self.assertEqual(g.life.round,1)

    def test_old_active_gathering_retains_matching_rules(self):
        g=self.open_all();g.life.start(g,'east');data=snapshot(g)
        del data['life']['activity'];del data['life']['tasks']
        h=Game();restore_state(data,h);self.assertEqual(h.life.activity,'match')
        self.assertTrue(h.life.choose(h,h.life.guest(0)[2]))

    def test_new_story_board_layout_and_legacy_discoveries_remain_stable(self):
        g=self.g;data=snapshot(g);h=Game();restore_state(data,h)
        self.assertEqual([p.position for p in g.story.points],[p.position for p in h.story.points])
        del data['story']['layout'];restore_state(data,h);self.assertEqual(h.story.layout,1)
        old=[p.position.copy() for p in h.story.points];restore_state(snapshot(h),h)
        self.assertEqual(old,[p.position for p in h.story.points])

    def test_all_event_menus_and_explanations_render_at_800_by_600(self):
        g=self.open_all();g.screen=pygame.display.set_mode((800,600))
        g.tutorial.start(g)
        for step in range(5):g.tutorial.step=step;g.draw()
        g.tutorial.skip()
        for key in ('north','east','garden','commons'):
            g.life.active=None;g.life.spot=None;g.life.tasks=[];g.life.sync_spots(g.mall)
            self.assertTrue(g.life.start(g,key));g.community_menu.open=True;g.draw();g.community_menu.open=False
        self.assertEqual(len({pygame.image.tobytes(g.art.sprites[f'chapter_board_{i}'],'RGBA') for i in range(4)}),4)
