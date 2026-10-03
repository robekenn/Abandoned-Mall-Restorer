"""Community progression, save compatibility, safe visitors and deliberate exits."""
import os
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import tempfile
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.shoppers import Shopper
from systems.saves import snapshot, restore_state


def key(code):return pygame.event.Event(pygame.KEYDOWN,key=code)


class MallLifeTests(unittest.TestCase):
    def setUp(self):self.game=Game()
    def tearDown(self):pygame.quit()

    def restore_north(self):
        g=self.game
        for t in g.mall.trash:g.mall.clean_trash(t)
        for s in g.mall.stores:s.restored=True
        g.mall.refresh_businesses();g.shoppers.walkways.refresh(g.mall)
        return g

    def open_all(self):
        g=self.restore_north()
        for r in g.mall.regions:
            self.assertTrue(g.mall.unlock_section(r))
            for t in r.trash:g.mall.clean_trash(t)
            for s in r.stores:s.restored=True
            g.mall.refresh_businesses()
        return g

    def test_events_need_local_shops_and_cleanliness_and_only_one_runs(self):
        g=self.game;self.assertFalse(g.life.start(g,'north'));self.assertFalse(g.life.start(g,'east'))
        g.mall.stores[1].restored=g.mall.stores[2].restored=True
        self.assertFalse(g.life.start(g,'north'))
        for t in g.mall.trash:g.mall.clean_trash(t)
        self.assertTrue(g.life.start(g,'north'));self.assertFalse(g.life.start(g,'north'))
        self.assertTrue(g.mall.obstacles[-1]==g.mall.event_obstacle)
        self.assertFalse(g.mall.event_obstacle.collidepoint(g.life.spot.position))
        for goal in g.mall.event_spots:self.assertIsNotNone(g.shoppers.walkways.route(g.mall.entrance,goal))

    def test_all_four_events_pay_once_rotate_and_wait_five_minutes(self):
        g=self.open_all()
        for court in g.janitors.courts(g.mall):
            k=court[0];self.assertTrue(g.life.start(g,k));title=g.life.event.title;cash=g.cash
            for n in range(3):
                if g.life.tasks:
                    task=g.life.visible_tasks[0];g.player.rect.center=task.position
                    if task.duration:g.life.work(task.duration,g,True,True)
                    else:g.life.touch(g,task)
                    continue
                correct=g.life.round if g.life.activity=='recipe' else g.life.event.guests[n][2]
                self.assertFalse(g.life.choose(g,(correct+1)%3));self.assertEqual(g.life.round,n)
                self.assertTrue(g.life.choose(g,correct));self.assertEqual(g.cash,cash)
            self.assertTrue(g.life.choose(g,0));self.assertGreater(g.cash,cash)
            cash=g.cash;self.assertFalse(g.life.choose(g,0));self.assertEqual(g.cash,cash)
            self.assertFalse(g.life.start(g,k));self.assertEqual(g.life.completed[k],1)
            self.assertIsNone(g.mall.event_obstacle);self.assertEqual(g.mall.event_spots,[])
            self.assertNotEqual(g.life.gathering(k).title,title)
            g.life.update(299,g);self.assertFalse(g.life.start(g,k));g.life.update(1,g)
            self.assertTrue(g.life.start(g,k))
            # Complete this second gathering before moving to the next court.
            for n in range(3):
                if g.life.tasks:
                    task=g.life.visible_tasks[0];g.player.rect.center=task.position
                    if task.duration:g.life.work(task.duration,g,True,True)
                    else:g.life.touch(g,task)
                else:g.life.choose(g,g.life.round if g.life.activity=='recipe' else g.life.event.guests[n][2])
            g.life.choose(g,0)

    def test_gathering_and_owner_conversations_survive_json_save_and_old_slots_load(self):
        import json
        g=self.restore_north();s=g.mall.stores[1];first=g.life.chat(g,s);s.request_level=2
        second=g.life.chat(g,s);third=g.life.chat(g,s);self.assertNotEqual(first,third)
        self.assertNotEqual(second,third);self.assertTrue(g.life.start(g,'north'))
        g.life.choose(g,g.life.event.guests[0][2])
        data=json.loads(json.dumps(snapshot(g),sort_keys=True));h=Game();restore_state(data,h)
        self.assertEqual(list(h.life.completed),['north','east','garden','commons'])
        self.assertEqual((h.life.active,h.life.round,h.life.owner_chats),(g.life.active,1,g.life.owner_chats))
        self.assertEqual(h.life.spot.position,g.life.spot.position);self.assertIn(h.mall.event_obstacle,h.mall.obstacles)
        self.assertEqual(h.life.event.title,g.life.event.title);self.assertEqual(h.life.participants,g.life.participants)
        del data['life'];legacy=Game();restore_state(data,legacy);self.assertIsNone(legacy.life.spot)
        data=snapshot(g);data['life']['position']=[0,0];before=h.mall
        with self.assertRaises(ValueError):restore_state(data,h)
        self.assertIs(h.mall,before)

    def test_pause_freezes_work_events_income_and_movement_and_esc_resumes(self):
        g=self.restore_north();g.life.start(g,'north');g.handle_event(key(pygame.K_ESCAPE))
        before=(g.cash,g.player.rect.center,g.rent_timer,g.litter_spawner.elapsed,g.life.elapsed,g.life.cooldowns.copy())
        g.update(300,(1,0),True);g.interact();g.draw()
        self.assertEqual(before,(g.cash,g.player.rect.center,g.rent_timer,g.litter_spawner.elapsed,g.life.elapsed,g.life.cooldowns.copy()))
        g.handle_event(key(pygame.K_ESCAPE));self.assertFalse(g.pause.open);self.assertTrue(g.running)

    def test_exit_defaults_to_stay_and_window_close_needs_confirmation(self):
        g=self.game;g.handle_event(key(pygame.K_ESCAPE));g.handle_event(key(pygame.K_RETURN))
        self.assertTrue(g.running);self.assertFalse(g.pause.open)
        g.handle_event(pygame.event.Event(pygame.QUIT));self.assertTrue(g.pause.confirm);self.assertTrue(g.running)
        g.handle_event(key(pygame.K_RETURN));self.assertTrue(g.running);self.assertFalse(g.pause.confirm)
        g.pause.activate(g,2);g.handle_event(key(pygame.K_DOWN));g.handle_event(key(pygame.K_RETURN))
        self.assertFalse(g.running)

    def test_save_failure_keeps_game_open_until_explicit_discard(self):
        g=self.game;g.save_started=True;g.pause.show(True)
        with patch.object(g,'save_checkpoint',return_value=False):g.pause.activate(g,1)
        self.assertTrue(g.running);self.assertTrue(g.pause.save_failed)
        g.pause.activate(g,2);self.assertFalse(g.running);self.assertTrue(g.skip_exit_save)

    def test_confirmed_exit_saves_progress_and_start_screen_cancel_preserves_continue(self):
        with tempfile.TemporaryDirectory() as directory:
            g=Game(persistence=True,save_dir=directory);g.cash=432;g.pause.show(True);g.pause.activate(g,1)
            self.assertFalse(g.running);h=Game(persistence=True,save_dir=directory);self.assertTrue(h.save_store.load(h));self.assertEqual(h.cash,432)
            h=Game(start_screen=True,persistence=True,save_dir=directory)
            h.handle_event(key(pygame.K_ESCAPE));self.assertTrue(h.welcome.open);self.assertTrue(h.pause.confirm)
            h.handle_event(key(pygame.K_ESCAPE));h.handle_event(key(pygame.K_ESCAPE))
            self.assertTrue(h.welcome.open);self.assertFalse(h.pause.open);self.assertTrue(h.welcome.has_save)

    def test_janitor_uses_broom_for_dirt_and_grabber_for_litter(self):
        g=self.restore_north();g.cash=100000;g.janitors.purchase('north','hire',g);j=g.janitors.people['north']
        t=next(t for t in g.mall.trash if tuple(t.position) in j.paths.nodes);g.mall.respawn_trash(t);j.position=t.position.copy()
        for kind,tool in (('dirt','broom'),('trash','grabber')):
            t.kind=kind;g.janitors.update(.21,g)
            with patch.object(g.art,'draw',wraps=g.art.draw) as draw:j.draw(g)
            names=[c.args[1] for c in draw.call_args_list]
            self.assertTrue(any(n.startswith('janitor_') and '_clean_' in n for n in names))
            self.assertTrue(any(n.startswith(tool+'_') for n in names));self.assertFalse(t.cleaned)
        g.mall.clean_trash(t)
        with patch.object(g.art,'draw') as draw:j.draw(g)
        self.assertFalse(any(c.args[1].startswith(('broom_','grabber_')) for c in draw.call_args_list))

    def test_clean_mall_visitor_shops_twice_carries_purchase_and_leaves_at_entrance(self):
        g=self.restore_north();p=Shopper(1,g.mall.entrance,g.mall.stores[1],g.shoppers.walkways);g.shoppers.people=[p]
        visited=set()
        for _ in range(1800):
            p.update(.1,g.shoppers,g.mall,g.upgrades)
            if p.state=='inside':visited.add(p.store.name)
            if p.done:break
        self.assertEqual(len(visited),2);self.assertTrue(p.carrying);self.assertTrue(p.done)
        self.assertLess(p.position.distance_to(g.mall.entrance),1)

    def test_shoppers_sit_on_restored_benches_without_changing_safe_routes(self):
        g=self.restore_north();g.upgrades.decor.add('bench_0');store=g.mall.stores[1]
        p=Shopper(0,g.mall.entrance,store,g.shoppers.walkways);p.position=store.position.copy();p.state='exiting';p.path=[]
        g.shoppers.people=[p]
        for _ in range(300):
            p.update(.1,g.shoppers,g.mall,g.upgrades)
            if p.state=='resting':break
        self.assertEqual((p.state,p.activity),('resting','bench'));self.assertIsNotNone(p.seat)
        self.assertFalse(any(w.colliderect(pygame.Rect(p.position.x-10,p.position.y-12,20,24)) for w in g.mall.obstacles))
        with patch.object(g.art,'draw') as draw:p.draw(g.screen,g.camera,g.art,g.hud.small,False)
        self.assertIn('_sit',draw.call_args_list[0].args[1]);self.assertNotEqual(p.display_position,p.position)

    def test_life_tab_and_event_menu_work_with_keyboard_at_minimum_resolution(self):
        g=self.restore_north();g.screen=pygame.display.set_mode((800,600));g.journal.open=True
        g.handle_event(key(pygame.K_4));self.assertEqual(g.journal.tab,3);g.draw()
        g.handle_event(key(pygame.K_RETURN));self.assertFalse(g.journal.open);self.assertIsNotNone(g.life.spot)
        g.player.rect.center=g.life.spot.position;self.assertIs(g.target(),g.life.spot);g.interact();self.assertTrue(g.community_menu.open);g.draw()
        g.handle_event(key(pygame.K_1));self.assertEqual(g.life.round,1)
        g.handle_event(key(pygame.K_ESCAPE));self.assertFalse(g.community_menu.open);self.assertTrue(g.running)

    def test_visitors_replan_around_a_new_table_even_after_gather_refreshes_paths(self):
        g=self.restore_north();self.assertTrue(g.life.start(g,'north'));wall=g.mall.event_obstacle
        g.mall.obstacles.remove(wall);g.shoppers.walkways.refresh(g.mall)
        origin=pygame.Vector2(g.shoppers.walkways.nearest((wall.centerx,wall.bottom+80)))
        goal=pygame.Vector2(g.shoppers.walkways.nearest((wall.centerx,wall.top-64)))
        p=Shopper(0,g.mall.entrance,g.mall.stores[1],g.shoppers.walkways)
        p.position=origin;p.path=g.shoppers.walkways.route(origin,goal);p.goal=goal;p.state='strolling'
        self.assertTrue(p.path)
        self.assertTrue(any(wall.clipline(a,b) for a,b in zip([origin]+p.path,p.path)))
        g.shoppers.people=[p];g.shoppers.path_signature=g.shoppers.walkways.signature
        g.mall.obstacles.append(wall);g.shoppers.walkways.refresh(g.mall)
        g.shoppers.update(.1,g.mall,g.upgrades)
        self.assertTrue(p.path)
        for a,b in zip([p.position]+p.path,p.path):self.assertFalse(wall.inflate(20,24).clipline(a,b))

    def test_a_second_visitor_can_meet_a_friend_by_the_fountain(self):
        g=self.restore_north();g.upgrades.decor.add('fountain');store=g.mall.stores[1]
        friend=Shopper(0,g.mall.entrance,store,g.shoppers.walkways)
        friend.position=pygame.Vector2(g.mall.fountain.centerx,g.mall.fountain.bottom+45);friend.state='resting';friend.activity='fountain'
        p=Shopper(2,g.mall.entrance,store,g.shoppers.walkways);p.position=store.position.copy();p.state='exiting';p.path=[]
        g.shoppers.people=[friend,p];p.update(0,g.shoppers,g.mall,g.upgrades)
        self.assertEqual(p.activity,'meeting');self.assertEqual(p.friend_name,friend.name);self.assertIsNotNone(p.goal)
        self.assertTrue(p.path)

    def test_bench_is_reserved_while_a_visitor_is_still_walking_to_it(self):
        g=self.restore_north();g.upgrades.decor.add('bench_0');store=g.mall.stores[1]
        people=[Shopper(n,g.mall.entrance,store,g.shoppers.walkways) for n in (0,3)]
        g.shoppers.people=people
        for p in people:p.position=store.position.copy();p.state='exiting';p.path=[];p.update(0,g.shoppers,g.mall,g.upgrades)
        self.assertEqual(people[0].activity,'bench');self.assertNotEqual(people[1].activity,'bench')
