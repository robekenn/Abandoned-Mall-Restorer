"""Warm main menu, named save cards and deliberate save-management dialogs."""

import pygame
from systems.economy import money
from systems.save_slots import save_name
from ui import theme
from ui.menu_scene import draw_concourse

CREAM = (248, 238, 211)
INK = (45, 68, 57)
GREEN = (55, 88, 68)
GOLD = (171, 115, 54)
LATEST = object()


def fit_text(font, text, width):
    if font.size(text)[0] <= width:
        return text
    while text and font.size(text + "…")[0] > width:
        text = text[:-1]
    return text + "…"


class Welcome:
    FADE_SECONDS = 0.9

    def __init__(self, open=True):
        self.open = open
        self.tutorial_enabled = True
        self.has_save = False
        self.continuing = False
        self.status = ""
        self.elapsed = 0.0
        self.leaving = False
        self.fade = 0.0
        self.saves = []
        self.selection = 0
        self.dialog = None
        self.pending_id = None
        self.name = ""
        self.replace_name = False
        self.confirm_selection = 0
        self.heading = pygame.font.Font(None, 62)
        self.font = pygame.font.Font(None, 25)
        self.small = pygame.font.Font(None, 21)
        self.card_title = pygame.font.Font(None, 28)

    @property
    def editing(self):
        return self.dialog == "new"

    @property
    def selected(self):
        return self.saves[self.selection] if self.saves else None

    def refresh(self, game, selected=LATEST):
        self.saves = game.save_slots.entries()
        if game.save_slots.status:
            self.status = game.save_slots.status
        self.has_save = any(slot.playable for slot in self.saves)
        self.selection = next(
            (i for i, slot in enumerate(self.saves) if slot.identifier == selected), 0
        )

    def geometry(self, surface):
        panel = pygame.Rect(
            0,
            0,
            min(surface.get_width() - 64, 1040),
            min(surface.get_height() - 152, 570),
        )
        panel.center = (surface.get_width() // 2, surface.get_height() // 2 + 50)
        sidebar = min(300, round(panel.width * 0.34))
        start = pygame.Rect(panel.x + 22, panel.y + 105, sidebar - 22, 44)
        quit = start.move(0, 174)
        return panel, start, quit

    def new_rect(self, surface):
        return self.geometry(surface)[1].move(0, 58)

    def settings_rect(self, surface):
        return self.geometry(surface)[1].move(0, 116)

    def tutorial_rect(self, surface):
        panel, start, _ = self.geometry(surface)
        return pygame.Rect(start.x, panel.bottom - 53, start.width, 30)

    def save_geometry(self, surface):
        panel, start, _ = self.geometry(surface)
        area = pygame.Rect(
            start.right + 28,
            panel.y + 18,
            panel.right - start.right - 50,
            panel.height - 36,
        )
        count = max(2, (panel.height - 150) // 70)
        page = self.selection // count
        rows = [
            pygame.Rect(area.x, area.y + 40 + i * 70, area.width, 62)
            for i in range(count)
        ]
        return area, rows, page, count

    def delete_rect(self, surface):
        area, _, _, _ = self.save_geometry(surface)
        return pygame.Rect(area.right - 100, area.bottom - 32, 100, 32)

    def page_rects(self, surface):
        area, _, _, _ = self.save_geometry(surface)
        return (
            pygame.Rect(area.x, area.bottom - 32, 32, 32),
            pygame.Rect(area.x + 42, area.bottom - 32, 32, 32),
        )

    def dialog_geometry(self, surface):
        panel = pygame.Rect(0, 0, min(490, surface.get_width() - 64), 250)
        panel.center = surface.get_rect().center
        field = pygame.Rect(panel.x + 28, panel.y + 92, panel.width - 56, 46)
        cancel = pygame.Rect(
            panel.x + 28, panel.bottom - 64, (panel.width - 68) // 2, 40
        )
        accept = cancel.move(cancel.width + 12, 0)
        return panel, field, cancel, accept

    def choose_new(self, game):
        self.dialog = "new"
        self.name = f"Northgate {len(self.saves) + 1}"
        self.replace_name = True
        self.status = ""
        pygame.key.start_text_input()
        pygame.key.set_text_input_rect(self.dialog_geometry(game.screen)[1])

    def choose_delete(self):
        if self.selected:
            self.dialog = "delete"
            self.pending_id = self.selected.identifier
            self.confirm_selection = 0
            self.status = ""

    def close_dialog(self):
        if self.editing:
            pygame.key.stop_text_input()
        self.dialog = None

    def start(self):
        if not self.leaving:
            self.close_dialog()
            self.leaving = True
            self.fade = 0.0

    def update(self, dt):
        self.elapsed += dt
        if self.leaving:
            self.fade = min(1, self.fade + dt / self.FADE_SECONDS)
            if self.fade >= 1:
                self.open = False

    def primary(self, game):
        if self.selected:
            if self.selected.playable:
                game.continue_game(self.selected.identifier)
            else:
                self.status = "This save could not be read. Choose another mall or create a new one."
        else:
            game.start_new_game()

    def dialog_action(self, game, accept):
        if not accept:
            self.close_dialog()
        elif self.editing:
            game.start_new_game(save_name(self.name))
        elif game.delete_save(self.pending_id):
            self.close_dialog()
        else:
            self.status = (
                self.status or game.save_slots.status or "Could not delete this save."
            )

    def handle_dialog(self, event, game):
        if event.type == pygame.TEXTINPUT and self.editing:
            if self.replace_name:
                self.name = ""
                self.replace_name = False
            self.name = (self.name + "".join(c for c in event.text if c.isprintable()))[
                :28
            ]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close_dialog()
            elif event.key == pygame.K_BACKSPACE and self.editing:
                self.name = "" if self.replace_name else self.name[:-1]
                self.replace_name = False
            elif (
                event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB)
                and not self.editing
            ):
                self.confirm_selection = 1 - self.confirm_selection
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and (
                not self.editing or event.key == pygame.K_RETURN
            ):
                self.dialog_action(game, self.editing or self.confirm_selection == 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, _, cancel, accept = self.dialog_geometry(game.screen)
            if cancel.collidepoint(event.pos):
                self.dialog_action(game, False)
            elif accept.collidepoint(event.pos):
                self.dialog_action(game, True)

    def handle(self, event, game):
        if self.leaving:
            return
        if self.dialog:
            self.handle_dialog(event, game)
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.primary(game)
            elif event.key == pygame.K_n:
                self.choose_new(game)
            elif event.key == pygame.K_d:
                self.choose_delete()
            elif event.key == pygame.K_ESCAPE:
                game.pause.show(True)
            elif self.saves and event.key in (
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_PAGEUP,
                pygame.K_PAGEDOWN,
            ):
                direction = -1 if event.key in (pygame.K_UP, pygame.K_PAGEUP) else 1
                amount = (
                    self.save_geometry(game.screen)[3]
                    if event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN)
                    else 1
                )
                self.selection = (self.selection + direction * amount) % len(self.saves)
        elif event.type == pygame.MOUSEWHEEL and self.saves:
            self.selection = (self.selection - event.y) % len(self.saves)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _, start, quit = self.geometry(game.screen)
            if self.tutorial_rect(game.screen).collidepoint(event.pos):
                self.tutorial_enabled = not self.tutorial_enabled
            elif self.new_rect(game.screen).collidepoint(event.pos):
                self.choose_new(game)
            elif start.collidepoint(event.pos):
                self.primary(game)
            elif quit.collidepoint(event.pos):
                game.pause.show(True)
            elif self.settings_rect(game.screen).collidepoint(event.pos):
                game.settings_menu.open = True
            elif self.delete_rect(game.screen).collidepoint(event.pos):
                self.choose_delete()
            else:
                _, rows, page, count = self.save_geometry(game.screen)
                for i, row in enumerate(rows):
                    if row.collidepoint(event.pos) and page * count + i < len(
                        self.saves
                    ):
                        self.selection = page * count + i
                for i, rect in enumerate(self.page_rects(game.screen)):
                    if rect.collidepoint(event.pos) and self.saves:
                        self.selection = max(
                            0,
                            min(
                                len(self.saves) - 1,
                                self.selection + (-count if i == 0 else count),
                            ),
                        )

    def button(
        self, surface, rect, label, *, primary=False, danger=False, selected=False
    ):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        color = (202, 220, 179) if primary else CREAM
        if hover:
            color = (225, 230, 196) if primary else (255, 247, 226)
        theme.frame(surface, rect, color, False)
        pygame.draw.rect(
            surface,
            GOLD if hover or selected else (182, 168, 127),
            rect,
            2 if hover or selected else 1,
            border_radius=9,
        )
        text = self.font.render(label, True, (142, 64, 45) if danger else INK)
        surface.blit(text, text.get_rect(center=rect.center))

    def draw_dialog(self, surface):
        theme.dim(surface)
        panel, field, cancel, accept = self.dialog_geometry(surface)
        theme.frame(surface, panel, CREAM, False)
        title = "A new beginning" if self.editing else "Delete this mall?"
        surface.blit(
            self.card_title.render(title, True, INK), (panel.x + 28, panel.y + 25)
        )
        if self.editing:
            surface.blit(
                self.small.render(
                    "Give your save a name. Your other malls stay safe.", True, INK
                ),
                (panel.x + 28, panel.y + 61),
            )
            theme.frame(surface, field, (255, 251, 235), False)
            pygame.draw.rect(surface, GREEN, field, 2, border_radius=9)
            visible = self.name
            while visible and self.font.size(visible + "|")[0] > field.width - 24:
                visible = visible[1:]
            text = self.font.render(
                visible + ("|" if int(self.elapsed * 2) % 2 == 0 else ""), True, INK
            )
            surface.blit(text, (field.x + 12, field.y + 12))
        else:
            label = self.selected.name if self.selected else "this save"
            for i, line in enumerate(
                theme.wrap(
                    self.font,
                    f"“{label}” and its recovery backup will be removed. This cannot be undone.",
                    panel.width - 56,
                )
            ):
                surface.blit(
                    self.font.render(line, True, INK),
                    (panel.x + 28, panel.y + 67 + i * 25),
                )
        self.button(
            surface,
            cancel,
            "Cancel",
            selected=not self.editing and self.confirm_selection == 0,
        )
        self.button(
            surface,
            accept,
            "Start restoring" if self.editing else "Delete save",
            primary=self.editing,
            danger=not self.editing,
            selected=not self.editing and self.confirm_selection == 1,
        )
        if self.status:
            for i, line in enumerate(
                theme.wrap(self.small, self.status, panel.width - 56)[:2]
            ):
                surface.blit(
                    self.small.render(line, True, (142, 64, 45)),
                    (panel.x + 28, panel.y + 145 + i * 18),
                )

    def draw(self, game):
        surface = pygame.Surface(game.screen.get_size(), pygame.SRCALPHA)
        draw_concourse(surface, game.art, self.elapsed)
        panel, start, quit = self.geometry(surface)
        title = self.heading.render("Northgate Mall", True, INK)
        surface.blit(title, (panel.x + 4, 23))
        surface.blit(
            self.font.render(
                "Abandoned Mall Restorer  ·  A place worth coming back to.", True, INK
            ),
            (panel.x + 6, 80),
        )
        pygame.draw.rect(surface, (115, 110, 80), panel.move(4, 6), border_radius=16)
        theme.frame(surface, panel, CREAM, False)
        sidebar = pygame.Rect(
            panel.x + 12, panel.y + 12, start.right - panel.x + 8, panel.height - 24
        )
        theme.frame(surface, sidebar, GREEN, False)
        surface.blit(
            self.small.render("WELCOME HOME", True, (232, 205, 143)),
            (start.x, panel.y + 30),
        )
        surface.blit(
            self.card_title.render("One shop at a time.", True, CREAM),
            (start.x, panel.y + 59),
        )
        self.button(
            surface,
            start,
            "Continue selected" if self.selected else "Start restoring",
            primary=True,
        )
        self.button(surface, self.new_rect(surface), "+  New game")
        self.button(surface, self.settings_rect(surface), "Settings")
        self.button(surface, quit, "Quit")
        for i, line in enumerate(
            ("Restore the shops.", "Bring your neighborhood home.")
        ):
            surface.blit(
                self.small.render(line, True, (222, 224, 191)),
                (start.x, quit.bottom + 22 + i * 21),
            )
        guide = "First steps guide: " + ("On" if self.tutorial_enabled else "Off")
        rect = self.tutorial_rect(surface)
        surface.blit(self.small.render(guide, True, CREAM), (rect.x, rect.y + 6))
        area, rows, page, count = self.save_geometry(surface)
        caption = "YOUR MALLS" + ("  ·  DEVELOPER" if game.developer.enabled else "")
        surface.blit(self.small.render(caption, True, GOLD), area.topleft)
        for i, slot in enumerate(self.saves[page * count : (page + 1) * count]):
            row = rows[i]
            selected = page * count + i == self.selection
            color = (218, 229, 194) if selected else (237, 224, 191)
            if row.collidepoint(pygame.mouse.get_pos()):
                color = (230, 235, 206)
            theme.frame(surface, row, color, False)
            pygame.draw.rect(
                surface,
                GREEN if selected else (204, 189, 148),
                row,
                2 if selected else 1,
                border_radius=9,
            )
            label = self.card_title.render(
                fit_text(self.card_title, slot.name, row.width - 28), True, INK
            )
            surface.blit(label, (row.x + 14, row.y + 8))
            details = (
                f"{money(slot.cash)}  ·  {slot.businesses} shops  ·  {slot.courts} area{'s' if slot.courts != 1 else ''}  ·  {int(slot.seconds // 60)} min"
                if slot.playable
                else "Save unavailable · choose another or delete"
            )
            if slot.recovered:
                details = "Recovery backup available · " + money(slot.cash)
            surface.blit(
                self.small.render(
                    fit_text(self.small, details, row.width - 28), True, INK
                ),
                (row.x + 14, row.y + 36),
            )
        if not self.saves:
            game.art.draw(
                surface, "plant_clean", (area.centerx, area.y + 110), (64, 96)
            )
            for i, text in enumerate(
                (
                    "A fresh start awaits.",
                    "Create a mall and make it your own.",
                    "Each save keeps its own progress.",
                )
            ):
                image = self.font.render(text, True, INK)
                surface.blit(
                    image, image.get_rect(midtop=(area.centerx, area.y + 170 + i * 30))
                )
        else:
            for label, rect in zip(("<", ">"), self.page_rects(surface)):
                self.button(surface, rect, label)
            pages = (len(self.saves) + count - 1) // count
            surface.blit(
                self.small.render(f"{page + 1} / {pages}", True, INK),
                (area.x + 88, area.bottom - 23),
            )
            self.button(surface, self.delete_rect(surface), "Delete", danger=True)
        caption = "Up / Down: saves  ·  Enter: play  ·  N: new  ·  D: delete"
        surface.blit(self.small.render(caption, True, INK), (area.x, area.bottom - 61))
        if self.status and not self.dialog:
            for i, line in enumerate(
                theme.wrap(self.small, self.status, area.width)[:2]
            ):
                surface.blit(
                    self.small.render(line, True, (142, 64, 45)),
                    (area.x, area.bottom - 98 + i * 18),
                )
        if self.dialog:
            self.draw_dialog(surface)
        if self.leaving:
            alpha = 1 - self.fade
            surface.set_alpha(round(255 * alpha * alpha * (3 - 2 * alpha)))
        game.screen.blit(surface, (0, 0))
