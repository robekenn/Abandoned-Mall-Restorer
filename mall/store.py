import pygame


class Store:
    def __init__(self, rect, name, available=False, cost=100, rent=5, kind='cafe'):
        self.rect = pygame.Rect(rect)
        self.name = name
        self.available = available
        self.restored = False
        self.cost = cost
        self.rent = rent
        self.kind = kind
        self.upgrade_shop = None
        self.position = pygame.Vector2(self.rect.centerx, self.rect.bottom + 35)

    @property
    def label(self):
        if self.restored:
            if self.rent == 0:
                return f'Enter {self.name} / buy upgrades'
            return f'{self.name}: +${self.rent} base rent / 5s'
        if not self.available:
            return f'{self.name}: finish the first cleanup and reopen the previous shop'
        return f'Reopen {self.name} (${self.cost})'

    def draw(self, surface, camera, font, art, selected=False):
        r = camera.rect(self.rect)
        name = self.kind + ('_clean' if self.restored else '_dirty')
        art.draw(surface, name, r.center, (r.width+12,r.height+20))
        sign = font.render(self.name.upper(), True, (250,234,193) if self.restored else (188,184,166))
        background = sign.get_rect(center=(r.centerx, r.y+40)).inflate(16,10)
        pygame.draw.rect(surface, (35,49,47), background, border_radius=4)
        surface.blit(sign, sign.get_rect(center=background.center))
        if self.available:
            point = camera.point(self.position)
            pygame.draw.circle(surface, (105,181,147) if self.restored else (216,177,104), point, 12)
            if selected:
                pygame.draw.circle(surface, (245,218,156), point, 21, 2)
