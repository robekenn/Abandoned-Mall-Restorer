# Abandoned Mall Restorer

[![CI](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml/badge.svg)](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml)

A top-down 2D restoration game built with Python and pygame-ce, without a commercial game engine.

## First playable prototype

Restore the north arcade of Northgate Mall. The 49 starting cleanup tasks cover every walkable floor tile; collecting them all leaves the entire playable floor clean. Each task gives $10 and adds a brief tool stroke, pixel dust, a reward popup and a quiet sound. The freestanding directory prop and floor area labels have been removed; the HUD map shows the larger mall beyond the closed galleries.

The game uses crisp retro pixel sprites (24x24 props, a 16x24 worker displayed at 48x72, and 48x40 storefronts) with four-direction walking animations. Five cleanup tasks restore benches and unlock greenery; ten unlock a mosaic; the complete first sweep restores the fountain. Tab cycles unlocked scenery.

Reopen Pages Bookshop for $100 and earn $5 every five seconds. Completing the first sweep unlocks sequential business restoration: Retro Replay ($250, $8 rent), Bean Street ($450, $12 rent), and The Tailor ($700, $16 rent). Rent adds together across open shops. After the first sweep and the first reopening, fresh litter returns every eight seconds, capped at twelve active piles. Reclean it to restore the floor and keep earning.

Progress resets when you close the game; saving, shoppers and additional playable wings remain future milestones. See [the opening arcade guide](docs/opening-arcade.md) for progression details and a review checklist.

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
- **E:** interact with the closest nearby cleanup spot or shop marker
- **Tab:** cycle unlocked scenery
- **M:** toggle sound
- **Esc:** quit

The camera follows the player. Walls, storefronts, benches, and the fountain block movement. The window is resizable (minimum 800 x 600).

## Development

`game/` owns the loop, settings, and camera; `entities/` owns the player and litter; `mall/` owns the layout and storefronts; `ui/` owns the HUD. Remaining starter modules are placeholders for later systems.

Run the movement, collision, camera, shutdown, and restoration-loop checks:

```bash
python -m unittest discover -s tests -v
```

Tests use SDL's dummy display driver, so they also run without a desktop.

## CI and downloadable builds

GitHub Actions tests Windows, Linux and macOS with Python 3.12/3.13, then builds and smoke-tests standalone packages. Download development builds from the CI run artifacts. Pushing a `v` version tag prepares a draft release after all checks pass. See [CI and release guide](docs/ci-and-releases.md) for local packaging and publishing steps.
