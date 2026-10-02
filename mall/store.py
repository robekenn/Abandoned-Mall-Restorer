import pygame


class Store:
    def __init__(self, rect, name, available=False):
        self.rect = pygame.Rect(rect)
        self.name = name
        self.available = available
        self.restored = False
        self.cost = 100
        self.position = pygame.Vector2(self.rect.centerx, self.rect.bottom + 35)

    @property
    def label(self):
        return "Shop open - earning $5 every 5 seconds" if self.restored else "Reopen Pages Bookshop ($100)"

    def draw(self, surface, camera, font, art, selected=False):
        r = camera.rect(self.rect)
        name = ('bookshop' if self.available else 'cafe') + ('_clean' if self.restored else '_dirty')
        art.draw(surface, name, r.center, (r.width+12,r.height+20))
        sign = font.render(self.name.upper(), True, (250,234,193) if self.restored else (188,184,166))
        background = sign.get_rect(center=(r.centerx, r.y+22)).inflate(16,10)
        pygame.draw.rect(surface, (35,49,47), background, border_radius=4)
        surface.blit(sign, sign.get_rect(center=background.center))
        if self.available:
            point = camera.point(self.position)
            pygame.draw.circle(surface, (105,181,147) if self.restored else (216,177,104), point, 12)
            if selected:
                pygame.draw.circle(surface, (245,218,156), point, 21, 2)
