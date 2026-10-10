# Runtime and project architecture

`main.py` parses launch options and configures headless SDL before importing
pygame. Interactive launches create `Game` and enter its frame loop. Headless
launches call `game/smoke.py`, whose stages exercise the same game in source
and frozen builds. The smoke harness is imported only for `--smoke-test`.

## A frame of live play

`Game.handle_event()` routes settings, window controls, pause and modal input
before world actions. Custom keys normalize to the existing action keys.
`Game.modal_menus` registers menus that block world input and simulation;
`Game.world_paused` also includes the welcome screen and tutorial explanations.
Menu registration doesn't automatically provide rendering or input handlers.

`Game.update()` handles the welcome transition and pauses before ticking a
scene. Cooking updates only its active round; settings and pause freeze that
round too. Tutorial practice permits normal play, while its explanations pause.

The indoor branch moves the player and updates story, community and owner
activities. The courtyard branch delegates local movement and feedback to
`Courtyard.update()`. Both call `Game.update_shared_worlds()` once to advance
indoor shoppers, courtyard shoppers and travel, recurring litter, and hired
janitors in that order. Offscreen maps stay active after unlocking; the locked
courtyard remains unallocated. Kitchen cooldowns tick with courtyard visitors
even while the player is indoors.

Both branches finish with `Game.update_income_and_autosave()`. It preserves a
single rent phase across scene transitions, combines indoor and courtyard
income, displays the payout over the player, and advances autosaving. Local
cleanliness still affects each area's rent. `Game.cleanliness` is a separate,
floor-weighted total for the HUD. Menus, tutorial explanations and cooking freeze
the shared simulation and its rent/autosave timers. Continue grants no offline
simulation or earnings.

`Game.draw()` renders only the active scene. Collision uses world coordinates;
`Camera` converts them for drawing and click targets. People and furniture use
depth ordering. Shared UI uses `ui/theme.py`, `HUD`, and the common marker helper
on `Store`; outdoor and indoor progress should read consistently.

## Checkpoints and settings

`game/storage.py` contains only standard-library code for platform data paths
and atomic writes. Both settings and checkpoints use it, so settings no longer
import world construction or save migrations.

`systems/saves.py` snapshots progression into a checksummed, versioned envelope.
Restoring first creates and validates replacement objects, then commits them
to `Game`. Invalid primary checkpoints can fall back to the previous backup.
Seating layouts and optional courtyard/kitchen fields have compatibility paths;
keep those paths when changing serialization. Runtime visitor routes and
unfinished cooking rounds are transient; consumed cooking deposits and the
individual kitchen cooldowns already save when an order is accepted.

The existing per-user `MallRestorer` directory contains `progress.json`,
`developer.json`, recovery `.bak` files and separate `settings.json`. Source and
frozen launches use the same directory. Tests disable persistence or supply a
temporary directory. Atomic writes flush a temporary sibling and replace the
destination only after flushing succeeds.

## Configuration and production checks

Layouts and economy definitions currently live in Python modules such as
`mall/mall.py`, `mall/section.py`, `mall/courtyard.py`, `systems/upgrades.py` and
`systems/cooking.py`. The empty `data/*.json` files are legacy scaffolding.
Pixel art and audio are generated locally, without an asset download. Consult
[art direction](art-direction.md) before extending the sprite system.

The repository uses `unittest` plus focused Ruff correctness checks. CI tests
Python 3.12/3.13 on all three platforms, then runs native PyInstaller builds.
`scripts/build_release.py` smoke-tests both modes outside the source directory,
archives the build and streams its SHA-256 calculation. Checksum files use LF
on Windows as well as Unix. See [contributing](../CONTRIBUTING.md) for commands
and [CI and releases](ci-and-releases.md) for publication.
