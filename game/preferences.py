"""Local user preferences, separate from playthrough checkpoints."""

import json
import math
import re
from pathlib import Path
import pygame
from game.storage import atomic_write

DEFAULT_KEYS = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "interact": pygame.K_e,
    "journal": pygame.K_j,
    "guide": pygame.K_h,
    "skip": pygame.K_t,
    "mute": pygame.K_m,
    "fullscreen": pygame.K_F11,
    "save": pygame.K_F5,
    "pause": pygame.K_ESCAPE,
}
RESERVED = {
    pygame.K_RETURN,
    pygame.K_SPACE,
    pygame.K_TAB,
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_LEFT,
    pygame.K_RIGHT,
    pygame.K_F2,
    pygame.K_F3,
    pygame.K_r,
    pygame.K_c,
    pygame.K_n,
    pygame.K_BACKSPACE,
    pygame.K_DELETE,
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LALT,
    pygame.K_RALT,
    *range(pygame.K_0, pygame.K_9 + 1),
}


class Preferences:
    def __init__(self, directory, enabled=False, fullscreen=False):
        self.path = Path(directory) / "settings.json"
        self.enabled = enabled
        self.music = self.effects = 1.0
        self.fullscreen = fullscreen
        self.guide = True
        self.notifications = True
        self.keys = DEFAULT_KEYS.copy()
        self.status = ""
        if enabled:
            self.load()

    def load(self):
        try:
            d = json.loads(self.path.read_text(encoding="utf-8"))
            keys = d["keys"]
            if (
                not isinstance(keys, dict)
                or set(keys) != set(DEFAULT_KEYS)
                or len(set(keys.values())) != len(keys)
            ):
                raise ValueError()
            for action, key in keys.items():
                if (
                    type(key) is not int
                    or not pygame.key.name(key)
                    or key in RESERVED
                    or key == pygame.K_ESCAPE
                    and action != "pause"
                ):
                    raise ValueError()
            for name in ("music", "effects"):
                if (
                    type(d[name]) not in (int, float)
                    or not math.isfinite(d[name])
                    or not 0 <= d[name] <= 1
                ):
                    raise ValueError()
            for name in ("fullscreen", "guide", "notifications"):
                if type(d[name]) is not bool:
                    raise ValueError()
            for name in (
                "music",
                "effects",
                "fullscreen",
                "guide",
                "notifications",
                "keys",
            ):
                setattr(self, name, d[name])
        except (OSError, ValueError, KeyError, TypeError):
            pass

    def save(self):
        if not self.enabled:
            return True
        try:
            atomic_write(
                self.path,
                json.dumps(
                    {
                        n: getattr(self, n)
                        for n in (
                            "music",
                            "effects",
                            "fullscreen",
                            "guide",
                            "notifications",
                            "keys",
                        )
                    }
                ).encode("utf-8"),
            )
            self.status = "Settings saved"
            return True
        except OSError:
            self.status = "Could not save settings"
            return False

    def bind(self, action, key):
        if (
            key in RESERVED
            or key == pygame.K_ESCAPE
            and action != "pause"
            or not pygame.key.name(key)
        ):
            return "That key is reserved for menus."
        other = next(
            (a for a, k in self.keys.items() if k == key and a != action), None
        )
        if other:
            return "That key is already used by " + other + ". Choose another."
        self.keys[action] = key
        self.save()
        return self.status or "Key updated"

    def normalize(self, event):
        if event.type != pygame.KEYDOWN:
            return event
        action = next((a for a, k in self.keys.items() if k == event.key), None)
        key = (
            DEFAULT_KEYS[action]
            if action
            else 0
            if event.key in DEFAULT_KEYS.values()
            else event.key
        )
        # Esc always remains a way out of menus and confirmations.
        if event.key == pygame.K_ESCAPE:
            key = pygame.K_ESCAPE
        values = event.dict.copy()
        values["key"] = key
        return pygame.event.Event(event.type, values)

    def label(self, action):
        return pygame.key.name(self.keys[action]).upper()

    def hint(self, text):
        mapping = {
            pygame.key.name(k).upper(): self.label(a) for a, k in DEFAULT_KEYS.items()
        }
        mapping["Esc"] = self.label("pause")
        mapping["WASD"] = " / ".join(
            self.label(a) for a in ("up", "left", "down", "right")
        )
        return re.sub(
            r"\b(?:WASD|F11|F5|Esc|E|J|H|T|M)\b", lambda m: mapping[m[0]], text
        )

    def direction(self, keys):
        return (
            int(keys[self.keys["right"]] or keys[pygame.K_RIGHT])
            - int(keys[self.keys["left"]] or keys[pygame.K_LEFT]),
            int(keys[self.keys["down"]] or keys[pygame.K_DOWN])
            - int(keys[self.keys["up"]] or keys[pygame.K_UP]),
        )


class HintFont:
    def __init__(self, font, preferences):
        self.font = font
        self.preferences = preferences

    def render(self, text, *args, **kwargs):
        return self.font.render(self.preferences.hint(text), *args, **kwargs)

    def size(self, text):
        return self.font.size(self.preferences.hint(text))

    def __getattr__(self, name):
        return getattr(self.font, name)
