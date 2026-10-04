"""Bounded recurring litter after the initial cleanup is finished."""
import random


class LitterSpawner:
    def __init__(self, interval=4.0, cap=12):
        self.interval = interval
        self.cap = cap
        self.elapsed = 0.0
        self.turn=0
        self.random = random.Random(41)

    def update(self, dt, mall, player_position, requests=None):
        pools = mall.recurring_pools
        if not pools:
            self.elapsed = 0.0
            return
        self.elapsed += dt
        if self.elapsed < self.interval:
            return
        self.elapsed %= self.interval
        order=list(range(len(pools)))
        order=order[self.turn%len(pools):]+order[:self.turn%len(pools)]
        # Fair court rotation preserves the global four-second interval and local caps.
        for i in order:
            pool=pools[i]
            if sum(not t.cleaned for t in pool)>=self.cap:continue
            choices=[t for t in pool if t.cleaned and t.position.distance_squared_to(player_position)>100**2]
            if choices:
                mall.respawn_trash(self.random.choice(choices));self.turn=i+1;return
