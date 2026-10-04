"""Native pixel art for patio kitchens, dining and planting."""
import pygame
from game.art import canvas,box


def food_stall(variant,opened,north=False):
    s=canvas((60,40));accent=('teal','rust','green','gold','wood','rust','green','teal')[variant]
    box(s,'ink',(1,3,58,35));box(s,'wood' if opened else 'shadow',(3,6,54,29))
    box(s,'cream' if opened else 'stone',(4,7,52,7))
    for x in range(3,57,6):box(s,accent if opened else 'shadow',(x,14,5,6))
    box(s,'ink',(8,21,43,12));box(s,'gold' if opened else 'shadow',(10,23,39,9))
    box(s,'wood',(7,31,46,3));box(s,'cream',(8,31,43,1))
    if opened:
        # Each kitchen has a distinct counter display: oven, noodles, fruit or pastries.
        for x in (13,25,37):
            if variant==0:
                box(s,'wood',(x,25,7,6));box(s,'cream',(x+1,27,5,1));box(s,'leaf',(x+2,24,3,2))
            elif variant==1:
                box(s,'rust',(x,25,7,5));box(s,'ink',(x+2,26,3,3));box(s,'gold',(x+3,28,1,1))
            elif variant==2:
                box(s,'cream',(x,28,7,2));box(s,'leaf',(x+1,26,5,2));box(s,'wood',(x+2,23,1,5))
            elif variant==3:
                box(s,'cream',(x+1,25,5,6));box(s,'rust',(x+2,27,3,3));box(s,'leaf',(x+3,22,1,4))
            elif variant==4:
                box(s,'cream',(x,29,7,1));box(s,'wood',(x+1,26,5,3));box(s,'gold',(x+2,26,1,2))
            elif variant==5:
                box(s,'ink',(x,26,7,4));box(s,'stone',(x+1,27,5,1));box(s,'rust',(x+2,24,4,2))
            elif variant==6:
                box(s,'cream',(x,27,7,3));box(s,'green',(x+1,25,5,3));box(s,'leaf',(x+2,24,2,2))
            else:
                box(s,'cream',(x,27,7,3));box(s,'rust',(x+1,25,5,3));box(s,'gold',(x+3,24,1,1))
    else:
        for y in range(22,32,3):box(s,'stone',(9,y,41,1))
    for x in (4,54):box(s,'green',(x,30,3,6))
    if north:
        # Draw a north-facing counter, keeping signage, food and plants upright.
        counter=s.subsurface((7,21,46,13)).copy()
        roof=s.subsurface((3,7,54,13)).copy()
        box(s,'wood' if opened else 'shadow',(3,6,54,29))
        s.blit(counter,(7,6));s.blit(roof,(3,23))
        box(s,'ink',(3,35,54,2));box(s,'cream' if opened else 'stone',(4,34,52,1))
        for x in (4,54):box(s,'green',(x,17,3,6))
    return s


def doors():
    s=canvas((24,32));box(s,'ink',(1,1,22,30));box(s,'wood',(2,2,20,28))
    for x in (4,13):
        box(s,'teal',(x,4,7,23));box(s,'water',(x+1,5,5,12));box(s,'cream',(x+4,20,1,2))
    box(s,'gold',(2,1,20,3));box(s,'stone',(1,29,22,2));return s


def picnic():
    s=canvas((32,28));box(s,'ink',(4,12,24,3));box(s,'wood',(5,10,22,5))
    box(s,'cream',(7,11,18,1));box(s,'wood',(7,17,3,8));box(s,'wood',(22,17,3,8))
    box(s,'teal',(0,16,5,6));box(s,'teal',(27,16,5,6))
    box(s,'wood',(16,3,1,9));pygame.draw.polygon(s,'#dfb45e',[(6,7),(16,0),(26,7)])
    box(s,'cream',(6,7,20,2));box(s,'rust',(13,10,3,3));return s


def herbs():
    s=canvas((24,32));box(s,'ink',(3,19,18,10));box(s,'rust',(4,20,16,8));box(s,'wood',(2,18,20,3))
    for x in (7,12,17):
        box(s,'green',(x,7,2,13));box(s,'leaf',(x-3,9,3,3));box(s,'leaf',(x+2,5,3,4));box(s,'green',(x-2,14,3,3))
    box(s,'cream',(6,24,12,1));return s


def lights():
    s=canvas((48,24));box(s,'wood',(2,2,2,21));box(s,'wood',(44,2,2,21))
    pygame.draw.lines(s,'#856448',False,[(3,3),(24,8),(45,3)],1)
    for x,y in ((9,5),(18,7),(28,7),(37,5)):
        box(s,'cream',(x,y,3,4));box(s,'gold',(x+1,y+1,1,3))
    return s


def patio_tree():
    s=canvas((24,36));box(s,'ink',(10,22,5,12));box(s,'wood',(11,20,3,12))
    for rect,color in (((4,5,15,19),'green'),((1,10,21,10),'green'),((7,2,10,9),'leaf'),((3,9,10,7),'leaf'),((13,15,7,6),'teal')):box(s,color,rect)
    box(s,'rust',(6,31,13,4));box(s,'cream',(7,31,11,1));return s


def install(art):
    for v in range(8):
        for opened in (True,False):art.sprites[f'food_stall_{v}_'+('open' if opened else 'closed')]=food_stall(v,opened)
    for v in range(8):
        for state in ('open','closed'):
            art.sprites[f'food_stall_{v}_{state}_up']=food_stall(v,state=='open',north=True)
    art.sprites.update(courtyard_doors=doors(),courtyard_table=picnic(),herb_planter=herbs(),patio_lights=lights(),patio_tree=patio_tree())
