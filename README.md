# Abandoned Mall Restorer

[![CI](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml/badge.svg)](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml)

A top-down 2D restoration game built with Python and pygame-ce, without a commercial game engine.

## A small beginning

The game starts fullscreen on a short introduction to Northgate’s story. Choose **Start restoring** or press **Enter/Space** to fade into the mall. After a checkpoint exists, **Continue** resumes it; **New game / N** asks for a second confirmation. Movement, litter and rent stay paused until the transition finishes. **F11** switches to a window; `python main.py --windowed` starts windowed instead. Music can be muted on the opening screen with **M**. The optional first-steps guide can be disabled before starting, skipped with **T**, or replayed with **H**.

## First playable prototype

Restore the north arcade of Northgate Mall. Collect litter and dust into a one-item bag, then sell the load at either of two marked trash bins for $1 per item. A full bag blocks further cleanup until sold. The HUD shows cash, bag space, floor cleanliness and one current goal. Press J for the mall journal, map, story and detailed stats.

Reopen **Northgate Supplies** first for $10. Return to its marker and press E to open the upgrade shop. Buy larger bags (2/4/8/16/20 slots), better recycling contracts ($2/$4/$8/$15/$30 per item), and tools with longer reach and multi-item pickup. Each bench, lamp, planter, fountain and mosaic is purchased separately and adds $1 base rent per five seconds; there is no automatic scenery restoration or Tab scene cycling.

The 63 starting cleanup tasks cover the entire concourse floor, including beneath furniture. Clearing all of them makes the opening floor 100% clean and unlocks the next business after Supplies: Pages Bookshop ($100, $5 rent), Retro Replay ($250, $8 rent), Bean Street ($450, $12 rent), and The Tailor ($700, $16 rent). Open businesses pay rent every five seconds according to the playable arcade’s floor cleanliness: 0% pays nothing; above 0% and below 50% pays half; 50% through less than 100% pays normal rent; exactly 100% pays 1.5 times rent. Half-dollar payouts are retained. The journal shows the current payout and multiplier. Supplies is an upgrade shop and does not pay rent.

After the first sweep and Supplies reopening, litter returns every **four seconds** (twice the previous rate), capped at twelve recurring piles per eligible section. Eligible courts take turns; janitors reserve the litter needed for an active local collection favor. Reclean it, fill your bag and sell another load. Floor cleanliness recovers fully when all litter is collected; purchased fixtures and businesses remain upgraded.

The east unlock marker stays hidden until all ten north businesses reopen. Then pay **$1,500** at the east gate to open the next gallery. Reopen **Eastgate Workshop for $2,000** for 25/30/35/40-item bags (requires the 20-slot Supplies bag), three walking-speed upgrades up to 1.5x, recycling contracts worth $45/$60/$80 per item (requires Supplies’ $30 contract), and east-gallery fixtures. Clean its 56 starting patches and reopen Vinyl & Company, The Green Table, Copper Kettle and Secondhand Stars. Finish the east businesses to unlock **Garden Arcade ($10,000)**, then finish Garden to unlock **Community Commons ($35,000)**. All four areas have ten businesses, with five on each side of the court, an equipment shop, two bins, a delivery station and independent first-sweep progression. Cleanliness now includes all unlocked floors.

A rising chime rewards 1.5x rent; a short low tone and an explanatory message signal full bags and unavailable actions. An original, quiet four-level chiptune loop plays beneath the effects. M mutes music and effects, then resumes music when unmuted.

The game uses crisp pixel sprites with a four-direction animated worker displayed at 48x72. Rounded silhouettes, shaded clothes and distinct hairstyles keep the warm pixel-art palette. Janitors animate with a broom for dirt and a grabber for litter, using the same tool strokes as the player. Cleaning produces a brief tool stroke, dust, an item popup and quiet audio. Progress now saves automatically, with Continue on the opening screen and a separate developer slot. F5 saves manually. See [the upgrade and opening guide](docs/opening-arcade.md) for prices, controls and a review checklist.

## A mall coming back to life

Shoppers begin returning when stores reopen. Every visitor uses one visible main entrance on the North arcade’s exterior west wall and walks through the connected courts. They walk around obstacles, enter shops, spend 10–14 seconds inside, walk back out, visit purchased benches and fountains, and leave again. Cleaner floors and restored amenities attract more visitors. Some visitors browse a second local shop on clean floors, carry purchases after shopping, sit on restored benches, pause by fountains, or meet a friend. Purchased amenities and clean floors encourage longer visits. Press E near a shopper for a friendly conversation in a speech bubble above their head. Speakers pause so you can read; routine pickups, sales and successful purchases use visual feedback without bottom-message chatter.

