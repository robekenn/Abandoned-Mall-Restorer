"""Kitchen challenges with limited mistakes, deposits and saved requests."""
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Recipe:
    dish: str
    sprite: str
    mode: str
    instruction: str
    choices: tuple = ()
    steps: int = 3
    color: tuple = (230,194,124)


RECIPES={
    'Hearth Pizza':Recipe('Garden pizza','food_pizza','ingredients','Add the toppings in ticket order.',('Tomato','Basil','Mushroom','Olive','Pepper'),color=(202,106,74)),
    'Mint & Noodles':Recipe('Mint noodle bowl','food_noodles','stir','Alternate left and right. Follow the spoon for six turns.',steps=6,color=(126,181,153)),
    'Orchard Juice':Recipe('Fresh orchard juice','food_juice','pour','Fill two glasses. Stop pouring when the marker is in the gold band.',steps=2,color=(231,168,86)),
    'Sunrise Bakery':Recipe('Hand-rolled croissant','food_pastry','fold','Follow the arrows to fold and roll the dough.',steps=4,color=(215,171,113)),
    'Copper Grill':Recipe('Vegetable skewer','food_grill','grill','Cook each side. Flip, then plate when the marker reaches the gold band.',steps=2,color=(189,131,104)),
    'Garden Bowls':Recipe('Harvest salad','food_salad','ingredients','Layer the ingredients in ticket order.',('Greens','Beans','Tomato','Cucumber','Corn'),color=(148,188,124)),
    'Moonrise Desserts':Recipe('Three-scoop sundae','food_dessert','ingredients','Stack the requested scoops from bottom to top.',('Vanilla','Berry','Chocolate','Mint','Peach'),color=(203,150,180)),
}
ARROWS=('Left','Right','Up','Down')


class CookingRound:
    def __init__(self,name,rng=None,served=0):
        self.name=name;self.recipe=RECIPES[name];rng=rng or random
        self.level=min(5,served//3);self.failed=False;self.total_elapsed=0;self.time_penalty=0;self.deposit=0
        r=self.recipe
        if r.mode=='ingredients':self.order=rng.sample(range(len(r.choices)),r.steps)
        elif r.mode=='stir':
            first=rng.randrange(2);self.order=[(first+i)%2 for i in range(r.steps)]
        elif r.mode=='fold':self.order=[rng.randrange(4) for _ in range(r.steps)]
        else:self.order=[]
        self.targets=[rng.uniform(.35,.7) for _ in range(r.steps)]
        self.step=0;self.mistakes=0;self.elapsed=0;self.notice='';self.rewarded=False

    @property
    def complete(self):return self.step==self.recipe.steps

    @property
    def score(self):return max(0,100-20*self.mistakes)

    @property
    def done(self):return self.complete or self.failed

    @property
    def band(self):return .10-.01*self.level

    @property
    def sweep_seconds(self):return 2.1-.18*self.level

    @property
    def time_limit(self):
        if self.recipe.mode=='ingredients':return 12-1.5*self.level
        if self.recipe.mode in ('pour','grill'):return 20-2*self.level
        return None

    @property
    def remaining(self):
        return max(0,self.time_limit-self.total_elapsed-self.time_penalty) if self.time_limit is not None else None

    @property
    def marker(self):
        phase=(self.elapsed/self.sweep_seconds)%2
        return phase if phase<=1 else 2-phase

    @property
    def target(self):return self.targets[min(self.step,self.recipe.steps-1)]

    def update(self,dt):
        if not self.done:
            self.elapsed+=dt;self.total_elapsed+=dt
            if self.remaining is not None and self.remaining<=0:
                self.failed=True;self.notice='Time ran out. The order could not be served.'

    def action(self,index=0):
        if self.done:return False
        if self.recipe.mode in ('pour','grill'):
            correct=abs(self.marker-self.target)<=self.band+1e-9
        else:correct=index==self.order[self.step]
        if not correct:
            self.mistakes+=1
            if self.recipe.mode=='ingredients':self.time_penalty+=2
            self.notice='A little early or late. Try the gold band again.' if self.recipe.mode in ('pour','grill') else 'Check the highlighted step and try again.'
            if self.mistakes>=3 or self.remaining is not None and self.remaining<=0:
                self.failed=True;self.notice='Order spoiled. The ingredient deposit is lost.'
            return False
        self.step+=1;self.elapsed=0;self.notice='Lovely. Keep going!' if not self.complete else 'Ready to serve!'
        return True

    def finish(self,game,store):
        if not self.done or self.rewarded or self.name!=store.name or not store.restored:return 0
        self.rewarded=True
        tip=round(store.base_rent*.25*self.score/100) if self.complete else 0
        stats=game.courtyard.cooking.setdefault(self.name,{'served':0,'best':0,'tips':0,'failed':0})
        stats.setdefault('failed',0)
        if self.complete:
            stats['served']+=1;stats['best']=max(stats['best'],self.score);stats['tips']+=tip
            game.cash+=self.deposit+tip
        else:stats['failed']=stats.get('failed',0)+1
        game.audio.play('pickup' if self.complete else 'blocked');game.save_checkpoint()
        return tip


class KitchenRequests:
    """One patient request shared by all kitchens, with a live-play cooldown."""
    def __init__(self,rng=None):
        self.rng=rng or random;self.wait=self.rng.uniform(180,600);self.pending=None;self.last=None

    def update(self,dt,game):
        stores=[s for s in game.courtyard.world.stores if s.restored and s.name in RECIPES]
        if self.pending or not stores:return
        self.wait=max(0,self.wait-dt)
        if self.wait>0:return
        choices=[s for s in stores if s.name!=self.last] or stores
        self.pending=self.rng.choice(choices).name
        game.notify(self.pending+' needs a hand cooking. Visit the Courtyard counter.')
        game.save_checkpoint()

    def accept(self,name):
        if self.pending!=name:return False
        self.pending=None;self.last=name;self.wait=self.rng.uniform(180,600)
        return True
