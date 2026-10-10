"""Checkpoints, four story claims and helper-friendly recurring cleanup."""
import copy
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import pygame
from game.game import Game
from systems.favors import FAVORS
from systems.requests import OWNERS
from systems.saves import canonical, snapshot, restore_state
from systems.story import CHAPTERS


class StoryAndSaveTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.game=Game(developer=True,persistence=True,save_dir=self.directory.name)
    def tearDown(self):pygame.quit();self.directory.cleanup()

    def clone(self):return Game(developer=True,persistence=True,save_dir=self.directory.name)

    def prepare(self):self.assertTrue(self.game.story.prepare(self.game))

    def finish_story(self):
        for i in range(4):
            self.prepare();self.assertTrue(self.game.story.confirm(self.game,i,'claim'))
        self.assertTrue(self.game.story.confirm(self.game,3,'festival'))

    def envelope(self, data, path=None):
        content=canonical({'version':1,'data':data,'checksum':hashlib.sha256(canonical(data)).hexdigest()})
        (path or self.game.save_store.path).write_bytes(content)

    def test_story_claim_requires_actual_care_and_rewards_only_once(self):
        g=self.game;board=g.story.points[0]
        self.assertTrue(g.story.action(board,g));self.assertEqual(g.story_menu.action,'begin')
        self.assertTrue(g.story.confirm(g,0,'begin'));self.assertFalse(g.story.confirm(g,0,'claim'))
        self.prepare();before=g.cash
        self.assertTrue(g.story.confirm(g,0,'claim'));self.assertEqual(g.cash-before,1000)
        self.assertFalse(g.story.confirm(g,0,'claim'));self.assertEqual(g.cash-before,1000)
        self.assertFalse(g.story.confirm(g,2,'claim'))
        self.assertEqual(g.story.current,1)

    def test_all_four_chapters_and_final_walk_keep_regular_game_playable(self):
        g=self.game;self.finish_story()
        self.assertEqual(g.cash,sum(c.reward for c in CHAPTERS));self.assertEqual(g.story.current,4)
        g.story.update(0,g.mall);self.assertEqual(len(g.mall.community_spots),12)
        before=g.cash;self.assertTrue(g.story.confirm(g,3,'festival'));self.assertEqual(g.cash,before)
        g.story_menu.open=False;g.story.update(61,g.mall);self.assertEqual(g.mall.community_spots,[])
        g.story.update(89,g.mall);self.assertEqual(len(g.mall.community_spots),12)
        self.assertTrue(g.story.confirm(g,0,'gather'));self.assertEqual(g.cash,before)
        g.shoppers.update(8,g.mall,g.upgrades)
        self.assertTrue(g.shoppers.people)
        self.assertLessEqual(len(g.shoppers.people),g.shoppers.population_limit(g.mall))
        self.assertTrue(any(p.state in ('strolling','resting') for p in g.shoppers.people))
        self.assertFalse(g.developer.act('story',g))

    def test_keepsakes_do_not_use_bag_and_all_markers_have_safe_routes(self):
        g=self.game;g.story.confirm(g,0,'begin');g.upgrades.held=1
        points=[p for p in g.story.visible_points(g.mall)+g.story.visible_neighbors(g.mall) if p.memory>=0]
        for point in points:self.assertTrue(g.story.action(point,g));g.story_menu.open=False
        self.assertEqual(g.upgrades.held,1);self.assertEqual(g.story.memories[0],[True]*3)
        self.assertFalse(g.story.action(next(p for p in points if p.source=='ground'),g))
        self.finish_story();g.shoppers.walkways.refresh(g.mall)
        for point in g.story.points:
            footprint=pygame.FRect(point.position.x-13,point.position.y-15,26,30)
            self.assertFalse(any(w.colliderect(footprint) for w in g.mall.obstacles))
            self.assertIsNotNone(g.shoppers.walkways.route(g.player.rect.center,point.position))

    def test_story_modal_pauses_timers_and_claim_keyboard_saves(self):
        g=self.game;self.prepare();g.story.action(g.story.points[0],g)
        before=(g.cash,g.story.elapsed,g.rent_timer,g.save_store.elapsed)
        g.update(100,(1,0));self.assertEqual((g.cash,g.story.elapsed,g.rent_timer,g.save_store.elapsed),before)
        g.story_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        self.assertFalse(g.story_menu.open);self.assertTrue(g.story.completed[0])
        h=self.clone();self.assertTrue(h.save_store.load(h));self.assertTrue(h.story.completed[0])

    def test_story_journal_and_dialogues_render_at_minimum_window(self):
        g=self.game;g.screen=pygame.display.set_mode((800,600));self.finish_story()
        g.story_menu.open=False;g.journal.open=True
        g.journal.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_3),g)
        self.assertEqual(g.journal.chapter,3)
        for i in range(4):
            g.journal.chapter=i
            for memories in (False,True):g.journal.memories_view=memories;g.draw()
        g.journal.open=False
        for i,c in enumerate(CHAPTERS):
            for text in (c.opening,c.ending,*c.memories):g.story_menu.visit(i,text,None);g.draw()

    def test_full_story_roundtrip_preserves_progress_economy_and_timers(self):
        g=self.game;self.finish_story();g.story_menu.open=False
        g.cash=12345.75;g.upgrades.capacity_level=2;g.upgrades.held=3;g.total_collected=19;g.total_sold=16
        g.rent_timer=3.5;g.litter_spawner.elapsed=2.5;g.litter_spawner.turn=3;g.audio.toggle()
        g.tutorial.start(g);g.tutorial.step=2
        self.assertTrue(g.save_checkpoint());h=self.clone();self.assertTrue(h.save_store.load(h))
        self.assertEqual(snapshot(g),snapshot(h));self.assertTrue(h.story.festival)
        self.assertEqual(h.cash,12345.75)  # No elapsed-wall-clock/offline payout.

    def test_active_original_projects_resume_and_claim_once(self):
        g=self.game;store=g.mall.north_stores[1];store.restored=True
        for level in range(3):
            with self.subTest(level=level):
                store.request_level=level;store.request_wait=0
                self.assertTrue(g.owner_requests.accept(store,g.mall))
                request=g.owner_requests
                if level==0:request.interact(request.spots[0])
                elif level==1:request.arrange_display(request.display_plan)
                else:request.spots[0].progress=1.25;request.greetings={11,17}
                self.assertTrue(g.save_checkpoint());h=self.clone();self.assertTrue(h.save_store.load(h))
                r=h.owner_requests;self.assertEqual(r.store.request_level,level)
                if level==2:
                    self.assertEqual(r.spots[0].progress,1.25);self.assertEqual(r.greetings,{11,17})
                    self.assertGreater(h.shoppers.next_identity,17)
                    r.spots[0].completed=True;r.greetings.add(23)
                self.assertTrue(r.ready);before=h.cash;self.assertTrue(h.claim_request(r.store))
                self.assertGreater(h.cash,before);self.assertIsNone(r.claim(h.mall.north_stores[1]))
                request.store=None;request.spots=[];request.greetings.clear()

    def test_all_repeatable_request_modes_resume_state(self):
        g=self.game;store=g.mall.north_stores[1];store.restored=True;store.request_level=3
        for index,favor in enumerate(FAVORS):
            with self.subTest(mode=favor.mode):
                store.request_wait=0;store.recurring_completed=(index-list(OWNERS).index(store.name))%len(FAVORS)
                self.assertTrue(g.owner_requests.accept(store,g.mall));r=g.owner_requests
                if favor.mode in ('collect','sell'):r.progress=2
                if r.needs_greetings:r.greetings={2}
                if r.spots:
                    r.spots[0].completed=True;r.spots[0].progress=r.spots[0].duration
                    if r.spots[0].kind=='parcel':r.parcel=True
                self.assertTrue(g.save_checkpoint());h=self.clone();self.assertTrue(h.save_store.load(h))
                self.assertEqual(snapshot(g)['request'],snapshot(h)['request'])
                self.assertEqual(h.owner_requests.favor,favor)
                r.store=None;r.spots=[];r.favor=None;r.greetings.clear()

    def test_janitor_resumes_mid_work_and_pays_remaining_time_once(self):
        g=self.game;g.cash=10000;g.janitors.purchase('north','hire',g);j=g.janitors.people['north']
        for t in g.mall.trash:g.mall.clean_trash(t)
        trash=next(t for t in g.mall.trash if tuple(t.position) in j.paths.nodes)
        g.mall.respawn_trash(trash);j.position=trash.position.copy();g.janitors.update(3,g)
        self.assertEqual(j.progress,3);self.assertTrue(g.save_checkpoint())
        h=self.clone();self.assertTrue(h.save_store.load(h));worker=h.janitors.people['north'];before=h.cash
        h.janitors.update(1.99,h);self.assertEqual(worker.cleaned,0)
        h.janitors.update(.01,h);self.assertEqual(worker.cleaned,1);self.assertEqual(h.cash,before+.75)

    def test_checksum_damage_recovers_previous_checkpoint_and_keeps_backup(self):
        g=self.game;g.cash=10;g.save_checkpoint();g.cash=20;g.save_checkpoint()
        g.save_store.path.write_text('{truncated')
        h=self.clone();self.assertTrue(h.save_store.load(h));self.assertEqual(h.cash,10)
        self.assertEqual(h.save_store.status,'Recovered backup')
        h.cash=30;h.save_checkpoint();h.save_store.path.write_text('broken')
        other=self.clone();self.assertTrue(other.save_store.load(other));self.assertEqual(other.cash,10)

    def test_semantic_damage_does_not_partly_replace_live_world(self):
        g=self.game;g.save_checkpoint();data=snapshot(g);data['story']['festival']=True;self.envelope(data)
        g.cash=777;mall=g.mall;player=g.player
        self.assertFalse(g.save_store.load(g));self.assertEqual(g.cash,777)
        self.assertIs(g.mall,mall);self.assertIs(g.player,player)
        for value in (float('inf'),-1,True):
            bad=copy.deepcopy(data);bad['cash']=value
            with self.assertRaises(ValueError):restore_state(bad,g)
            self.assertIs(g.mall,mall)

    def test_semantically_invalid_primary_recovers_valid_backup(self):
        g=self.game;g.cash=10;g.save_checkpoint();g.cash=20;g.save_checkpoint()
        data=snapshot(g);data['held']=500;self.envelope(data)
        h=self.clone();self.assertTrue(h.save_store.load(h));self.assertEqual(h.cash,10)
        h.cash=30;h.save_checkpoint();h.save_store.path.write_text('broken')
        other=self.clone();self.assertTrue(other.save_store.load(other));self.assertEqual(other.cash,10)

    def test_failed_atomic_replace_preserves_primary_and_removes_temporary_file(self):
        g=self.game;g.cash=10;g.save_checkpoint();previous=g.save_store.path.read_bytes();g.cash=20
        with patch('game.storage.os.replace',side_effect=OSError('disk error')):self.assertFalse(g.save_checkpoint())
        self.assertEqual(g.save_store.path.read_bytes(),previous)
        self.assertEqual(list(Path(self.directory.name).glob('*.tmp')),[])

    def test_normal_and_developer_slots_never_overwrite_each_other(self):
        dev=self.game;dev.cash=1000000;dev.save_checkpoint()
        normal=Game(persistence=True,save_dir=self.directory.name);self.assertFalse(normal.welcome.has_save)
        normal.cash=9;normal.save_checkpoint();dev.cash=7;dev.save_checkpoint()
        h=Game(persistence=True,save_dir=self.directory.name);self.assertTrue(h.save_store.load(h));self.assertEqual(h.cash,9)
        self.assertNotEqual(dev.save_store.path,normal.save_store.path)

    def test_intro_continue_and_new_game_confirmation_do_not_overwrite_on_launch(self):
        g=self.game;g.cash=123;g.tutorial.start(g);g.tutorial.step=3;g.save_checkpoint()
        h=Game(developer=True,persistence=True,save_dir=self.directory.name,start_screen=True)
        self.assertTrue(h.welcome.has_save);self.assertFalse(h.save_started);self.assertFalse(h.save_checkpoint())
        self.assertTrue(h.continue_game());h.update(.9,(0,0))
        self.assertEqual(h.cash,123);self.assertEqual(h.tutorial.step,3);self.assertTrue(h.save_started)
        fresh=Game(developer=True,persistence=True,save_dir=self.directory.name,start_screen=True)
        fresh.welcome.choose_new();self.assertFalse(fresh.welcome.leaving)
        fresh.welcome.choose_new();fresh.update(.9,(0,0));self.assertEqual(fresh.cash,0)
        self.assertEqual(fresh.save_store.read(fresh.save_store.backup)['cash'],123)

    def test_autosave_contains_current_rent_and_pauses_with_menus(self):
        g=self.game;self.prepare();g.rent_timer=4;g.save_store.elapsed=29
        g.journal.open=True;g.update(2,(0,0));self.assertFalse(g.save_store.path.exists())
        g.journal.open=False;g.update(1,(0,0));self.assertTrue(g.save_store.path.exists())
        h=self.clone();self.assertTrue(h.save_store.load(h));self.assertEqual(h.cash,g.cash);self.assertGreater(h.cash,0)
        self.assertEqual(h.rent_timer,g.rent_timer)

    def test_manual_f5_and_exit_checkpoint(self):
        g=self.game;g.cash=45
        events=[[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F5)],[pygame.event.Event(pygame.QUIT)],
                 [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN),pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN)]]
        with patch('pygame.event.get',side_effect=events),patch.object(g,'draw'),patch.object(g,'update'):g.run()
        h=self.clone();self.assertTrue(h.save_store.load(h));self.assertEqual(h.cash,45)

    def test_unsupported_version_is_rejected_without_new_game_damage(self):
        g=self.game;g.save_checkpoint();data=__import__('json').loads(g.save_store.path.read_text());data['version']=999
        g.save_store.path.write_text(__import__('json').dumps(data))
        self.assertFalse(g.save_store.available());self.assertFalse(g.save_store.load(g));self.assertEqual(g.cash,0)

    def test_litter_rotates_across_all_courts_at_one_global_interval(self):
        g=self.game;self.finish_story();g.story_menu.open=False
        for t in g.mall.trash:g.mall.clean_trash(t)
        # Last court's stores after sixth must be restored for later equipment only, not spawns.
        pools=g.mall.recurring_pools;self.assertEqual(len(pools),4)
        for count in range(1,5):
            g.litter_spawner.update(3.99,g.mall,(0,0));self.assertEqual(g.mall.active_litter_count,count-1)
            g.litter_spawner.update(.01,g.mall,(0,0));self.assertEqual(g.mall.active_litter_count,count)
        self.assertEqual([sum(not t.cleaned for t in pool) for pool in pools],[1,1,1,1])

    def test_helpers_preserve_only_the_litter_needed_for_collect_favor(self):
        g=self.game;self.prepare();g.cash=10000;g.janitors.purchase('north','hire',g)
        store=g.mall.north_stores[1];store.request_level=3;store.request_wait=0
        index=next(i for i,f in enumerate(FAVORS) if f.mode=='collect')
        store.recurring_completed=(index-list(OWNERS).index(store.name))%len(FAVORS)
        self.assertTrue(g.owner_requests.accept(store,g.mall));r=g.owner_requests;j=g.janitors.people['north']
        g.litter_spawner.turn=3;g.litter_spawner.update(4,g.mall,(0,0),r)
        self.assertEqual(g.mall.active_litter_count,1)
        trash=next(t for t in g.mall.north_trash if not t.cleaned);j.position=trash.position.copy()
        g.janitors.update(10,g);self.assertFalse(trash.cleaned);self.assertEqual(r.progress,0)
        g.player.rect.center=trash.position;g.collect(trash);self.assertTrue(trash.cleaned);self.assertEqual(r.progress,1)
        r.progress=r.amount;g.mall.respawn_trash(trash);j.position=trash.position.copy()
        g.janitors.update(5,g);self.assertTrue(trash.cleaned)