Open **J → Mall life** (journal key **4**) to host an optional community gathering. Each court needs two reopened regular shops and at least 50% local cleanliness. Book swaps, café tastings, plant sales and evening makers markets rotate after each completed gathering. Visit the gold-marked community table and listen to three neighbors before choosing something they will enjoy. There is no deadline or penalty for trying again. Completion pays $200/$500/$1,000/$1,800 by court; the next gathering becomes available after five minutes of play. Progress and owner conversations save with the existing checkpoint.

**Esc** opens a pause screen, freezing movement, work, rent and event timers. Resume, save, or choose Exit game and confirm. Closing the window also asks for confirmation. The default confirmation is to stay; a failed save keeps the game open and offers a deliberate exit without saving.

Press E at any reopened rent-paying business to meet its owner. **C / Just chat** shares a personal memory or a reaction to the mall; these conversations develop as the owner earns improvements. Owners appear by their doors while speaking. Accept a relaxed request with Enter or a click: collect supplies from a permanent DELIVERIES station in a separate satchel, arrange a shop-specific window display by matching three products to the owner’s shelf plan, then set up a welcome sign and greet three different visitors. Return to the owner to finish each request. Jobs have no deadlines and are optional; one is active at a time.

These jobs earn three permanent storefront improvements, with +$0.5 / +$1 / +$2 base rent and $50 / $100 / $200 thank-you payments. Each owner offers their first request after three minutes of open-store play; claiming an improvement starts another three-minute wait. After those three improvements, owners rotate through twelve repeatable community favors. Each pays cash; four favor types also add $0.50 permanent base rent. A fresh three-minute wait follows every claim. Litter pickup favors ask for a random 3–10 pieces from anywhere in the mall, with the target preserved through Continue. The HUD tracks one next action; the J-key journal holds the map, blue request markers and owner countdowns. Each section’s first business remains an equipment shop. See [shoppers and requests](docs/shoppers-and-requests.md) and [community favors and expansion](docs/community-favors-and-expansion.md) for details.

## The winter lantern walk

You return to the mall you visited as a child. Mara, Remy, Fern and Wren help recover its neighborhood festival through four chapters: reading, music, lantern-making and a shared table. Find the gold community boards, discover two scattered keepsakes and talk to a neighbor holding a third in each court, reopen six businesses, help owners twice and restore three local fixtures. Earlier work counts. Chapters hang pixel lanterns on restored storefronts and bring gatherings of real shoppers and one-time rewards; the final lantern walk leaves the mall playable. **J → Story** tracks goals; **R** reads your keepsakes. See [discovery and court transitions](docs/court-transitions-and-discovery.md) for the new search mechanics and entrance, and [saving and the lantern story](docs/saving-and-lantern-story.md) for the narrative, save locations and review guide.

## Run on Windows

Install Python 3.12 or newer. Download this repository or pull the latest changes, open a terminal in its folder, then run:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Run on macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Controls

- **WASD / Arrow keys:** move
- **E:** collect nearby litter, sell at a trash bin, reopen a business, open a section gate, enter an upgrade shop, meet an owner, greet a visitor or read a community board / keepsake
- **Hold E while still:** set up a request sign
- **1–3 / click in a display task:** place a product; **Backspace** undoes a choice
- **H:** replay the optional tutorial; **T:** skip an active tutorial
- **M:** toggle music and effects
- **F5:** save a checkpoint
- **F11:** switch between fullscreen and a resizable window
- **J:** open/close the journal (map, stats, owner countdowns, janitors and story)
- **Esc:** close an open menu/journal, or pause from the mall; exiting requires confirmation

Inside any upgrade shop, click an upgrade row to buy. Use **1/2/3** or **Tab** to select menu tabs, **Up/Down** to select a row, **Enter** to buy, and **Esc/E** to close. Gameplay and owner request countdowns pause while any menu or the journal is open.

Each court now has five shops on either side. After reopening the original row, continue through five opposing businesses before the next section gate appears. Hire one janitor per unlocked section through **J → Janitors**. Janitors stay local, walk slowly, spend five seconds on each piece and automatically sell it for 75% of your current trash value. Upgrade cleaning and walking speeds separately in the same tab. See [courts and janitors](docs/courts-and-janitors.md) for prices.

