"""A relaxed owner conversation; Enter/click accepts or claims, Esc/E returns to play."""
import pygame
from systems.economy import money
from systems.requests import OWNERS, PROJECTS


class OwnerMenu:
    def __init__(self):
        self.open = False
        self.store = None

    def geometry(self, surface):
        w,h = surface.get_size()
        panel = pygame.Rect(0,0,min(w-48,760),min(h-72,460))
        panel.center = (w//2,h//2)
        button = pygame.Rect(panel.x+20,panel.bottom-80,panel.width-40,40)
        return panel,button

    def visit(self, store):
        self.store = store
        self.open = True

    def action(self, game):
        requests,store = game.owner_requests,self.store
        if requests.store is store and requests.ready:
            game.claim_request(store)
        elif not requests.store and requests.eligible(store):
            requests.accept(store,game.mall)
            game.notify(f'{OWNERS[store.name]}: Thank you! {requests.objective}')
            game.audio.play('pickup')
        elif requests.store and requests.store is not store:
            game.notify('Finish your current owner request first. There is no deadline.')
        self.open = False

    def handle(self, event, game):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_e):
                self.open = False
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):
                self.action(game)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.geometry(game.screen)[1].collidepoint(event.pos):
                self.action(game)

    def draw(self, game):
        surface = game.screen
        shade = pygame.Surface(surface.get_size(),pygame.SRCALPHA)
        shade.fill((10,20,22,210)); surface.blit(shade,(0,0))
        panel,button = self.geometry(surface)
        pygame.draw.rect(surface,(30,45,47),panel)
        pygame.draw.rect(surface,(146,164,126),panel,2)
        owner,store = OWNERS[self.store.name],self.store
        surface.blit(game.hud.title.render(f'{owner.upper()} / {store.name}',True,(235,222,170)),(panel.x+20,panel.y+18))
        summary = f'Shop improvements {store.request_level}/3 / +{money(store.request_bonus)} base rent / no deadlines'
        surface.blit(game.hud.small.render(summary,True,(177,206,174)),(panel.x+20,panel.y+58))
        if store.request_level == len(PROJECTS):
            title = 'A familiar place'
            description = 'You helped turn this shop into a neighborhood favorite. Thank you for bringing people back.'
            reward = f'Permanent base rent: {money(store.rent)} every five seconds.'
            status,action = 'All three improvements earned. Your work stays with this shop.','Back to the mall'
        else:
            title,description,improvement,bonus,cash = game.owner_requests.details(store)
            reward = f'Earn {improvement} / +{money(bonus)} base rent / {money(cash)} thank-you'
            if game.owner_requests.store is store:
                status = game.owner_requests.objective
                action = 'Complete request and improve shop' if game.owner_requests.ready else 'Keep helping'
            elif game.owner_requests.store:
                status = f'You are helping {OWNERS[game.owner_requests.store.name]} first. Come back any time.'
                action = 'Back to current request'
            else:
                status,action = 'One request at a time. Take your time; nothing expires.','Accept request'
        surface.blit(game.hud.font.render(title,True,(234,205,147)),(panel.x+20,panel.y+100))
        for i,line in enumerate(game.hud.wrap(description,panel.width-40)):
            surface.blit(game.hud.font.render(line,True,(206,220,196)),(panel.x+20,panel.y+137+i*25))
        surface.blit(game.hud.small.render(reward,True,(174,212,175)),(panel.x+20,panel.y+236))
        for i,line in enumerate(game.hud.wrap(status,panel.width-40)):
            surface.blit(game.hud.font.render(line,True,(189,208,193)),(panel.x+20,panel.y+270+i*25))
        pygame.draw.rect(surface,(76,100,78),button)
        label = game.hud.font.render(action,True,(235,225,182))
        surface.blit(label,label.get_rect(center=button.center))
        surface.blit(game.hud.small.render('Enter / click: choose   Esc / E: close   M: mute music and effects',True,(169,185,169)),(panel.x+20,panel.bottom-26))
