# North arcade: cleanup and business progression

The north arcade is the first playable corner of a 3600x2200 mall. Closed east and south grilles and distant storefronts imply more to restore later. The character uses the previous 48x72 display size and 26x30 collision footprint. The freestanding directory prop and world-space area labels are removed; the small HUD map remains.

## A complete first sweep

The layout currently contains 49 starting cleanup tasks. Fifteen familiar positions are supplemented by a deterministic coverage pass that places enough reachable tasks to cover every walkable floor tile within the 115-pixel cleanup radius. The backs of the storefronts are solid, so no task can hide behind shops or above the visible play area. Starting tasks avoid door markers and the player's immediate spawn.

Each task gives $10, removes debris, brightens its local floor patch, briefly animates a broom/grabber, emits pixel dust and displays a reward popup. The HUD reports floor cleanliness and remaining litter. Collecting all starting tasks makes the playable floor 100% clean and permanently completes the first sweep. Benches recover at five tasks; greenery unlocks at five and mosaic at ten; the fountain returns after the entire first sweep.

## Businesses

| Order | Business | Reopening cost | Rent every 5 seconds |
| --- | --- | --- | --- |
| 1 | Pages Bookshop | $100 | $5 |
| 2 | Retro Replay | $250 | $8 |
| 3 | Bean Street | $450 | $12 |
| 4 | The Tailor | $700 | $16 |

Pages can reopen while the initial cleanup is in progress. The other businesses require completing the first sweep and reopening the previous business. Gold markers identify shops ready to reopen. Each reopening deducts its own price, restores that storefront and enables the next business. Rent from all open businesses adds together; opening another shop does not reset the rent timer. The HUD names the next business, its cost and rent.

## Recurring litter

Once the first sweep is complete and at least one shop is open, fresh litter returns every eight seconds, up to twelve active piles. The spawner reuses cleaned starting positions, stays more than 100 pixels from the player, and preserves the initial door clearance. It produces at most one pile per update and does not accumulate a catch-up burst when capped. There is no unbounded growth in trash objects.

New litter dirties nearby floor tiles. Cleaning it gives another $10 and restores the patch; overlapping piles retain the dirt belonging to piles still present. When all active litter is collected, the playable floor is again 100% clean. Fresh litter does not relock businesses, scenery, benches or the fountain.

## Review checklist

1. Start fresh. Press E at the first dust patch; check the tool stroke, sound, popup and floor change.
2. Confirm the previous character size and absence of the freestanding directory/area signs.
3. Clean the arcade and optionally open Pages after earning $100. Follow the remaining-litter count until the floor reaches 100%.
4. After the first sweep and Pages reopening, visit Retro Replay's gold marker and pay $250. Confirm rent now totals $13 every five seconds.
5. Wait eight seconds and find the returning litter. Clean it, confirm its $10 reward and watch its floor patch recover.
6. Continue earning and reopen Bean Street and The Tailor in order. All four businesses together earn $41 every five seconds.
7. Try M for sound, Tab for scenery, resize to 800x600, and walk against the future-gallery grilles.

Audio effects are synthesized at startup with no downloaded audio assets or extra dependencies. Missing audio devices fall back to silent play. The tests cover full floor coverage, reachability/door clearance, one-time and repeated cleanup, bounded spawns, overlapping dirt patches, ordered shop unlocks, affordability and summed rents alongside movement, animation, effects, shutdown and minimum-size rendering.

Progress resets on close. Saving, shoppers, new playable wings, distinctive art for every business and further economic balancing remain future work.
