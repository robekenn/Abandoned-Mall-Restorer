# Mall pixel art v2

The runtime art is hand-authored in game/art.py with a muted 15-color palette. Props use 24x24 transparent canvases, the worker uses 16x24, and storefronts use 48x40 so their doors and windows remain readable. Integer nearest-neighbor scaling keeps square, hard-edged pixels with no smoothing. The previous illustrated atlas is retained as an unused reference asset.

Dirty versions use boarded windows, broken bench slats, dried plants, scattered litter and an empty fountain. Restored versions use cream signs, warm windows, green foliage and blue water. Cleanup progression and Tab scenery choices are unchanged: 5 spots unlock greenery/lamps and recover benches, 10 unlock the mosaic, and the complete first sweep restores the fountain.

The worker has four facing directions with four animation frames per direction. Frames advance every 0.12 seconds during actual movement, and reset to idle when stopped or blocked. Diagonal movement faces its dominant axis, preferring the vertical direction on ties. The worker renders at the earlier 48x72 screen pixel size with a 26x30 collision footprint, independent of sprite frames. Brief broom/grabber strokes accompany cleanup. Local floor restoration and the larger surrounding mall are described in [the opening guide](opening-arcade.md).
