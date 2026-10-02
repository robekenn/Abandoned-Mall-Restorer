# Mall pixel art v2

The runtime art is hand-authored in game/art.py with a muted 15-color palette. Props use 24x24 transparent canvases, the worker uses 16x24, and storefronts use 48x40 so their doors and windows remain readable. Integer nearest-neighbor scaling keeps square, hard-edged pixels with no smoothing. The previous illustrated atlas is retained as an unused reference asset.

Dirty versions use boarded windows, broken bench slats, dried plants, scattered litter and an empty fountain. Restored versions use cream signs, warm windows, green foliage and blue water. Each bench, lamp, planter, fountain and mosaic changes only when its individual upgrade is purchased at its section’s upgrade shop. Unpurchased lamps remain unlit; trash bins use a matching 24x24 sprite. Cleanup restores floor tiles but does not grant free furniture.

The worker has four facing directions with four animation frames per direction. Frames advance every 0.12 seconds during actual movement, and reset to idle when stopped or blocked. Diagonal movement faces its dominant axis, preferring the vertical direction on ties. The worker renders at the earlier 48x72 screen pixel size with a 26x30 collision footprint, independent of sprite frames. Brief broom/grabber strokes accompany cleanup. Local floor restoration and the larger surrounding mall are described in [the opening guide](opening-arcade.md).
