"""Mouse and keyboard upgrade-shop menu, sized for the minimum window."""
import pygame
from systems.economy import money


class UpgradeShop:
    categories = ('Gear','Furniture','Garden')

    def __init__(self):
        self.open = False
        self.category = 0
        self.selection = 0
        self.notice = 'Choose an upgrade. Each fixture is purchased separately.'

    def geometry(self, screen):
        w,h = screen.get_size()
        panel = pygame.Rect(0,0,min(w-48,760),min(h-48,580))
        panel.center = (w//2,h//2)
        tabs = [pygame.Rect(panel.x+16+i*(panel.width-32)//3,panel.y+74,(panel.width-32)//3-6,34) for i in range(3)]
        return panel,tabs

    def rows(self, game):
        panel,_ = self.geometry(game.screen)
        offers = game.upgrades.offers(self.categories[self.category])
        return [(o,pygame.Rect(panel.x+16,panel.y+116+i*44,panel.width-32,40)) for i,o in enumerate(offers)]

    def buy(self, game, key):
        self.notice = game.buy_upgrade(key)

    def handle(self, event, game):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_e):
                self.open = False
            elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                self.category = event.key-pygame.K_1
                self.selection = 0
            elif event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_TAB):
                self.category = (self.category+(-1 if event.key == pygame.K_LEFT else 1))%3
                self.selection = 0
            elif event.key in (pygame.K_UP,pygame.K_DOWN):
                count = len(self.rows(game))
                self.selection = (self.selection+(-1 if event.key == pygame.K_UP else 1))%count
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):
                self.buy(game,self.rows(game)[self.selection][0].key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _,tabs = self.geometry(game.screen)
            for i,rect in enumerate(tabs):
                if rect.collidepoint(event.pos):
                    self.category,self.selection = i,0
                    return
            for i,(offer,rect) in enumerate(self.rows(game)):
                if rect.collidepoint(event.pos):
                    self.selection = i
                    self.buy(game,offer.key)
                    return

    def draw(self, game):
        surface = game.screen
        shade = pygame.Surface(surface.get_size(),pygame.SRCALPHA)
        shade.fill((10,20,22,205));surface.blit(shade,(0,0))
        panel,tabs = self.geometry(surface)
        pygame.draw.rect(surface,(30,45,47),panel)
        pygame.draw.rect(surface,(146,164,126),panel,2)
        surface.blit(game.hud.title.render('NORTHGATE SUPPLIES',True,(235,222,170)),(panel.x+16,panel.y+14))
        surface.blit(game.hud.small.render(f'{money(game.cash)} available / bag {game.upgrades.held}/{game.upgrades.capacity} / ${game.upgrades.unit_value} per item',True,(177,206,174)),(panel.x+16,panel.y+48))
        for i,rect in enumerate(tabs):
            pygame.draw.rect(surface,(77,100,78) if i == self.category else (44,62,62),rect)
            surface.blit(game.hud.font.render(f'{i+1} {self.categories[i]}',True,(229,222,184)),(rect.x+10,rect.y+7))
        for i,(offer,rect) in enumerate(self.rows(game)):
            pygame.draw.rect(surface,(53,74,68) if i == self.selection else (37,55,54),rect)
            surface.blit(game.hud.font.render(offer.title,True,(222,224,190)),(rect.x+9,rect.y+3))
            surface.blit(game.hud.small.render(offer.detail,True,(167,187,170)),(rect.x+9,rect.y+23))
            text = 'Installed' if offer.owned else f'Buy ${offer.price}'
            color = (159,175,147) if offer.owned else ((224,192,124) if game.cash >= offer.price else (145,149,140))
            label = game.hud.font.render(text,True,color)
            surface.blit(label,label.get_rect(midright=(rect.right-10,rect.y+13)))
        lines = game.hud.wrap(self.notice,panel.width-32)
        for i,line in enumerate(lines[:2]):
            surface.blit(game.hud.small.render(line,True,(223,202,151)),(panel.x+16,panel.bottom-65+i*18))
        surface.blit(game.hud.small.render('Click to buy / 1-3: tabs / arrows: select / Enter: buy / Esc or E: close',True,(169,185,169)),(panel.x+16,panel.bottom-23))
