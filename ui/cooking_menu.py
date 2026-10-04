"""Visible recipe tickets and kitchen controls, usable by mouse or keyboard."""
import math
import pygame
from systems.cooking import CookingRound, RECIPES, ARROWS
from systems.economy import money
from ui import theme


class CookingMenu:
    def __init__(self):
        self.open=False;self.store=None;self.round=None;self.started=False;self.tip=0

    def visit(self,store,game):
        world=game.courtyard.world
        if game.scene!='courtyard' or not game.courtyard.unlocked or world is None or store not in world.stores or not store.restored or store.name not in RECIPES:return False
        if game.courtyard.kitchen_requests.pending!=store.name:
            game.notify('The kitchen is settled. Watch for its next cooking request.');return False
        served=game.courtyard.cooking.get(store.name,{}).get('served',0)
        self.store=store;self.round=CookingRound(store.name,served=served);self.started=False;self.tip=0;self.open=True
        return True

    def geometry(self,surface):
        w,h=surface.get_size();panel=pygame.Rect(0,0,min(w-48,820),min(h-48,600));panel.center=(w//2,h//2)
        body=pygame.Rect(panel.x+24,panel.y+136,panel.width-48,196)
        button=pygame.Rect(panel.x+24,panel.bottom-86,panel.width-48,42)
        close=pygame.Rect(panel.right-92,panel.y+18,68,30)
        return panel,body,button,close

    def choices(self):
        r=self.round.recipe
        if r.mode=='ingredients':return r.choices
        if r.mode=='stir':return ARROWS[:2]
        if r.mode=='fold':return ARROWS
        return ('Pour / stop' if r.mode=='pour' else 'Flip skewer' if self.round.step==0 else 'Plate skewer',)

    def choice_rects(self,surface):
        panel,_,_,_=self.geometry(surface);count=len(self.choices());cols=min(3,count)
        width=(panel.width-48-12*(cols-1))//cols
        return [pygame.Rect(panel.x+24+(i%cols)*(width+12),panel.y+350+(i//cols)*48,width,40) for i in range(count)]

    def act(self,index,game):
        if not self.started or self.round.done:return
        self.round.action(index)
        if self.round.done and not self.round.rewarded:self.tip=self.round.finish(game,self.store)

    def primary(self,game):
        if self.round.done:self.open=False;return
        if self.started:return
        deposit=round(self.store.base_rent*.1)
        if game.cash<deposit:
            self.round.notice='You need '+money(deposit)+' for the ingredient deposit.';return
        if not game.courtyard.kitchen_requests.accept(self.store.name):self.open=False;return
        self.round.deposit=deposit;game.cash-=deposit;self.started=True
        game.save_checkpoint()

    def close(self,game):
        if self.started and not self.round.done:
            self.round.failed=True;self.round.notice='Order abandoned. The ingredient deposit is lost.'
            self.round.finish(game,self.store)
        self.open=False

    def update(self,dt,game):
        if self.started:
            self.round.update(dt)
            if self.round.done and not self.round.rewarded:self.tip=self.round.finish(game,self.store)

    def handle(self,event,game):
        if event.type==pygame.KEYDOWN:
            if getattr(event,'repeat',False):return
            if event.key==pygame.K_ESCAPE:self.close(game);return
            if not self.started or self.round.done:
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):self.primary(game)
                return
            mode=self.round.recipe.mode
            if mode in ('pour','grill') and event.key in (pygame.K_SPACE,pygame.K_RETURN):self.act(0,game)
            elif mode in ('stir','fold') and event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN):
                index=(pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN).index(event.key)
                if index<len(self.choices()):self.act(index,game)
            elif mode=='ingredients' and pygame.K_1<=event.key<=pygame.K_5:
                self.act(event.key-pygame.K_1,game)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            _,_,button,close=self.geometry(game.screen)
            if close.collidepoint(event.pos):self.close(game)
            elif not self.started or self.round.done:
                if button.collidepoint(event.pos):self.primary(game)
            else:
                for i,rect in enumerate(self.choice_rects(game.screen)):
                    if rect.collidepoint(event.pos):self.act(i,game);break

    @staticmethod
    def text(surface,font,text,pos,color=theme.TEXT):surface.blit(font.render(text,True,color),pos)

    def draw_food(self,game,rect):
        surface=game.screen;r=self.round.recipe;round_=self.round
        center=(rect.centerx,rect.centery+14)
        pygame.draw.ellipse(surface,(19,31,31),(center[0]-112,center[1]+55,224,26))
        pygame.draw.ellipse(surface,(216,211,184),(center[0]-118,center[1]-68,236,144))
        pygame.draw.ellipse(surface,(166,172,151),(center[0]-102,center[1]-56,204,120),3)
        if round_.complete:
            game.art.draw(surface,r.sprite,center,(144,144))
        elif r.mode=='pour':
            glass=pygame.Rect(center[0]-43,center[1]-68,86,130)
            fill=self.round.marker if self.started and not round_.complete else (self.round.target if round_.complete else 0)
            pygame.draw.rect(surface,(77,108,110),glass,border_radius=8)
            liquid=pygame.Rect(glass.x+5,glass.bottom-5-round(120*fill),76,round(120*fill))
            if liquid.height:pygame.draw.rect(surface,r.color,liquid,border_radius=4)
            pygame.draw.rect(surface,(215,222,207),glass,3,border_radius=8)
            pygame.draw.line(surface,theme.GOLD,(glass.left-8,glass.bottom-round(120*round_.target)),(glass.right+8,glass.bottom-round(120*round_.target)),3)
        elif self.store.name=='Hearth Pizza':
            pygame.draw.ellipse(surface,(210,164,96),(center[0]-92,center[1]-48,184,100))
            pygame.draw.ellipse(surface,(189,92,66),(center[0]-81,center[1]-39,162,82))
            pygame.draw.ellipse(surface,(233,201,129),(center[0]-73,center[1]-32,146,68))
            colors=((197,72,55),(92,152,98),(164,147,113),(65,76,66),(220,153,82))
            for i,index in enumerate(round_.order[:round_.step]):
                for j in range(5):
                    angle=j*math.tau/5+i*.7
                    pygame.draw.circle(surface,colors[index],(round(center[0]+math.cos(angle)*(26+i*13)),round(center[1]+math.sin(angle)*(13+i*7))),6)
        elif r.mode=='fold':
            points=[(center[0]-85,center[1]+40),(center[0]+85,center[1]+40),(center[0],center[1]-60)]
            pygame.draw.polygon(surface,r.color,points)
            for i in range(round_.step):
                y=center[1]+28-i*20
                pygame.draw.line(surface,(135,98,65),(center[0]-65+i*14,y),(center[0]+65-i*14,y),5)
        elif r.mode=='stir':
            game.art.draw(surface,r.sprite,center,(144,144))
            angle=round_.step*math.pi/3
            tip=(round(center[0]+math.cos(angle)*44),round(center[1]+math.sin(angle)*25))
            pygame.draw.line(surface,(211,173,108),(center[0]+90,center[1]-65),tip,8)
            pygame.draw.circle(surface,(233,203,149),tip,10)
        elif r.mode=='grill':
            pygame.draw.rect(surface,(52,63,62),(center[0]-100,center[1]-55,200,110),border_radius=10)
            for x in range(center[0]-85,center[0]+90,20):pygame.draw.line(surface,(121,135,125),(x,center[1]-48),(x,center[1]+48),2)
            game.art.draw(surface,r.sprite,center,(136,136))
            if round_.step:pygame.draw.line(surface,(94,61,45),(center[0]-40,center[1]),(center[0]+40,center[1]+15),4)
        else:
            colors=((234,215,164),(188,105,127),(120,82,60),(130,181,151),(229,157,101)) if self.store.name=='Moonrise Desserts' else ((96,156,99),(163,129,91),(199,91,66),(146,183,112),(222,189,94))
            pygame.draw.ellipse(surface,(112,140,131),(center[0]-72,center[1],144,65))
            for i,index in enumerate(round_.order[:round_.step]):
                if self.store.name=='Moonrise Desserts':pygame.draw.circle(surface,colors[index],(center[0],center[1]+12-i*34),28)
                else:pygame.draw.ellipse(surface,colors[index],(center[0]-63+i*4,center[1]-i*13,126-i*8,40))
        self.text(surface,game.hud.small,f'{min(round_.step,r.steps)} / {r.steps} steps',(rect.x+12,rect.bottom-18),theme.MUTED)

    def draw(self,game):
        surface=game.screen;theme.dim(surface);panel,body,button,close=self.geometry(surface);theme.frame(surface,panel)
        r=self.round.recipe;round_=self.round
        self.text(surface,game.hud.title,self.store.name,(panel.x+24,panel.y+22),r.color)
        self.text(surface,game.hud.font,r.dish,(panel.x+24,panel.y+62))
        self.text(surface,game.hud.small,r.instruction,(panel.x+24,panel.y+100),theme.MUTED)
        theme.frame(surface,close,theme.CARD);self.text(surface,game.hud.small,'Close',(close.x+13,close.y+8))
        plate=pygame.Rect(body.x,body.y,body.width//2,body.height);theme.frame(surface,plate,theme.CARD,False);self.draw_food(game,plate)
        ticket=pygame.Rect(plate.right+16,body.y,body.width-plate.width-16,body.height);theme.frame(surface,ticket,theme.CARD,False)
        self.text(surface,game.hud.font,'Recipe ticket',(ticket.x+14,ticket.y+12),theme.GOLD)
        if r.mode in ('pour','grill'):
            bar=pygame.Rect(ticket.x+16,ticket.y+70,ticket.width-32,28)
            pygame.draw.rect(surface,theme.BG,bar,border_radius=6)
            band=pygame.Rect(bar.x+round((round_.target-round_.band)*bar.width),bar.y,round(2*round_.band*bar.width),bar.height)
            pygame.draw.rect(surface,theme.GOLD,band,border_radius=4)
            x=bar.x+round(round_.marker*bar.width);pygame.draw.line(surface,theme.TEXT,(x,bar.y-7),(x,bar.bottom+7),4)
            self.text(surface,game.hud.small,'Stop in gold. No rush to start.',(ticket.x+14,ticket.y+122),theme.MUTED)
            phase='Glass '+str(min(round_.step+1,r.steps)) if r.mode=='pour' else 'First side' if round_.step==0 else 'Second side'
            self.text(surface,game.hud.font,phase,(ticket.x+14,ticket.y+151))
        else:
            labels=[r.choices[i] if r.mode=='ingredients' else ARROWS[i] for i in round_.order]
            for i,label in enumerate(labels):
                color=theme.ACCENT if i<round_.step else theme.GOLD if i==round_.step else theme.MUTED
                self.text(surface,game.hud.small,('Done  ' if i<round_.step else str(i+1)+'.  ')+label,(ticket.x+14,ticket.y+43+i*23),color)
        challenge=f'Challenge {round_.level+1} · {round_.mistakes}/3 mistakes'
        if round_.remaining is not None:challenge+=f' · {round_.remaining:.1f}s left'
        self.text(surface,game.hud.small,challenge,(panel.x+24,panel.y+332),theme.GOLD)
        if not self.started or round_.done:
            message=('Served! '+str(round_.score)+'/100 · '+money(self.tip)+' tip; deposit returned.') if round_.complete else ('Order failed. '+money(round_.deposit)+' deposit lost. '+round_.notice) if round_.failed else self.round.notice or f'Ingredient deposit: {money(round(self.store.base_rent*.1))}. Returned on success; lost on failure or quitting. Three mistakes fail the order.'
            for i,line in enumerate(theme.wrap(game.hud.font,message,panel.width-48)):
                self.text(surface,game.hud.font,line,(panel.x+24,panel.y+356+i*26),theme.ACCENT)
            stats=game.courtyard.cooking.get(self.store.name,{'served':0,'best':0,'tips':0,'failed':0})
            self.text(surface,game.hud.small,f"Served: {stats['served']}   Best: {stats['best']}/100   Failed: {stats.get('failed',0)}   Tips: {money(stats['tips'])}",(panel.x+24,panel.y+421),theme.MUTED)
            theme.frame(surface,button,theme.CARD)
            text='Enter / click: Back to courtyard' if round_.done else 'Enter / click: Accept cooking request'
            label=game.hud.font.render(text,True,theme.ACCENT);surface.blit(label,label.get_rect(center=button.center))
        else:
            for i,rect in enumerate(self.choice_rects(surface)):
                theme.frame(surface,rect,theme.CARD)
                prefix=str(i+1)+'  ' if r.mode=='ingredients' else ''
                label=game.hud.font.render(prefix+self.choices()[i],True,theme.TEXT);surface.blit(label,label.get_rect(center=rect.center))
            self.text(surface,game.hud.small,round_.notice or 'Mistakes: -20 score. Three mistakes spoil the order.',(panel.x+24,panel.bottom-62),theme.ACCENT)
        controls='1–5 / click: ingredient' if r.mode=='ingredients' else 'Arrow keys / click: shape or stir' if r.mode in ('fold','stir') else 'Space / click: stop in gold'
        self.text(surface,game.hud.small,controls+'   ·   Esc: abandon order' if self.started and not round_.done else 'Esc: close   ·   Next request after 3–10 minutes of play',(panel.x+24,panel.bottom-28),theme.MUTED)
