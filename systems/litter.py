"""Bounded recurring litter after the initial cleanup is finished."""
import random


class LitterSpawner:
    def __init__(self, interval=8.0, cap=12):
        self.interval = interval
        self.cap = cap
        self.elapsed = 0.0
        self.random = random.Random(41)

    def update(self, dt, mall, player_position):
        if not mall.initial_cleanup_complete or not any(s.restored for s in mall.stores):
            self.elapsed = 0.0
            return
        self.elapsed += dt
        if self.elapsed < self.interval:
            return
        self.elapsed %= self.interval
        if mall.active_litter_count >= self.cap:
            return
        # Reuse the finite starting pool. Keep new litter clear of doors and player.
        choices = [t for t in mall.trash if t.cleaned and t.position.distance_squared_to(player_position) > 100**2]
        if choices:
            mall.respawn_trash(self.random.choice(choices))
