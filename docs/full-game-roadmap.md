# Marty's Mall: build and review in sections

Marty is the returning player character. Northgate remains the fictional mall.
The full story follows Marty and the neighbors restoring a place they can share,
culminating in the winter lantern walk. Each section gets a focused PR and a
playtest point before the next major addition.

| Section | Scope | What to review |
| --- | --- | --- |
| 1: One door and First lights | Marty's arrival, Mara's reading-circle project, responsive dialogue and a gathering at the restored west table | Opening tone, clear objectives, first reward timing, mouse/keyboard controls and Continue |
| 2: Restoration workshop | A compact new room, one complete hands-on repair project and approved object finishes/locations | Whether repair feels satisfying and different from cleanup; safe routes and saved projects |
| 3: East and Silver Screen | Remy's story, an interior for the existing cinema and program selection/hosting | Character development, audience behavior and a worthwhile repeatable activity |
| 4: Garden and rooftop greenhouse | Fern's story, roof access, planting and useful harvests | Calm growing pace, live-time/pause rules and Courtyard connections |
| 5: Commons and the next light | Wren's story, shared preparations, a neighborhood supper, lantern walk and epilogue | A clear emotional payoff, callbacks to restored spaces and uninterrupted postgame play |
| 6: Whole-game polish | Dialogue consistency, pacing, presentation, accessibility and end-to-end validation | A complete playthrough on supported platforms with real drivers |

## Section 1: current review slice

The opening menu and first-steps guide introduce Marty. Mara recalls the crooked
lantern Marty chose as a child and proposes a first reading circle. A new reader's
request nudges her toward welcoming new stories as well as remembering old ones.

Read the gold North community board to accept her project. It requires:

1. Reopen Pages Bookshop.
2. Complete the North arcade's first sweep.
3. Recover the photograph, drawing and festival program through the existing
   gold keepsake markers and neighbor encounter.
4. Buy **Restore table 1** from **Supplies → Furniture** ($70).
5. Buy that table's **left and right chairs** separately ($35 each).

The table is the existing west table; its position and collision do not change.
The first chapter no longer requires six businesses, two owner favors and any
three local fixtures. Its existing $1,000 thank-you is consequently available
earlier. Other shop, upgrade, gate and story reward prices stay the same.

Return to the community board and choose **Gather the first readers** with Enter
or a click. Three visitors use normal safe paths toward the west reading table,
lanterns appear as before, and Mara points Marty toward Remy in East. Just chat
and the Story journal respond to the current project step. Owner requests remain
independent, optional activities.

Existing restoration counts immediately. Partial projects resume from ordinary
store, fixture and keepsake state. Older completed North chapters retain their
achievement and cannot pay again; they do not require buying this table again.
The later three chapters remain playable with their current content while their
sections await implementation. The workshop is section 2; completing section 1
will not create a requirement to replay it when the workshop arrives.

## Playtest section 1

- Start a new named game and read Marty's opening thoughts. Check practice,
  Skip guide, Help and the clickable Menu/Back paths.
- Read Mara's North board, then close it. Confirm the story stays optional and
  the board, HUD and J → Story give a useful next step.
- Complete the sweep, reopen Supplies and Pages, and find the three keepsakes.
  Restore table 1 first, then each of its two chairs through the purchase button.
- Try to finish with a chair missing or with three unrelated fixtures instead.
  Neither should complete the reading circle or award its thank-you.
- Finish using either Enter or the button. Follow the visitors toward the west
  table. Revisit the board and talk to Mara; repeat invitations must not pay again.
- Exit midway through the project and Continue. Also load a checkpoint with
  First lights already completed. Check that progress, money and fixtures survive.
- At 800 × 600, check the tutorial, Mara's dialog, goals, keycaps and return paths.
  Rebind the interaction/journal keys and check their hints.
- For a quick completion check, launch with --dev and use F3 → 6. This prepares
  the current chapter but still requires claiming through the actual story dialog.

The next section begins after this slice has been reviewed. Every implementation
keeps existing saves and the core pause, input and offscreen simulation rules.
