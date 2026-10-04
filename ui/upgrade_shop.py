"""Mouse and keyboard upgrade-shop menu, sized for the minimum window."""
import pygame
from systems.economy import money
from ui import theme


class UpgradeShop:
    categories = ('Gear','Furniture','Garden')

    def __init__(self):
        self.open = False
        self.shop = 'north'
        self.category = 0
        self.selection = self.scroll = 0
        self.notice = ''

    def geometry(self, screen):
        w,h = screen.get_size()
        panel = pygame.Rect(0,0,min(w-48,760),min(h-48,580))
        panel.center = (w//2,h//2)
        tabs = [pygame.Rect(panel.x+16+i*(panel.width-32)//3,panel.y+86,(panel.width-32)//3-6,34) for i in range(3)]
        return panel,tabs

    def offers(self,game):
        return game.upgrades.offers(self.categories[self.category],self.shop)

    def capacity(self,game):
        panel,_=self.geometry(game.screen)
        return max(1,(panel.height-242)//40)

    def keep_visible(self,game):
        count=len(self.offers(game));self.selection=min(self.selection,count-1)
        self.scroll=max(0,min(self.scroll,count-self.capacity(game)))
        if self.selection<self.scroll:self.scroll=self.selection
        if self.selection>=self.scroll+self.capacity(game):self.scroll=self.selection-self.capacity(game)+1

    def rows(self, game):
        panel,_ = self.geometry(game.screen);self.keep_visible(game)
        offers=self.offers(game)[self.scroll:self.scroll+self.capacity(game)]
        return [(o,pygame.Rect(panel.x+16,panel.y+132+i*40,panel.width-32,36)) for i,o in enumerate(offers)]

    def purchase_rect(self, game):
        panel,_=self.geometry(game.screen)
        return pygame.Rect(panel.right-150,panel.bottom-60,130,30)

    def buy(self, game, key):
        self.notice = game.buy_upgrade(key)

    def handle(self, event, game):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_e):
                self.open = False
            elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                self.category = event.key-pygame.K_1
                self.selection = self.scroll = 0
            elif event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_TAB):
                self.category = (self.category+(-1 if event.key == pygame.K_LEFT else 1))%3
                self.selection = self.scroll = 0
            elif event.key in (pygame.K_UP,pygame.K_DOWN):
                count = len(self.offers(game))
                self.selection = (self.selection+(-1 if event.key == pygame.K_UP else 1))%count
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):
                self.buy(game,self.offers(game)[self.selection].key)
        elif event.type == pygame.MOUSEWHEEL:
            count=len(self.offers(game))
            self.selection=max(0,min(count-1,self.selection-event.y))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _,tabs = self.geometry(game.screen)
            for i,rect in enumerate(tabs):
                if rect.collidepoint(event.pos):
                    self.category,self.selection,self.scroll = i,0,0
                    return
            if self.purchase_rect(game).collidepoint(event.pos):
                self.buy(game,self.offers(game)[self.selection].key);return
            for i,(offer,rect) in enumerate(self.rows(game)):
                if rect.collidepoint(event.pos):
                    self.selection = self.scroll+i
                    return

    def draw(self, game):
        surface = game.screen
        theme.dim(surface)
        panel,tabs = self.geometry(surface)
        theme.frame(surface,panel)
        title={'north':'Northgate Supplies','east':'Eastgate Workshop','garden':'Garden Supply','commons':'Commons Exchange','courtyard':'Courtyard Provisions'}[self.shop]
        surface.blit(game.hud.title.render(title,True,theme.TEXT),(panel.x+20,panel.y+18))
        surface.blit(game.hud.small.render(f'{money(game.cash)} available',True,theme.GOLD),(panel.x+20,panel.y+56))
        for i,rect in enumerate(tabs):
            theme.frame(surface,rect,theme.CARD if i==self.category else theme.PANEL)
            surface.blit(game.hud.font.render(f'{i+1}  '+('Service' if self.shop=='courtyard' and i==0 else self.categories[i]),True,theme.ACCENT if i==self.category else theme.MUTED),(rect.x+10,rect.y+8))
        rows = self.rows(game)
        count=len(self.offers(game))
        if count>len(rows):
            page=game.hud.small.render(f'{self.scroll+1}–{self.scroll+len(rows)} of {count}',True,theme.MUTED)
            surface.blit(page,page.get_rect(topright=(panel.right-20,panel.y+56)))
        for local,(offer,rect) in enumerate(rows):
            i=self.scroll+local
            theme.frame(surface,rect,theme.CARD if i==self.selection else theme.PANEL, i==self.selection)
            label = 'Installed' if offer.owned else money(offer.price)
            price = game.hud.font.render(label,True,theme.MUTED if offer.owned else theme.GOLD)
            surface.blit(price,price.get_rect(midright=(rect.right-12,rect.centery)))
            # Place descriptions below the list, keeping every row easy to scan.
            name = offer.title.split(' / ')[0]
            surface.blit(game.hud.font.render(name,True,theme.TEXT),(rect.x+12,rect.y+9))
        selected = self.offers(game)[self.selection]
        detail = selected.detail
        if ' / ' in selected.title:
            detail = selected.title.split(' / ',1)[1]+' · '+detail
        for i,line in enumerate(theme.wrap(game.hud.small,detail,panel.width-40)[:2]):
            surface.blit(game.hud.small.render(line,True,theme.ACCENT),(panel.x+20,panel.bottom-91+i*18))
        for i,line in enumerate(theme.wrap(game.hud.small,self.notice,panel.width-190)[:2]):
            surface.blit(game.hud.small.render(line,True,theme.GOLD),(panel.x+20,panel.bottom-55+i*18))
        button=self.purchase_rect(game);theme.frame(surface,button,theme.CARD)
        label=game.hud.small.render('Purchase · Enter',True,theme.GOLD)
        surface.blit(label,label.get_rect(center=button.center))
        surface.blit(game.hud.small.render('Click: inspect · Enter: buy · Arrows / wheel: browse · 1–3: tabs · Esc: close',True,theme.MUTED),(panel.x+20,panel.bottom-23))
