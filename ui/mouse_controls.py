"""Mouse access to nearby actions and every menu's return path."""

import pygame
from entities.trash import Trash
from mall.courtyard import SceneDoor
from systems.requests import RequestSpot
from systems.mall_life import EventTask
from ui import theme


class MouseControls:
    def __init__(self):
        self.work_target = None
        self.cursor = None

    def release(self):
        self.work_target = None

    def cancel(self):
        self.release()

    @staticmethod
    def modal(game):
        menus = (game.settings_menu, game.pause)
        if not game.welcome.open:
            menus += (
                game.cooking_menu,
                game.community_menu,
                game.story_menu,
                game.developer,
                game.display_menu,
                game.shop_menu,
                game.owner_menu,
                game.journal,
            )
        return next((menu for menu in menus if menu.open), None)

    def back_rect(self, game):
        menu = self.modal(game)
        if menu in (game.settings_menu, game.journal, game.cooking_menu):
            return menu.geometry(game.screen)[-1]
        if menu is not None:
            return theme.back_rect(menu.geometry(game.screen)[0])
        if game.tutorial.paused and not game.welcome.open:
            return theme.back_rect(game.tutorial.geometry(game.screen)[0])
        return None

    def handle(self, event, game):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        menu = self.modal(game)
        if menu is game.cooking_menu and menu.pause_rect(game.screen).collidepoint(
            event.pos
        ):
            self.cancel()
            game.pause.show()
            return True
        back = self.back_rect(game)
        if back and back.collidepoint(event.pos):
            self.cancel()
            if menu is game.cooking_menu:
                menu.close(game)
            elif menu is game.pause and menu.confirm:
                menu.activate(game, 0)
            elif menu is not None:
                menu.open = False
                if menu is game.settings_menu:
                    menu.capture = menu.drag = None
            else:
                game.pause.show()
            return True
        if game.welcome.open or game.tutorial.paused or menu is not None:
            return False
        if (
            game.developer.enabled
            and game.scene == "mall"
            and game.hud.developer_rect(game.screen).collidepoint(event.pos)
        ):
            self.cancel()
            game.developer.open = True
            return True
        for action, rect in game.hud.button_rects(game.screen).items():
            if not rect.collidepoint(event.pos):
                continue
            self.cancel()
            if action == "action":
                target = game.target()
                if target is not None:
                    self.activate(game, target)
            elif action == "journal":
                game.tutorial.journal_seen = True
                game.journal.open = True
            elif action == "help":
                if game.scene == "mall":
                    game.tutorial.start(game)
                else:
                    game.journal.tab = 0
                    game.journal.open = True
            elif action == "settings":
                game.settings_menu.open = True
            elif action == "pause":
                game.pause.show()
            return True
        return False

    def activate(self, game, target):
        game.interact(target)
        if isinstance(target, (RequestSpot, EventTask)) and target.duration:
            self.work_target = target

    def working(self, game):
        target = self.work_target
        if target is None or game.world_paused or game.scene != "mall":
            return False
        visible = game.owner_requests.visible_spots + game.life.visible_tasks
        return (
            target in visible
            and target.position.distance_to(game.player.rect.center) <= 72
        )

    @staticmethod
    def world_rect(game):
        top = 190 if game.tutorial.active else 170
        return pygame.Rect(
            0, top, game.screen.get_width(), game.screen.get_height() - top - 58
        )

    def world_target(self, game, point):
        outside = game.scene == "courtyard"
        world = game.courtyard.world if outside else game.mall
        door = world.return_door if outside else game.courtyard.door(game.mall)
        if (
            (outside or game.mall.commons.unlocked)
            and abs(point.x - door.position.x) <= 110
            and abs(point.y - door.position.y) <= 88
        ):
            return door
        stores = [store for store in world.stores if store.rect.collidepoint(point)]
        if stores:
            return min(
                stores, key=lambda store: store.position.distance_squared_to(point)
            )
        objects = list(world.trash_bins) + [
            trash for trash in world.trash if not trash.cleaned
        ]
        objects += list(world.stores)
        visitors = game.courtyard.shoppers if outside else game.shoppers
        objects += [person for person in visitors.people if person.visible]
        if not outside:
            objects += game.owner_requests.visible_spots + game.life.visible_tasks
            objects += game.story.visible_points(
                game.mall
            ) + game.story.visible_neighbors(game.mall)
            objects += [
                region
                for region in game.mall.regions
                if not region.unlocked and region.ready(game.mall)
            ]
            if game.life.spot:
                objects.append(game.life.spot)
        hits = [
            obj
            for obj in objects
            if obj.position.distance_to(point) <= (24 if isinstance(obj, Trash) else 36)
        ]
        return min(
            hits, key=lambda obj: obj.position.distance_squared_to(point), default=None
        )

    def world_click(self, event, game):
        if event.button != 1 or game.world_paused or not self.world_rect(game).collidepoint(event.pos):
            return
        self.cancel()
        point = pygame.Vector2(event.pos) + game.camera.offset
        target = self.world_target(game, point)
        if target is None:
            return
        reach = (
            game.upgrades.tool[1]
            if isinstance(target, Trash)
            else 110
            if isinstance(target, SceneDoor)
            else 72
        )
        if target.position.distance_to(game.player.rect.center) > reach:
            game.deny("Walk closer with the movement keys, then click again.")
            return
        self.activate(game, target)

    def hotspots(self, game):
        surface = game.screen
        menu = self.modal(game)
        back = self.back_rect(game)
        spots = [back] if back else []
        if menu is game.settings_menu:
            _, tabs, rows, _ = menu.geometry(surface)
            return (
                spots + tabs + rows[: 6 if menu.tab == 0 else len(menu.actions()) + 1]
            )
        if menu is game.pause:
            return spots + [
                row
                for row, label in zip(menu.geometry(surface)[1], menu.labels(game))
                if label
            ]
        if menu is game.cooking_menu:
            spots.append(menu.pause_rect(surface))
            if menu.started and not menu.round.done:
                return spots + menu.choice_rects(surface)
            return spots + [menu.geometry(surface)[2]]
        if menu is game.shop_menu:
            return (
                spots
                + menu.geometry(surface)[1]
                + [row for _, row in menu.rows(game)]
                + [menu.purchase_rect(game)]
                + menu.page_buttons(game)
            )
        if menu is game.owner_menu:
            return spots + [menu.geometry(surface)[1], menu.chat_button(surface)]
        if menu is game.display_menu:
            return (
                spots
                + menu.geometry(surface)[1]
                + ([menu.undo_rect(surface)] if menu.arrangement else [])
            )
        if menu is game.story_menu:
            return spots + [menu.geometry(surface)[1]]
        if menu is game.community_menu:
            choices = game.life.menu_content()[1]
            return spots + [
                row for row, choice in zip(menu.geometry(surface)[1], choices) if choice
            ]
        if menu is game.developer:
            return spots + menu.geometry(surface)[1]
        if menu is game.journal:
            spots += menu.tabs(surface)
            if menu.tab == 0:
                spots += menu.page_buttons(surface)
            elif menu.tab == 1:
                for court, row in zip(
                    menu.staff_courts(game), menu.staff_rows(surface)
                ):
                    actions = (
                        ("clean", "walk")
                        if court[0] in menu.staff_context(game)[0].people
                        else ("hire",)
                    )
                    spots += [menu.staff_buttons(row)[action] for action in actions]
            elif menu.tab == 2:
                spots += menu.page_buttons(surface) + [menu.memories_rect(surface)]
            else:
                spots += menu.life_rows(surface)
            return spots
        if game.welcome.open:
            welcome = game.welcome
            if welcome.leaving:
                return []
            if welcome.dialog:
                return list(welcome.dialog_geometry(surface)[2:])
            _, start, quit_button = welcome.geometry(surface)
            _, rows, page, count = welcome.save_geometry(surface)
            return (
                [
                    start,
                    quit_button,
                    welcome.new_rect(surface),
                    welcome.settings_rect(surface),
                    welcome.tutorial_rect(surface),
                ]
                + rows[: len(welcome.saves[page * count : (page + 1) * count])]
                + (
                    list(welcome.page_rects(surface)) + [welcome.delete_rect(surface)]
                    if welcome.saves
                    else []
                )
            )
        if game.tutorial.paused:
            return spots + list(game.tutorial.geometry(surface)[1:])
        spots += list(game.hud.button_rects(surface).values())
        if game.developer.enabled and game.scene == "mall":
            spots.append(game.hud.developer_rect(surface))
        if game.tutorial.active:
            spots.append(game.tutorial.skip_rect(surface))
        return spots

    def draw(self, game):
        surface = game.screen
        menu = self.modal(game)
        back = self.back_rect(game)
        if menu is game.cooking_menu:
            theme.button(surface, menu.pause_rect(surface), "Menu", game.hud.small)
        if back and menu not in (game.settings_menu, game.journal, game.cooking_menu):
            label = "Menu" if menu is None else "Back"
            theme.button(surface, back, label, game.hud.small)
        point = pygame.mouse.get_pos()
        hovered = next(
            (rect for rect in self.hotspots(game) if rect.collidepoint(point)), None
        )
        if hovered:
            pygame.draw.rect(surface, theme.ACCENT, hovered, 2, border_radius=8)
        clickable = hovered is not None
        if not game.world_paused and self.world_rect(game).collidepoint(point):
            clickable |= (
                self.world_target(game, pygame.Vector2(point) + game.camera.offset)
                is not None
            )
        cursor = pygame.SYSTEM_CURSOR_HAND if clickable else pygame.SYSTEM_CURSOR_ARROW
        if cursor != self.cursor:
            try:
                pygame.mouse.set_cursor(cursor)
            except pygame.error:
                pass  # Dummy SDL and some remote drivers do not have system cursors.
            self.cursor = cursor
