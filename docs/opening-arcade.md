# North arcade: a small beginning

The opening is built around the feeling of one person tending a neglected place much larger than themselves. The worker is drawn at 32x48 screen pixels; the world footprint is 3600x2200. The playable north arcade stays contained inside a 1720x1020 area, while closed grilles, visible distant storefronts and a mall directory establish the east and south galleries as future spaces.

## First five minutes

Start by sweeping the dust directly in front of the worker. The HUD asks for three nearby cleanup tasks, then guides the player toward the $100 needed to reopen Pages Bookshop. Each of the 15 tasks gives $10, removes debris, restores nearby floor tiles, briefly animates a broom or grabber, emits pixel dust, and shows a world-space reward label. The floor brightens locally within 115 world pixels of completed tasks; distant tiles stay neglected.

Milestone messages acknowledge the first task, five tasks, ten tasks and all fifteen. Benches return at five, scenery choices remain unlockable with Tab, and the fountain returns at fifteen. Pages' opening is framed as the first light coming on in a quiet mall, with a warm outline and an opening chime. Rent still arrives every five seconds and produces a brief popup.

## Controls and audio

Existing movement, interaction and scenery controls remain. M toggles sound. Cleanup and milestone effects use small synthesized PCM buffers, generated once at startup with no downloaded sound assets or new dependencies. If SDL cannot open an audio device, gameplay continues silently.

## Review checklist

- Start a fresh run: the nearby dust should be selected, and E should produce one $10 reward, a tool stroke, dust and a cleaner patch.
- Walk around the concourse: the worker should feel small against the storefronts and open floor space.
- Clean five tasks: benches recover and Tab enables greenery.
- Clean ten tasks and reopen Pages: the first warm storefront should stand out against its shuttered neighbors.
- Visit the east and south grilles: the future galleries are visible but remain closed. No gallery unlock mechanic is included in this pass.
- Clean all fifteen tasks: the fountain returns; previously cleaned patches remain visible.
- Try M, resize to 800x600, and move against a grille. Controls and HUD should remain usable.

The review branch does not add persistence, shoppers, more playable wings or new economic systems. Those remain later milestones. Tests cover the existing restoration loop, keyboard handling and animation plus local floor changes, one-time rewards, transient effects, minimum-size rendering, gate collisions and missing audio devices. Real speaker/display behavior and the emotional pacing still need a manual playtest.
