"""A relaxed owner conversation; Enter/click accepts or claims, Esc/E returns to play."""
import pygame
from systems.economy import money
from systems.requests import OWNERS, PROJECTS
from ui import theme
from game.lore import OWNER_LORE


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
            game.save_checkpoint()
            game.say_owner(store,'Thank you for making time for us. The journal will show where to go.')
            game.audio.play('pickup')
        elif requests.store and requests.store is not store:
            game.say_owner(store,'Finish helping your neighbor first. There is no rush; we will be here.')
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
        theme.dim(surface)
        panel,button = self.geometry(surface)
        theme.frame(surface,panel)
        store = self.store
        requests = game.owner_requests
        surface.blit(game.hud.title.render(OWNERS[store.name],True,theme.TEXT),(panel.x+20,panel.y+18))
        subtitle=store.name+(f' · {store.recurring_completed} favors completed' if store.request_level==3 else '')
        surface.blit(game.hud.small.render(subtitle,True,theme.MUTED),(panel.x+20,panel.y+55))
        for i in range(3):
            pygame.draw.circle(surface,theme.GOLD if i<store.request_level else theme.BORDER,(panel.right-28-i*20,panel.y+38),5)
        reward = ''
        if requests.store is not store and store.request_wait>0:
            title = 'A little time to settle in'
            description = 'We are enjoying the shop as it is. Come back later and we will have a new idea to work on together.'
            if store.request_level==3:
                title='A neighborhood to care for'
                description=OWNER_LORE+' We will have another small favor soon.'
            status,action = f'Next request in {theme.clock(store.request_wait)} of play','Back to the mall'
        elif requests.store and requests.store is not store:
            title = 'One small thing at a time'
            description = f'You are helping {OWNERS[requests.store.name]} right now. Finish that request, then come see us.'
            status,action = '','Back to your request'
        else:
            title,description,improvement,bonus,cash = requests.details(store)
            reward = f'{money(cash)} thank-you'+(f'   ·   +{money(bonus)} base rent' if bonus else '')
            if store.request_level<3:reward=improvement+'   ·   '+reward
            status = requests.objective if requests.store is store else 'Take your time. There is no deadline.'
            action = ('Claim reward' if requests.ready else 'Keep helping') if requests.store is store else 'Accept request'
        surface.blit(game.hud.font.render(title,True,theme.ACCENT),(panel.x+20,panel.y+101))
        for i,line in enumerate(theme.wrap(game.hud.font,description,panel.width-40)):
            surface.blit(game.hud.font.render(line,True,theme.TEXT),(panel.x+20,panel.y+140+i*25))
        if reward:
            theme.frame(surface,pygame.Rect(panel.x+20,panel.y+227,panel.width-40,38),theme.CARD,False)
            surface.blit(game.hud.small.render(reward,True,theme.GOLD),(panel.x+30,panel.y+239))
        for i,line in enumerate(theme.wrap(game.hud.font,status,panel.width-40)):
            surface.blit(game.hud.font.render(line,True,theme.MUTED),(panel.x+20,panel.y+284+i*25))
        theme.frame(surface,button,theme.CARD)
        label = game.hud.font.render(action,True,theme.ACCENT)
        surface.blit(label,label.get_rect(center=button.center))
        surface.blit(game.hud.small.render('Enter / click: continue     Esc / E: close',True,theme.MUTED),(panel.x+20,panel.bottom-26))
