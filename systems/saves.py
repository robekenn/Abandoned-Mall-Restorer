"""Versioned, validated checkpoints with atomic replacement and a recovery backup."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import pygame
from entities.player import Player
from mall.mall import Mall
from systems.upgrades import Upgrades
from systems.requests import OwnerRequests
from systems.shoppers import Shoppers
from systems.janitors import Janitors, Janitor
from systems.story import Story
from systems.mall_life import MallLife, EventSpot
from ui.tutorial import Tutorial


def save_directory():
    if sys.platform=='win32':return Path(os.environ.get('APPDATA',Path.home()))/'MallRestorer'
    if sys.platform=='darwin':return Path.home()/'Library'/'Application Support'/'MallRestorer'
    return Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local'/'share'))/'MallRestorer'


def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def number(value, minimum=0, maximum=10**12, integer=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not minimum<=value<=maximum:
        raise ValueError('Invalid checkpoint number')
    if integer and not isinstance(value,int):raise ValueError('Expected an integer')
    return value


def flag(value):
    if not isinstance(value,bool):raise ValueError('Invalid checkpoint flag')
    return value


def vector(value):
    if not isinstance(value,list) or len(value)!=2:raise ValueError('Invalid checkpoint position')
    return pygame.Vector2(*(number(n,0,10000) for n in value))


def snapshot(game):
    requests=game.owner_requests;tutorial=game.tutorial
    active=None
    if requests.store:
        active={'store':requests.store.name,'parcel':requests.parcel,'progress':requests.progress,
                'greetings':sorted(requests.greetings),'spots':[[s.progress,s.completed] for s in requests.spots]}
    workers={}
    for key,j in game.janitors.people.items():
        target=j.target if j.target and not j.target.cleaned and getattr(j.target,'revision',0)==j.target_revision else None
        workers[key]={'position':list(j.position),'walk':j.walk_level,'clean':j.clean_level,'cleaned':j.cleaned,
                      'earnings':j.earnings,'target':game.mall.trash.index(target) if target else None,
                      'progress':j.progress if target else 0}
    life=game.life
    community={'completed':life.completed,'cooldowns':life.cooldowns,'owner_chats':life.owner_chats,
               'active':life.active,'position':list(life.spot.position) if life.spot else None,'round':life.round,'participants':life.participants}
    return {'life':community,'cash':game.cash,'player':list(game.player.rect.center),'facing':game.player.facing,
            'unlocked':[r.key for r in game.mall.active_regions],
            'stores':{s.name:[s.restored,s.request_level,s.request_bonus,s.recurring_completed,s.request_wait] for s in game.mall.stores},
            'trash':[[t.cleaned,t.ever_cleaned,getattr(t,'revision',0)] for t in game.mall.trash],
            'dirty':[list(p) for p in sorted(game.mall.dirty_tiles)],
            'upgrades':{k:v for k,v in vars(game.upgrades).items() if k.endswith('_level')},
            'held':game.upgrades.held,'fixtures':sorted(game.upgrades.decor),'request':active,'janitors':workers,
            'rent_timer':game.rent_timer,'litter_timer':game.litter_spawner.elapsed,
            'litter_turn':getattr(game.litter_spawner,'turn',0),'visitor_identity':game.shoppers.next_identity,
            'collected':game.total_collected,'sold':game.total_sold,'muted':game.audio.muted,
            'tutorial':{'active':tutorial.active,'step':tutorial.step,'origin':list(getattr(tutorial,'origin',game.player.rect.center)),
                        'collected':getattr(tutorial,'collected',0),'sold':getattr(tutorial,'sold',0),'journal':tutorial.journal_seen},
            'story':{'seed':game.story.seed,'started':game.story.started,'memories':game.story.memories,'completed':game.story.completed,
                     'festival':game.story.festival,'elapsed':game.story.elapsed,'celebrations':game.story.celebrations}}


def restore_state(data, game):
    """Build and validate a replacement world before changing the live game."""
    mall=Mall();u=Upgrades();requests=OwnerRequests();workers=Janitors();story=Story();tutorial=Tutorial()
    if data['unlocked']!=[r.key for r in mall.regions[:len(data['unlocked'])]]:raise ValueError('Invalid section order')
    if len(data['unlocked'])>3:raise ValueError('Too many sections')
    # Geometry activates independently of saved economy, then all state is checked.
    for region in mall.regions[:len(data['unlocked'])]:
        for t in mall.trash:mall.clean_trash(t)
        for s in mall.stores:s.restored=True
        mall.refresh_businesses();mall.unlock_section(region)
    if set(data['stores'])!={s.name for s in mall.stores} or len(data['trash'])!=len(mall.trash):raise ValueError('Checkpoint layout mismatch')
    for s in mall.stores:
        restored,level,bonus,recurring,wait=data['stores'][s.name]
        s.restored=flag(restored);s.request_level=number(level,0,3,True);s.request_bonus=number(bonus,0,10**9)
        s.recurring_completed=number(recurring,0,10**9,True);s.request_wait=number(wait,0,180)
        if s.request_level and (not s.restored or s.upgrade_shop):raise ValueError('Invalid owner progression')
    for t,row in zip(mall.trash,data['trash']):
        cleaned,ever,revision=row;t.cleaned=flag(cleaned);t.ever_cleaned=flag(ever);t.revision=number(revision,0,10**12,True)
        if t.cleaned and not t.ever_cleaned:raise ValueError('Invalid cleanup state')
    mall._initial_cleanup_complete=all(t.ever_cleaned for t in mall.north_trash)
    for region in mall.active_regions:region.initial_cleanup_complete=all(t.ever_cleaned for t in region.trash)
    for region in mall.active_regions:
        if not region.ready(mall):raise ValueError('Unlocked section lacks its prerequisites')
    mall.refresh_businesses()
    dirty={tuple(vector(p)) for p in data['dirty']}
    if not dirty<=set(mall.floor_tiles):raise ValueError('Invalid dirty floor')
    mall.dirty_tiles=dirty
    limits={'capacity_level':5,'value_level':5,'tool_level':3,'advanced_capacity_level':4,'advanced_value_level':3,'speed_level':3}
    for tracks in u.REGIONAL_TRACKS.values():
        for key,_,prices,*_ in tracks:limits[key+'_level']=len(prices)
    if set(data['upgrades'])!=set(limits):raise ValueError('Unknown equipment')
    for key,limit in limits.items():setattr(u,key,number(data['upgrades'][key],0,limit,True))
    u.held=number(data['held'],0,u.capacity,True)
    allowed={o.key for key,*_ in workers.courts(mall) for category in ('Furniture','Garden') for o in u.offers(category,key)}
    u.decor=set(data['fixtures'])
    if not u.decor<=allowed:raise ValueError('Unknown fixture')
    for key,name,area,stores,pool,unlocked,origin in workers.courts(mall):
        if key not in data['janitors']:continue
        if not unlocked:raise ValueError('Janitor in a closed court')
        row=data['janitors'][key];j=Janitor(key,area,origin,mall);j.position=vector(row['position'])
        footprint=pygame.FRect(j.position.x-10,j.position.y-12,20,24)
        if not area.collidepoint(j.position) or any(w.colliderect(footprint) for w in mall.obstacles):raise ValueError('Unsafe janitor position')
        j.walk_level=number(row['walk'],0,3,True);j.clean_level=number(row['clean'],0,3,True)
        j.cleaned=number(row['cleaned'],0,10**12,True);j.earnings=number(row['earnings'])
        j.progress=number(row['progress'],0,j.clean_seconds)
        if row['target'] is not None:
            j.target=mall.trash[number(row['target'],0,len(mall.trash)-1,True)]
            if j.target not in pool or j.target.cleaned:raise ValueError('Invalid janitor target')
            j.target_revision=j.target.revision
            path=j.route_to(j.target.position,mall)
            if path is None:raise ValueError('Unreachable janitor target')
            j.path=[] if j.progress and j.position.distance_to(j.target.position)<.01 else path
        elif j.progress:raise ValueError('Work without a target')
        workers.people[key]=j
    if set(data['janitors'])-{'north','east','garden','commons'}:raise ValueError('Unknown janitor')
    if data['request']:
        row=data['request'];store=next(s for s in mall.stores if s.name==row['store'])
        if not requests.accept(store,mall):raise ValueError('Invalid active request')
        if len(row['spots'])!=len(requests.spots):raise ValueError('Request layout mismatch')
        requests.parcel=flag(row['parcel']);requests.progress=number(row['progress'],0,requests.favor.amount if requests.favor else 0,True)
        limit=requests.favor.amount if requests.favor and requests.needs_greetings else 3
        requests.greetings={number(n,0,10**12,True) for n in row['greetings']}
        if len(requests.greetings)>limit:raise ValueError('Too many greetings')
        for spot,(progress,completed) in zip(requests.spots,row['spots']):
            spot.progress=number(progress,0,spot.duration);spot.completed=flag(completed)
    saved_story=data['story']
    for key in ('started','completed'):
        values=saved_story[key]
        if len(values)!=4:raise ValueError('Invalid chapter count')
        setattr(story,key,[flag(v) for v in values])
    if story.completed!=[True]*sum(story.completed)+[False]*(4-sum(story.completed)):raise ValueError('Invalid chapter order')
    if len(saved_story['memories'])!=4 or any(len(row)!=3 for row in saved_story['memories']):raise ValueError('Invalid memories')
    story.memories=[[flag(v) for v in row] for row in saved_story['memories']]
    story.festival=flag(saved_story['festival']);story.elapsed=number(saved_story['elapsed'],0,10**9)
    if len(saved_story['celebrations'])!=4:raise ValueError('Invalid gatherings')
    story.celebrations=[number(t,0,60) for t in saved_story['celebrations']]
    if story.festival and not all(story.completed):raise ValueError('Festival without chapters')
    if any((story.started[i] or story.completed[i]) and i>len(mall.active_regions) for i in range(4)):raise ValueError('Story in a closed court')
    if any(story.completed[i] and (not story.started[i] or not all(story.memories[i])) for i in range(4)):raise ValueError('Incomplete chapter memory state')
    story.seed=number(saved_story.get('seed',0),0,2**31-1,True)
    story.setup(mall);story.update(0,mall)
    life=MallLife()
    if data.get('life') is not None:
        row=data['life']
        if set(row['completed'])!=set(life.completed) or set(row['cooldowns'])!=set(life.cooldowns):raise ValueError('Invalid community courts')
        life.completed={k:number(row['completed'][k],0,10**9,True) for k in life.completed}
        life.cooldowns={k:number(row['cooldowns'][k],0,life.COOLDOWN) for k in life.cooldowns}
        allowed={s.name for s in mall.stores if s.restored and not s.upgrade_shop}
        if not set(row['owner_chats'])<=allowed:raise ValueError('Unknown owner conversation')
        life.owner_chats={k:number(v,0,10**12,True) for k,v in row['owner_chats'].items()}
        life.active=row['active'];life.round=number(row['round'],0,3,True)
        names=row.get('participants',[])
        if not isinstance(names,list) or len(names)>3 or any(n not in ('Alex','Bea','Sam','Nico','June','Lee','Robin','Kit') for n in names):raise ValueError('Unknown event participants')
        life.participants=names
        if life.active is not None:
            if life.active not in life.completed:raise ValueError('Unknown gathering')
            court=next(c for c in workers.courts(mall) if c[0]==life.active)
            point=vector(row['position']);footprint=pygame.Rect(point.x-90,point.y-82,180,162)
            if not court[5] or not court[2].contains(footprint) or any(w.colliderect(footprint) for w in mall.obstacles):raise ValueError('Unsafe community table')
            life.spot=EventSpot(point,life.event.title)
        elif life.round or row['position'] is not None or life.participants:raise ValueError('Community progress without a gathering')
    life.sync_spots(mall)
    player=Player(vector(data['player']))
    if not any(a.collidepoint(player.rect.center) for a in mall.playable_areas) or any(w.colliderect(player.rect) for w in mall.obstacles):
        # A checkpoint on a grille threshold is moved to the nearest safe floor node.
        safe=[p for p in mall.floor_tiles if not any(w.colliderect(pygame.FRect(p[0]-13,p[1]-15,26,30)) for w in mall.obstacles)]
        player.rect.center=min(safe,key=lambda p:pygame.Vector2(p).distance_squared_to(player.rect.center))
    if data['facing'] not in ('up','down','left','right'):raise ValueError('Invalid player direction')
    player.facing=data['facing']
    row=data['tutorial'];tutorial.active=flag(row['active']);tutorial.step=number(row['step'],0,5,True)
    if tutorial.active and tutorial.step==5:raise ValueError('Invalid guide stage')
    tutorial.origin=vector(row['origin']);tutorial.collected=number(row['collected'],integer=True);tutorial.sold=number(row['sold'],integer=True)
    tutorial.journal_seen=flag(row['journal'])
    shoppers=Shoppers();shoppers.next_identity=number(data['visitor_identity'],integer=True)
    if requests.greetings:shoppers.next_identity=max(shoppers.next_identity,max(requests.greetings)+1)
    state={'mall':mall,'upgrades':u,'owner_requests':requests,'janitors':workers,'story':story,'tutorial':tutorial,
           'life':life,'player':player,'shoppers':shoppers,'cash':number(data['cash']),'rent_timer':number(data['rent_timer'],0,5),
           'total_collected':number(data['collected'],integer=True),'total_sold':number(data['sold'],integer=True)}
    litter_timer=number(data['litter_timer'],0,4);turn=number(data['litter_turn'],0,10**12,True);muted=flag(data['muted'])
    # Commit only after every field passed; a damaged primary can safely fall back.
    for key,value in state.items():setattr(game,key,value)
    game.litter_spawner.elapsed=litter_timer;game.litter_spawner.turn=turn
    if muted!=game.audio.muted:game.audio.toggle()
    game.frame_camera(game.screen.get_size())


class SaveStore:
    VERSION=1

    def __init__(self, directory=None, developer=False, enabled=False):
        self.enabled=enabled;self.path=Path(directory or save_directory())/('developer.json' if developer else 'progress.json')
        self.backup=self.path.with_suffix('.bak');self.status='Not saved yet';self.elapsed=0;self.recovering=False

    def read(self, path):
        if path.stat().st_size>2*1024*1024:raise ValueError('Checkpoint is too large')
        envelope=json.loads(path.read_text(encoding='utf-8'))
        if envelope['version']!=self.VERSION:raise ValueError('Unsupported checkpoint version')
        if envelope['checksum']!=hashlib.sha256(canonical(envelope['data'])).hexdigest():raise ValueError('Checkpoint checksum mismatch')
        return envelope['data']

    def available(self):
        if not self.enabled:return False
        for path in (self.path,self.backup):
            try:self.read(path);return True
            except (OSError,ValueError,KeyError,TypeError):pass
        return False

    @staticmethod
    def atomic(path, content):
        path.parent.mkdir(parents=True,exist_ok=True)
        descriptor,temp=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
        try:
            with os.fdopen(descriptor,'wb') as stream:
                stream.write(content);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)

    def save(self, game):
        if not self.enabled:return False
        try:
            data=snapshot(game);content=canonical({'version':self.VERSION,'data':data,'checksum':hashlib.sha256(canonical(data)).hexdigest()})
            try:
                if not self.recovering:
                    self.read(self.path);self.atomic(self.backup,self.path.read_bytes())
            except (OSError,ValueError,KeyError,TypeError):pass
            self.atomic(self.path,content);self.status='Saved just now';self.elapsed=0;self.recovering=False;return True
        except (OSError,ValueError,TypeError):self.status='Save failed; previous checkpoint retained';return False

    def load(self, game):
        if not self.enabled:return False
        for path in (self.path,self.backup):
            try:
                restore_state(self.read(path),game)
                self.status='Recovered backup' if path==self.backup else 'Checkpoint restored'
                self.elapsed=0;self.recovering=path==self.backup;return True
            except (OSError,ValueError,KeyError,TypeError,IndexError,StopIteration,AttributeError):pass
        self.status='Could not read checkpoint; start a new game or restore a backup';return False
