"""Bounded recurring litter after the initial cleanup is finished."""
import random


class LitterSpawner:
    def __init__(self, interval=4.0, cap=12):
        self.interval = interval
        self.cap = cap
        self.elapsed = 0.0
        self.random = random.Random(41)

    def update(self, dt, mall, player_position):
        pools = mall.recurring_pools
        if not pools:
            self.elapsed = 0.0
            return
        self.elapsed += dt
        if self.elapsed < self.interval:
            return
        self.elapsed %= self.interval
        pools = [pool for pool in pools if sum(not t.cleaned for t in pool) < self.cap]
        # Reuse the finite starting pool. Keep new litter clear of doors and player.
        choices = [t for pool in pools for t in pool if t.cleaned and t.position.distance_squared_to(player_position) > 100**2]
        if choices:
            mall.respawn_trash(self.random.choice(choices))
