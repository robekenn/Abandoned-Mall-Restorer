"""A restored concourse for the main menu; animation never ticks gameplay."""

import math
import pygame


def draw_concourse(surface, art, elapsed):
    width, height = surface.get_size()
    surface.fill((224, 213, 181))
    roof = round(height * 0.30)
    for y in range(roof):
        fraction = y / max(1, roof)
        color = (
            round(227 + 17 * fraction),
            round(226 + 8 * fraction),
            round(205 + 4 * fraction),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
    for x in range(-120, width + 240, 240):
        pygame.draw.polygon(
            surface,
            (198, 215, 197),
            ((x, 0), (x + 205, 0), (x + 255, roof), (x + 55, roof)),
        )
        pygame.draw.line(surface, (147, 137, 102), (x + 205, 0), (x + 255, roof), 7)
    pygame.draw.line(surface, (157, 132, 87), (0, roof), (width, roof), 12)
    for i, x in enumerate(range(-80, width + 180, 200)):
        art.draw(
            surface,
            "cafe_clean" if i % 2 else "bookshop_clean",
            (x + 90, roof + 80),
            (200, 168),
        )
        art.draw(surface, "festival_lantern_0", (x + 95, roof + 4), (28, 40))
    floor = roof + 140
    for y in range(floor, height, 48):
        for x in range(-48, width, 64):
            color = (212, 202, 165) if (x // 64 + y // 48) % 2 else (223, 212, 178)
            pygame.draw.rect(surface, color, (x, y, 64, 48))
            pygame.draw.rect(surface, (198, 188, 151), (x, y, 64, 48), 1)
    sun = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(
        sun,
        (255, 238, 173, 42),
        ((width * 0.63, 0), (width * 0.82, 0), (width, height), (width * 0.40, height)),
    )
    surface.blit(sun, (0, 0))
    art.draw(surface, "mosaic", (width * 0.55, height * 0.84), (260, 156))
    art.draw(surface, "fountain_clean", (width * 0.55, height * 0.76), (240, 132))
    for x in (width * 0.12, width * 0.88):
        art.draw(surface, "bench_clean", (x, height * 0.82), (144, 64))
        art.draw(surface, "plant_clean", (x - 72, height * 0.72), (64, 96))
    for i in range(3):
        progress = ((elapsed * (19 + i * 4) + i * 290) % (width + 160)) - 80
        direction = "right" if i % 2 == 0 else "left"
        x = progress if direction == "right" else width - progress
        art.draw(
            surface,
            f"shopper_{i}_{direction}_{int(elapsed * 5) % 4}",
            (x, floor + 52 + i * 64),
            (32, 48),
        )
    for i in range(9):
        x = (i * 193 + elapsed * 7) % width
        y = height * 0.28 + math.sin(elapsed * 0.4 + i) * 18 + i * 29
        pygame.draw.circle(surface, (244, 226, 167), (round(x), round(y)), 2)
