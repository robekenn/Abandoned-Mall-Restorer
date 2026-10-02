# Mall sprite set v1

Generated with the built-in image generation tool. Source atlas: assets/sprites/mall_atlas.png. Runtime source bounds and sprite names: game/art.py. All sixteen sprites are loaded with transparency and scaled with a cache. Paths work independently of the terminal's current directory.

Prompt specification: one transparent square 4-by-4 sprite atlas for a top-down abandoned mall; detailed illustrated pixel-art style; dusty teal, faded cream, ochre, rust and charcoal, with amber restored lighting; isolated objects with generous padding; no text or background. Rows: abandoned/restored bookshop and cafe; garbage bags, paper/cup/can litter, dirt stain, broken bench; restored bench, dry/restored fountain, dead planter; lush planter, lamp, maintenance worker, mosaic. Preserve the visible contrast between neglect and warm restoration.

Scenery progression in this version: 5 cleaned spots unlock the greenery/lamp style, 10 unlock mosaic decor, and 15 restore the fountain. Tab cycles only unlocked styles. Benches recover after five spots; opening the bookshop replaces its boarded sprite. Decorative plants and lamps are nonblocking; bench, fountain and store collision footprints are retained from the prototype.

This is the complete art set for the current prototype, not the final game's full animation or tile library. The player currently has one static sprite; walking/directional animation, more store types, wall and floor texture tiles, and custom furniture placement remain future work.
