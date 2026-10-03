# Discoveries, storefront lanterns and a shared entrance

The lantern story's chapter goals and rewards are unchanged. This revision makes searching, celebrating and traveling feel more like a physical mall.

## Keepsakes

Each chapter has two keepsakes tucked into distant corners of its court and one held by a named neighbor near the west seating area: Lena, Ash, Tess and Mo. They appear after beginning the chapter at its community board. The item held by the neighbor and the exact floor positions vary between new games, using a saved discovery seed. Continue preserves the same locations and recovered-item flags.

Approach a floor find and press E. Approach a neighbor and press E to hear how they found the object lying around and kept it safe. Talking recovers it without using bag space, even with a full bag. The neighbor remains available afterward; repeated conversations cannot grant another item or cash reward. Neighbors holding keepsakes are community volunteers separate from ordinary shoppers' store visits.

J → Story → R gives a clue for each missing object and its original narrative after recovery. The map marks community boards, rather than revealing the scattered items. A nearby floor find has a small pixel glint. Court positions use collision-safe floor tiles and stay clear of shop interaction markers.

## Lanterns on businesses

After confirming “Bring the neighbors together,” four lanterns hang across the front of each restored business in that court. Strings attach below the upper row's awnings. The north-facing row uses foreshortened rectangular paper lanterns drawn on the same six-pixel grid as its building. Cream top planes, shaded sides, gold panels, wooden caps and tassels keep the original lantern palette. Short strings attach directly to the two front coping panels, with lamp centers 24 pixels inside the front edge and bodies overlapping the shallow facade. The central doorway stays clear. Newly reopened businesses in a completed court also receive lanterns. Unfinished chapters and closed stores have none. The board's floating lantern string is removed; brief celebration confetti remains there.

Gathering destinations stay around the community board, independent of the distant keepsake positions. Ordinary visitors walk there from the shared entrance or their current position. They remain within the usual population limit.

## One public entrance and continuous crossings

A glass main entrance on the exterior west wall of the North arcade is now the only entry/exit point for ordinary shoppers in every court. It has visible doors, a welcome mat and a sign below the delivery station. Visitors for East, Garden and Commons walk the connected concourse instead of appearing or leaving inside those courts. Opening a section extends their navigation graph without recreating existing visitors.

Walkway routes include their off-grid starting and ending joins, check those joins against the visitor footprint, and distinguish an unreachable route from arrival. Visitors become hidden only after crossing their destination shop's door; a finished exit route removes them only at the main entrance. An interrupted or failed route cannot turn into a straight walk through buildings or a disappearance in the middle of the mall.

Camera framing uses world rows with a continuous blend through the north/south corridor. Crossing an east/west boundary or standing between courts no longer switches to the North arcade's camera bias. The opposing storefront row still stays visible when approached. Janitor navigation continues to restrict each worker to its purchased court.

## Refreshed pixel props and cleanup

Native 24×24 litter includes tied bags, folded paper, a discarded cup and a bottle. Stable position-based variants spread these across cleanup locations. These props now render at a proper integer 2× scale. Indoor bins have stainless-steel sides, a disposal slot and a teal recycling panel. Benches have warm wood slats and metal arms; damaged versions retain broken slats and moss.

Four-frame reaching poses and directional pixel brooms/grabbers replace the old line strokes. Watering and setup actions use matching tools. Cleanup chips use paper/metal colors or dusty earth colors. Character scale, body collisions, pickup reach/batches, rent and upgrade prices are unchanged; bench and bin ground footprints still fit their sprites.

## Playtest and saves

Continue works with checkpoints from the first lantern-story build. A checkpoint without the new discovery seed gets a stable seed of zero; its recovered memories, chapter claims, cash, upgrades and owner progress are retained. Further saves preserve that layout. Normal and developer profiles remain separate.

For search testing, start a developer game, F3 → 5 to reach another court if desired, then begin that chapter after finishing the preceding story chapter. F3 → 6 still prepares a chapter, so it deliberately marks all its keepsakes recovered. Use a fresh chapter before pressing 6 when reviewing discovery. J → Story → R supplies clues.

For lantern and traversal review, use F3 → 6 and claim at each board, then walk each connecting corridor. Wait near the main entrance or a shop door to watch visitors' arrivals and departures. Automated checks exercise all forty entrance routes, full visits in both storefront directions in all four courts, collision-safe movement, interrupted routes, player crossings without population resets, continuous camera framing, randomized/saved discoveries, old checkpoint migration, full-bag conversations and lantern attachment.
