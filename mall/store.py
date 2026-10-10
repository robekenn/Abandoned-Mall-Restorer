import pygame


class Store:
    def __init__(self, rect, name, available=False, cost=100, rent=5, kind='cafe', facing='down'):
        self.rect = pygame.Rect(rect)
        self.facing = facing
        self.name = name
        self.available = available
        self.restored = False
        self.cost = cost
        self.base_rent = rent
        self.request_bonus = 0
        self.request_level = 0
        self.recurring_completed = 0
        self.section_key = 'north'
        self.request_wait = 180.0
        self.door_open = False
        self.kind = kind
        self.upgrade_shop = None
        self.position = pygame.Vector2(self.rect.centerx, self.rect.bottom + 35 if facing=='down' else self.rect.top-35)

    @property
    def rent(self):
        return self.base_rent+self.request_bonus

    @staticmethod
    def draw_request_marker(surface,point):
        pygame.draw.line(surface,(173,217,210),(point.x,point.y-35),(point.x,point.y-27),3)
        pygame.draw.circle(surface,(173,217,210),(point.x,point.y-22),2)

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
        if self.restored and self.door_open:
            name += '_open'
        if self.facing=='up':name+='_up'
        art.draw(surface, name, r.center, (r.width+12,r.height+20))
        sign = font.render(self.name.upper(), True, (250,234,193) if self.restored else (188,184,166))
        background = sign.get_rect(center=(r.centerx, r.y+40 if self.facing=='down' else r.bottom-40)).inflate(16,10)
        pygame.draw.rect(surface, (35,49,47), background, border_radius=4)
        surface.blit(sign, sign.get_rect(center=background.center))
        if self.facing=='up':
            if self.request_level>=1:
                for x in (r.centerx-r.width//4,r.centerx+r.width//4):
                    pygame.draw.rect(surface,(223,180,94),(x-12,r.y+29,24,5))
            if self.request_level>=2:
                for x in (r.centerx-r.width//4,r.centerx+r.width//4):
                    pygame.draw.rect(surface,(84,139,131),(x-8,r.y+18,5,10))
                    pygame.draw.rect(surface,(172,120,79),(x+2,r.y+20,5,8))
            if self.request_level>=3:
                for x in range(r.left+12,r.right-12,24):
                    pygame.draw.polygon(surface,(223,180,94),[(x,r.y+6),(x+14,r.y+6),(x+7,r.y+15)])
            for i in range(self.request_level):
                pygame.draw.rect(surface,(223,180,94),(r.centerx+(i-1)*18-5,r.bottom-15,10,5))
        else:
            # Permanent earned improvements: window display, flower boxes, then welcome pennants.
            if self.request_level >= 1:
                for offset in (-r.width//4,r.width//4):
                    pygame.draw.rect(surface,(223,180,94),(r.centerx+offset-12,r.bottom-70,24,6))
            if self.request_level >= 2:
                for offset in (-r.width//4,r.width//4):
                    x,y = r.centerx+offset,r.bottom-70
                    for dx,color in ((-8,(84,139,131)),(0,(223,180,94)),(8,(172,120,79))):
                        pygame.draw.rect(surface,color,(x+dx-3,y-18,6,18))
                    pygame.draw.rect(surface,(228,216,164),(x-15,y-23,30,3))
            if self.request_level >= 3:
                for x in range(r.left+12,r.right-12,24):
                    pygame.draw.polygon(surface,(223,180,94),[(x,r.y+90),(x+14,r.y+90),(x+7,r.y+102)])
            if self.request_level:
                for i in range(self.request_level):
                    x = r.centerx+(i-(self.request_level-1)/2)*18
                    pygame.draw.rect(surface,(223,180,94),(x-5,r.y+65,10,10))
                    pygame.draw.rect(surface,(228,216,164),(x-2,r.y+68,4,4))
        if self.upgrade_shop:
            badge=font.render('UPGRADES',True,(130,196,180))
            badge_rect=badge.get_rect(midtop=(background.centerx,background.bottom+5)).inflate(10,4)
            pygame.draw.rect(surface,(35,49,47),badge_rect,border_radius=4)
            surface.blit(badge,badge.get_rect(center=badge_rect.center))
        if self.available:
            point = camera.point(self.position)
            pygame.draw.circle(surface, (105,181,147) if self.restored else (216,177,104), point, 12)
            if self.restored and not self.upgrade_shop and self.request_wait <= 0:
                self.draw_request_marker(surface,point)
            if selected:
                pygame.draw.circle(surface, (245,218,156), point, 21, 2)
