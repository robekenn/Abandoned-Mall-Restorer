# Abandoned Mall Restorer

[![CI](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml/badge.svg)](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml)

A top-down 2D restoration game built with Python and pygame-ce, without a commercial game engine.

## First playable prototype

Restore the north arcade of Northgate Mall. Collect litter and dust into a one-item bag, then sell the load at either of two marked trash bins for $1 per item. A full bag blocks further cleanup until sold. The HUD shows cash, bag space, floor cleanliness and one current goal. Press J for the mall journal, map and detailed stats.

Reopen **Northgate Supplies** first for $10. Return to its marker and press E to open the upgrade shop. Buy larger bags (2/4/8/16/20 slots), better recycling contracts ($2/$4/$8/$15/$30 per item), and tools with longer reach and multi-item pickup. Each bench, lamp, planter, fountain and mosaic is purchased separately and adds $1 base rent per five seconds; there is no automatic scenery restoration or Tab scene cycling.

The 48 starting cleanup tasks cover every walkable floor tile. Clearing all of them makes the opening floor 100% clean and unlocks the next business after Supplies: Pages Bookshop ($100, $5 rent), Retro Replay ($250, $8 rent), Bean Street ($450, $12 rent), and The Tailor ($700, $16 rent). Open businesses pay rent every five seconds according to the playable arcade’s floor cleanliness: 0% pays nothing; above 0% and below 50% pays half; 50% through less than 100% pays normal rent; exactly 100% pays 1.5 times rent. Half-dollar payouts are retained. The journal shows the current payout and multiplier. Supplies is an upgrade shop and does not pay rent.

After the first sweep and Supplies reopening, litter returns every **four seconds** (twice the previous rate), capped at twelve recurring piles per eligible section. Reclean it, fill your bag and sell another load. Floor cleanliness recovers fully when all litter is collected; purchased fixtures and businesses remain upgraded.

The east unlock marker stays hidden until all five north businesses reopen. Then pay **$1,500** at the east gate to open the next gallery. Reopen **Eastgate Workshop for $2,000** for 25/30/35/40-item bags (requires the 20-slot Supplies bag), three walking-speed upgrades up to 1.5x, recycling contracts worth $45/$60/$80 per item (requires Supplies’ $30 contract), and east-gallery fixtures. Clean its 42 starting patches and reopen Vinyl & Company and The Green Table for further rent. Both sections have two bins and independent first-sweep progression. Cleanliness now includes all unlocked floors.

A rising chime rewards 1.5x rent; a short low tone and an explanatory message signal full bags and unavailable actions. An original, quiet four-level chiptune loop plays beneath the effects. M mutes music and effects, then resumes music when unmuted.

The game uses crisp pixel sprites with a four-direction animated worker displayed at 48x72. Cleaning produces a brief tool stroke, dust, an item popup and quiet audio. Progress resets on close; saving and the southern galleries remain future milestones. See [the upgrade and opening guide](docs/opening-arcade.md) for prices, controls and a review checklist.

## A mall coming back to life

Shoppers begin returning when stores reopen. They walk around obstacles, enter shops, spend 10–14 seconds inside, walk back out, visit purchased benches and fountains, and leave again. Cleaner floors and restored amenities attract more visitors. Press E near a shopper for a friendly conversation.

Press E at any reopened rent-paying business to meet its owner. Accept a relaxed request with Enter or a click: deliver supplies in a separate satchel, hold E while standing still to water community seedlings, then set up a welcome sign and greet three different visitors. Return to the owner to finish each request. Jobs have no deadlines and are optional; one is active at a time.

These jobs earn three permanent storefront improvements, with +$0.5 / +$1 / +$2 base rent and $50 / $100 / $200 thank-you payments. Each owner offers their first request after three minutes of open-store play; claiming an improvement starts another three-minute wait. There are at most three improvements per business. The HUD tracks one next action; the J-key journal holds the map, blue request markers and owner countdowns. Supplies and Workshop remain equipment shops. See [shoppers and requests](docs/shoppers-and-requests.md) for details.

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
- **E:** collect nearby litter, sell at a trash bin, reopen a business open the east gate, enter an upgrade shop, meet an owner or greet a visitor
- **Hold E while still:** water seedlings or set up a request sign
- **M:** toggle music and effects
- **J:** open/close the journal (map, stats and owner request countdowns)
- **Esc:** close an open menu/journal, or quit from the mall

Inside either upgrade shop, click an upgrade row to buy. Use **1/2/3** or **Tab** to select menu tabs, **Up/Down** to select a row, **Enter** to buy, and **Esc/E** to close. Gameplay and owner request countdowns pause while any menu or the journal is open.

The camera follows the player. Walls, storefronts, trash bins, benches, and the fountain block movement. The window is resizable (minimum 800 x 600).

## Development

`game/` owns the loop, settings, and camera; `entities/` owns the player, litter and bins; `mall/` owns the layout and storefronts; `ui/` owns the HUD. `systems/` owns upgrades, rent rules and bounded recurring litter. Remaining starter modules are placeholders for later systems.

Run the movement, collision, camera, shutdown, restoration, shoppers and request progression checks:

```bash
python -m unittest discover -s tests -v
```

Tests use SDL's dummy display driver, so they also run without a desktop.

## CI and downloadable builds

GitHub Actions tests Windows, Linux and macOS with Python 3.12/3.13, then builds and smoke-tests standalone packages. Download development builds from the CI run artifacts. Pushing a `v` version tag prepares a draft release after all checks pass. See [CI and release guide](docs/ci-and-releases.md) for local packaging and publishing steps.
