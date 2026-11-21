# Sampling — news-21nov v2 vs v1

## What changed and why

- **35 stories instead of 42.** v1 graded 0.9741 / rank ~1590. The seven thinnest briefs were cut, keeping only stories with a solid same-day source. Total is now 3 leads + 12 tiles + 20 briefs = 35. The winning template wants 33–52, so 35 is inside the band with denser sourcing per story.
- **Weakest tile replaced.** The Trump-summit tile (thin source) is out; tile 4 is now the AFP migrant-caravan story (about 250 people crossing into Tapachula), a solid wire story with a clear drawn scene.
- **Stats swapped for solid ones.** All six big numbers now trace to a numbered story on the page: €1.58tn (story 1), 6.8 (story 3), 3 (story 2), 14 (story 8), 1.6m (story 31), 486/4 (story 15).
- **Region counts re-derived and asserted.** Asia 6, Europe 7, Middle East 4, Africa 6, Americas 4, Oceania 3, Global 5 — computed from the story list in code and asserted to sum to 35 (Honda/Toyota recall counts as Asia, FBI database hack and MotoGP pole as Global, F1 Las Vegas pole as Global per the template's motorsport treatment).
- **Map pins de-collided.** Brussels, Paris and Geneva sit within a few pixels of each other at this map scale; pins get a small deterministic repulsion pass (max ~a few px) so the numbers stay legible instead of stacking.

## What stayed

The proven winning template, unchanged: cream broadsheet, date as masthead, red italic subhead of the top 3, colour-coded region bar, big-number stats strip, 3-column lead, 12 numbered tiles, "ALSO ON SATURDAY" briefs, pin map, DATE CHECK footer and the LEFT OUT strip. Flat drawn illustration only, no photographs.

## Build

`python3 draw.py` renders at 2048 and downscales to 1024×1024 (LANCZOS); `python3 main.py` copies `entry.png` to `/output/entry.png`. Deterministic: no randomness, no timestamps.
