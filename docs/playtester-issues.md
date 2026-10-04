# First release playtester improvements

This PR addresses issues #16–#26 and #28 and prepares v0.1.1. Merging it into main triggers tests, native packages and checksum verification, then publishes the new preview downloads. The published v0.1.0 release remains available.

| Issue | Behavior |
| --- | --- |
| #16 | Nearby litter, quest objects and shop actions take priority over ordinary shopper conversations. Shoppers can still be greeted when there is no competing work target. |
| #17 | Pickup-tool offers describe reach in 64-pixel game tiles. Actual tool balance is preserved. |
| #18 | F2 opens Settings on the opening screen or during play; Pause also has a Settings entry. Music and effects have separate sliders, including dragging. Fullscreen, new-game guide and favor reminders can be toggled. Controls are rebound on two pages, with conflict checks and reserved menu keys. Preferences save separately in settings.json alongside saves; New game does not erase them. |
| #19 | Every equipment shop has a teal UPGRADES sign and a distinctive map color. Early guidance explicitly directs players to Supplies for gear. |
| #20 | Available owner favors have a quiet persistent reminder; newly ready owners show an eight-second summary without repeating sounds. Settings can hide these reminders. |
| #21 | Janitors reconsider nearer reachable litter while walking. They finish an item once cleaning starts, and still protect litter reserved for player requests. |
| #22 | Clicking an upgrade row selects and inspects it. Only the Purchase button or Enter/Space buys it. |
| #23 | The HUD names the active business and owner; its doorway and map position have blue request rings. |
| #24 | North-facing owners' speech sits beside them, away from the worktable. Other quest-object overlap is checked before drawing. |
| #25 | Speech bubbles move with their world anchor and disappear when the speaker leaves the playable viewport. They no longer clamp themselves against the HUD or window edge. |
| #26 | Left-click nearby litter to collect the clicked piece first, within tool reach and bag capacity. Menus, HUD clicks and paused explanations cannot collect litter. |

| #28 | Litter pickup favors count across every open zone, choose 3–10 pieces on acceptance, and preserve that target and progress in saves. Legacy saves retain their original five-piece goal. Janitors reserve only the remaining goal across the mall; recurring litter continues its fair court rotation. |

## Controls

Click an action under Settings → Controls, then press a new key. Duplicate assignments are rejected rather than silently replacing another action. Enter, Space, arrows, Tab, numbered menu shortcuts, F2/F3, and existing menu shortcuts remain reserved. Esc cancels rebinding and always remains a safe way out of menus. Remapped keys work for interactions, journal, guide, skipping, mute, fullscreen, quicksave, pause and WASD movement. Arrow movement remains available. HUD/tutorial/menu hints follow the chosen keys. Restore defaults resets bindings and audio without touching progression.

## Playtest

At 800×600, try Settings from both the opening and Pause, drag both volumes separately, change Interact to Q and Move up to Z, then restart and confirm those settings remain. Check the on-screen prompts and hold-work interactions. Try an occupied key and a reserved menu key. Open an upgrade shop, click several rows and confirm money does not change until Purchase. Approach litter or a quest item while a shopper stands nearby. Accept a north-facing shop request and inspect its worktable with the owner's bubble visible. Walk away from a speaking shopper in each direction. Hire a janitor, watch it change its target as closer litter appears, and verify it still completes five-second cleanups.
