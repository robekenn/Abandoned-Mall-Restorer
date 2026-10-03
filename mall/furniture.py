"""Ground footprints matched to the integer-scaled pixel art, not layout rectangles."""
import pygame


def bench_footprint(layout):
    # 24px sprite at 3x: the seat and feet occupy 60x24 at its base.
    return pygame.Rect(layout.centerx-30,layout.centery+6,60,24)


def fountain_footprint(layout):
    # 24px sprite at 6x: a 132px rim, with the tall jet above its ground base.
    return pygame.Rect(layout.centerx-66,layout.centery,132,60)
