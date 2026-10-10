"""Bounded recurring litter after the initial cleanup is finished."""
import random


class LitterSpawner:
    def __init__(self, interval=4.0, cap=12):
        self.interval = interval
        self.cap = cap
        self.elapsed = 0.0
        self.turn=0
        self.random = random.Random(41)

    def update(self, dt, mall, player_position, requests=None, *, traffic='Steady hours'):
        pools = mall.recurring_pools
        if not pools:
            self.elapsed = 0.0
            return
        # Keep saved progress in baseline seconds so old checkpoints remain valid.
        factor=2 if traffic=='Busy hours' else .5 if traffic=='Quiet hours' else 1
        self.elapsed += dt*factor
        if self.elapsed < self.interval:
            return
        self.elapsed %= self.interval
        order=list(range(len(pools)))
        order=order[self.turn%len(pools):]+order[:self.turn%len(pools)]
        # Rotate fairly between eligible courts, keeping each court's litter cap.
        for i in order:
            pool=pools[i]
            if sum(not t.cleaned for t in pool)>=self.cap:continue
            choices=[t for t in pool if t.cleaned and (player_position is None or t.position.distance_squared_to(player_position)>100**2)]
            if choices:
                mall.respawn_trash(self.random.choice(choices));self.turn=i+1;return
