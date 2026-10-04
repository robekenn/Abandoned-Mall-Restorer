import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import tempfile
import unittest
from unittest.mock import patch
from collections import defaultdict
from pathlib import Path
import pygame
from game.game import Game
from game.preferences import Preferences
from systems.shoppers import Shopper
from ui.speech import Speech


class PlaytesterTests(unittest.TestCase):
    def setUp(self):self.g=Game()
    def tearDown(self):pygame.quit()
    def key(self,key):self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))
    def click(self,pos):self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))

    def test_mouse_collects_clicked_litter_with_range_capacity_and_modal_guards(self):
        g=self.g;trash=g.mall.trash[0];g.player.rect.center=trash.position;g.frame_camera(g.screen.get_size())
        pos=tuple(g.camera.point(trash.position));g.upgrades.held=g.upgrades.capacity
        self.click(pos);self.assertFalse(trash.cleaned)
        g.upgrades.held=0;g.pause.show();self.click(pos);self.assertFalse(trash.cleaned)
        g.pause.open=False;g.tutorial.start(g);self.click(pos);self.assertFalse(trash.cleaned);g.tutorial.skip()
        g.player.rect.x+=200;self.click(pos);self.assertFalse(trash.cleaned)
        g.player.rect.center=trash.position;self.click(pos);self.assertTrue(trash.cleaned)
        self.assertEqual(g.total_collected,1)

    def test_mouse_chooses_clicked_piece_and_ignores_hud_clicks(self):
        g=self.g;first,second=g.mall.trash[:2]
        first.position=pygame.Vector2(400,350);second.position=pygame.Vector2(430,350)
        g.player.rect.center=first.position;g.camera.offset=pygame.Vector2(0,0)
        self.click((430,350));self.assertTrue(second.cleaned);self.assertFalse(first.cleaned)
        g.upgrades.held=0;first.position=pygame.Vector2(400,50);g.player.rect.center=first.position
        self.click((400,50));self.assertFalse(first.cleaned)

    def test_upgrade_clicks_inspect_until_explicit_purchase(self):
        g=self.g;g.mall.stores[0].restored=True;g.open_upgrade_shop(g.mall.stores[0]);g.cash=500
        self.click(g.shop_menu.rows(g)[1][1].center)
        self.assertEqual(g.shop_menu.selection,1);self.assertEqual(g.cash,500)
        self.assertEqual(g.upgrades.value_level,0)
        self.click(g.shop_menu.purchase_rect(g).center)
        self.assertEqual(g.upgrades.value_level,1);self.assertLess(g.cash,500)

    def test_shopper_does_not_intercept_litter_or_owner_request_objects(self):
        g=self.g;trash=g.mall.trash[0];g.player.rect.center=trash.position
        g.shoppers.walkways.refresh(g.mall)
        person=Shopper(1,trash.position,g.mall.stores[1],g.shoppers.walkways)
        person.position=trash.position.copy();g.shoppers.people=[person]
        self.assertIs(g.target(),trash);g.interact();self.assertTrue(trash.cleaned)
        store=g.mall.stores[1];store.restored=True;store.request_wait=0;g.owner_requests.accept(store,g.mall)
        spot=g.owner_requests.spots[0];g.player.rect.center=spot.position;person.position=spot.position.copy()
        self.assertIs(g.target(),spot);g.interact();self.assertTrue(g.owner_requests.parcel)

    def test_remapped_interaction_and_movement_and_hints_are_consistent(self):
        g=self.g;g.preferences.bind('interact',pygame.K_q)
        g.player.rect.center=g.mall.trash[0].position
        self.key(pygame.K_e);self.assertEqual(g.total_collected,0)
        self.key(pygame.K_q);self.assertEqual(g.total_collected,1)
        g.preferences.bind('up',pygame.K_z)
        keys=defaultdict(bool);keys[pygame.K_z]=True;self.assertEqual(g.preferences.direction(keys),(0,-1))
        self.assertEqual(g.preferences.hint('Hold E · J map'),'Hold Q · J map')
        previous=g.preferences.keys.copy();g.preferences.bind('journal',pygame.K_q)
        self.assertEqual(g.preferences.keys,previous)
        g.preferences.bind('journal',pygame.K_RETURN);self.assertEqual(g.preferences.keys,previous)

    def test_preferences_persist_separately_and_invalid_settings_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Preferences(directory,True);p.bind('interact',pygame.K_q);p.music=.2;p.effects=.6;p.guide=False;p.notifications=False;p.save()
            loaded=Preferences(directory,True)
            self.assertEqual((loaded.music,loaded.effects,loaded.guide,loaded.notifications),(.2,.6,False,False))
            self.assertEqual(loaded.keys['interact'],pygame.K_q)
            self.assertFalse((Path(directory)/'progress.json').exists())
            p.path.write_text('{broken');self.assertEqual(Preferences(directory,True).music,1)

    def test_settings_pause_world_and_close_window_confirmation_still_works(self):
        g=self.g;self.key(pygame.K_F2);self.assertTrue(g.settings_menu.open)
        before=(g.player.rect.center,g.rent_timer,g.litter_spawner.elapsed,g.mall.stores[1].request_wait)
        g.update(200,(1,0),True);g.interact()
        self.assertEqual(before,(g.player.rect.center,g.rent_timer,g.litter_spawner.elapsed,g.mall.stores[1].request_wait))
        g.handle_event(pygame.event.Event(pygame.QUIT))
        self.assertFalse(g.settings_menu.open);self.assertTrue(g.pause.confirm);self.assertTrue(g.running)

    def test_music_and_effects_controls_apply_independently(self):
        g=self.g;self.key(pygame.K_F2)
        rows=g.settings_menu.geometry(g.screen)[2]
        rect=rows[0];self.click((rect.x+240,rect.centery))
        self.assertEqual(g.preferences.music,0);self.assertEqual(g.preferences.effects,1)
        self.assertEqual(g.audio.music_channel.get_volume(),0)
        self.assertGreater(g.audio.sounds['pickup'].get_volume(),.9)

    def test_settings_on_title_pause_and_controls_pages_fit_800_by_600(self):
        g=self.g;g.screen=pygame.display.set_mode((800,600));g.welcome.open=True
        self.key(pygame.K_F2)
        with patch.object(g.settings_menu,'draw',wraps=g.settings_menu.draw) as draw:g.draw();draw.assert_called_once()
        for page in (0,1):g.settings_menu.tab=1;g.settings_menu.page=page;g.draw()
        g.settings_menu.open=False;g.welcome.open=False;g.pause.show();g.pause.activate(g,3)
        with patch.object(g.pause,'draw') as pause_draw:g.draw();pause_draw.assert_not_called()

    def test_request_heading_and_upgrade_units_are_clear(self):
        g=self.g;store=g.mall.stores[1];store.restored=True;store.request_wait=0;g.owner_requests.accept(store,g.mall)
        self.assertIn(store.name,g.hud.goal(g)[0])
        offers=g.upgrades.offers('Gear','north');details=' '.join(o.detail for o in offers)
        self.assertIn('tiles reach',details);self.assertNotIn('px reach',details)

    def test_speech_follows_world_anchor_and_culls_offscreen_speaker(self):
        g=self.g;p=pygame.Vector2(600,500);g.camera.offset=pygame.Vector2(0,0)
        first=Speech.geometry(g,'Hello neighbor',p)[0]
        g.camera.offset=pygame.Vector2(40,30)
        second=Speech.geometry(g,'Hello neighbor',p)[0]
        self.assertEqual(first.x-second.x,40);self.assertEqual(first.y-second.y,30)
        with patch('ui.speech.theme.frame') as draw:g.speech.draw_bubble(g,'Neighbor','Hello',(-100,500));draw.assert_not_called()

    def test_north_facing_owner_bubble_avoids_work_desk(self):
        g=self.g;store=next(s for s in g.mall.stores if s.facing=='up')
        store.restored=True;store.request_level=2;store.request_wait=0;g.owner_requests.accept(store,g.mall)
        g.say_owner(store,'Thank you for helping us.');g.player.rect.center=store.position;g.frame_camera(g.screen.get_size())
        rect=Speech.geometry(g,g.speech.text,g.speech.position)[0];p=g.camera.point(g.owner_requests.spots[0].position)
        self.assertFalse(rect.colliderect(pygame.Rect(p.x-24,p.y-48,96,80)))

    def test_janitor_retargets_new_nearer_litter_while_walking(self):
        g=self.g;g.cash=999999;g.janitors.purchase('north','hire',g);j=g.janitors.people['north']
        for t in g.mall.north_trash:g.mall.clean_trash(t)
        candidates=sorted((t for t in g.mall.north_trash if j.route_to(t.position,g.mall) is not None),key=lambda t:j.position.distance_squared_to(t.position))
        near,far=candidates[0],candidates[-1]
        g.mall.respawn_trash(far);j.choose_work(g.mall.north_trash,g.mall);self.assertIs(j.target,far)
        g.mall.respawn_trash(near);j.update(0,g.mall.north_trash,g)
        self.assertIs(j.target,near)
        j.path=[];j.progress=1;g.mall.respawn_trash(far);j.update(0,g.mall.north_trash,g);self.assertIs(j.target,near)
