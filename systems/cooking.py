"""Small, forgiving kitchen activities; each completed order pays exactly once."""
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
    def __init__(self,name,rng=None):
        self.name=name;self.recipe=RECIPES[name];rng=rng or random
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
    def score(self):return max(40,100-10*self.mistakes)

    @property
    def marker(self):
        phase=(self.elapsed/2.4)%2
        return phase if phase<=1 else 2-phase

    @property
    def target(self):return self.targets[min(self.step,self.recipe.steps-1)]

    def update(self,dt):
        if not self.complete:self.elapsed+=dt

    def action(self,index=0):
        if self.complete:return False
        if self.recipe.mode in ('pour','grill'):
            correct=abs(self.marker-self.target)<=.13+1e-9
        else:correct=index==self.order[self.step]
        if not correct:
            self.mistakes+=1
            self.notice='A little early or late. Try the gold band again.' if self.recipe.mode in ('pour','grill') else 'Check the highlighted step and try again.'
            return False
        self.step+=1;self.elapsed=0;self.notice='Lovely. Keep going!' if not self.complete else 'Ready to serve!'
        return True

    def finish(self,game,store):
        if not self.complete or self.rewarded or self.name!=store.name or not store.restored:return 0
        self.rewarded=True
        tip=round(store.base_rent*.25*self.score/100)
        stats=game.courtyard.cooking.setdefault(self.name,{'served':0,'best':0,'tips':0})
        stats['served']+=1;stats['best']=max(stats['best'],self.score);stats['tips']+=tip
        game.cash+=tip;game.audio.play('pickup');game.save_checkpoint()
        return tip
