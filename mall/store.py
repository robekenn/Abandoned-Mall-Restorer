import pygame


class Store:
    def __init__(self, rect, name, available=False, cost=100, rent=5, kind='cafe'):
        self.rect = pygame.Rect(rect)
        self.name = name
        self.available = available
        self.restored = False
        self.cost = cost
        self.base_rent = rent
        self.request_bonus = 0
        self.request_level = 0
        self.kind = kind
        self.upgrade_shop = None
        self.position = pygame.Vector2(self.rect.centerx, self.rect.bottom + 35)

    @property
    def rent(self):
        return self.base_rent+self.request_bonus

    @property
    def label(self):
        if self.restored:
            if self.rent == 0:
                return f'Enter {self.name} / buy upgrades'
            return f'Meet the owner at {self.name} / requests and improvements'
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
        # Permanent earned improvements: window display, flower boxes, then welcome pennants.
        if self.request_level >= 1:
            for offset in (-r.width//4,r.width//4):
                pygame.draw.rect(surface,(223,180,94),(r.centerx+offset-12,r.bottom-70,24,6))
        if self.request_level >= 2:
            for offset in (-r.width//4,r.width//4):
                x,y = r.centerx+offset,r.bottom-35
                pygame.draw.rect(surface,(133,94,61),(x-20,y,40,8))
                for dx in (-12,0,12):
                    pygame.draw.rect(surface,(112,150,87),(x+dx-4,y-10,8,10))
                    pygame.draw.rect(surface,(223,180,94),(x+dx-3,y-12,6,5))
        if self.request_level >= 3:
            for x in range(r.left+12,r.right-12,24):
                pygame.draw.polygon(surface,(223,180,94),[(x,r.y+90),(x+14,r.y+90),(x+7,r.y+102)])
        if self.request_level:
            for i in range(self.request_level):
                x = r.centerx+(i-(self.request_level-1)/2)*18
                pygame.draw.rect(surface,(223,180,94),(x-5,r.y+65,10,10))
                pygame.draw.rect(surface,(228,216,164),(x-2,r.y+68,4,4))
        if self.available:
            point = camera.point(self.position)
            pygame.draw.circle(surface, (105,181,147) if self.restored else (216,177,104), point, 12)
            if self.restored and not self.upgrade_shop and self.request_level < 3:
                pygame.draw.line(surface,(173,217,210),(point.x,point.y-35),(point.x,point.y-27),3)
                pygame.draw.circle(surface,(173,217,210),(point.x,point.y-22),2)
            if selected:
                pygame.draw.circle(surface, (245,218,156), point, 21, 2)