The camera follows the player and shifts its framing toward the nearby storefront row. Walls, storefronts, delivery platforms, bins, benches, and the fountain block movement. Bench and fountain collisions follow the visible ground bases; people render behind tall props when passing behind them. Floor beneath furniture gets dirty and cleans with nearby litter, like the rest of the concourse. The window is resizable (minimum 800 x 600).

## Development

`game/` owns the loop, settings, and camera; `entities/` owns the player, litter and bins; `mall/` owns the layout and storefronts; `ui/` owns the HUD. `systems/` owns upgrades, rent rules and bounded recurring litter. Remaining starter modules are placeholders for later systems.

Run the movement, collision, camera, shutdown, restoration, shoppers and request progression checks:

```bash
python -m unittest discover -s tests -v
```

Tests use SDL's dummy display driver, so they also run without a desktop.

## Developer playtesting

Launch with `python main.py --dev` (Windows: `py main.py --dev`). After starting, press **F3** to add $10,000/$100,000/$1,000,000, clean the current court or jump to the next area. Use 1–7 or click a button; **6** prepares the next story chapter and takes you to its community board. **7** prepares a community gathering in the current court. F3/Esc closes the panel. These controls are disabled during normal launches. See [developer playtesting](docs/developer-playtesting.md) for windowed and packaged-build commands.

## CI and downloadable builds

GitHub Actions tests Windows, Linux and macOS with Python 3.12/3.13, then builds and smoke-tests standalone packages. Download development builds from the CI run artifacts. Pushing a `v` version tag prepares a draft release after all checks pass. See [CI and release guide](docs/ci-and-releases.md) for local packaging and publishing steps.

See [mall life and community gatherings](docs/mall-life.md) for events, evolving conversations and the new exit flow.

### Calmer first steps and event variety

The H-key guide now pauses for your character’s explanations and resumes for real practice; T skips it. Recurring owner favors wait a random 3–10 minutes after the first three projects. Gatherings offer book matching, cafe preparation, scattered planting and makers-material hunts, with court-specific completed story boards. See [playtest notes](docs/calm-guide-and-event-variety.md).

### Downloadable releases

Merging PR #27 publishes **v0.1.1 — Playable Preview** after all platform tests and packaged launch checks pass. Windows, Linux and Apple-silicon macOS downloads appear on the [Releases page](https://github.com/robekenn/Abandoned-Mall-Restorer/releases). Python is not required. See the [v0.1.1 release notes](docs/releases/v0.1.1.md) and [release workflow guide](docs/ci-and-releases.md).

### Playtester controls and settings

Open **F2 → Settings** or **Esc → Settings** for independent music/effects sliders, fullscreen, tutorial/reminder preferences, and custom keys. Upgrade rows are now inspect-only; use the Purchase button or Enter to buy. Equipment shops are marked UPGRADES, and active owner favors identify their business. See [issue-by-issue changes and playtest notes](docs/playtester-issues.md).

### Courtyard and social visitors (development branch)

Families and teen groups join shoppers, busy/quiet hours vary foot traffic, and restored indoor seating provides places to sit and chat. Story boards move to room edges and keepsake-givers leave after handing over their finds. From Community Commons, complete its sweep and reopen six businesses to pay $50,000 once with E at the hanging Courtyard wall sign, then walk through its opening in either direction. Outside is a separate food-court map with seven restaurants, picnic seating, and service, comfort and compost upgrades. Both maps and your current location save through Continue. Wait for a kitchen help request (one every 3–10 minutes of live play), then visit its counter with E or a click to cook: top pizza, stir noodles, pour juice, roll pastry, flip skewers, layer salads or stack sundaes. Varied recipe tickets guide each activity; completed orders earn tips and save per-kitchen records. Ingredient deposits are refunded on success and lost on failure or abandonment. Three mistakes spoil an order; timing bands tighten and ingredient deadlines shorten every three successful orders per kitchen. Cooking is optional and pauses the mall. See [Courtyard and social life](docs/courtyard-and-social-life.md) for progression and review steps.

Food-court visitors now walk from the front entrance through the mall to the Courtyard, queue at visible restaurant counters, and return indoors carrying restaurant-specific food. Outside, J → Janitors hires the local cleaner with saved upgrades and partial work. Larger framed doors, restored picnic benches, kitchen-side herb boxes, a framed Provisions sign and five-second rent popups improve courtyard readability. Indoor Furniture purchases repair visibly broken benches.
