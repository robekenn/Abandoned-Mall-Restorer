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

    def draw(self, surface, camera, font, selected=False):
        r = camera.rect(self.rect)
        pygame.draw.rect(surface, (60, 92, 85) if self.restored else (66, 69, 69), r)
        pygame.draw.rect(surface, (154, 185, 164) if self.restored else (118, 116, 105), r, 8)
        sign = pygame.Rect(r.x + 15, r.y + 14, r.width-30, 42)
        pygame.draw.rect(surface, (36, 66, 62) if self.restored else (47, 49, 49), sign)
        text = font.render(self.name.upper(), True, (240, 224, 183))
        surface.blit(text, text.get_rect(center=sign.center))
        for x in range(r.x+25, r.right-25, 65):
            window = pygame.Rect(x, r.y+76, 48, r.height-105)
            pygame.draw.rect(surface, (161, 203, 183) if self.restored else (36, 45, 48), window)
            if self.restored:
                for y in range(window.y+15, window.bottom, 30):
                    pygame.draw.rect(surface, (113, 78, 57), (x+5, y, 38, 7))
            else:
                pygame.draw.line(surface, (140, 109, 77), window.topleft, window.bottomright, 12)
                pygame.draw.line(surface, (140, 109, 77), window.topright, window.bottomleft, 12)
        if self.available:
            p = camera.point(self.position)
            pygame.draw.circle(surface, (105, 181, 147) if self.restored else (216, 177, 104), p, 14)
            if selected:
                pygame.draw.circle(surface, (245, 218, 156), p, 22, 2)
