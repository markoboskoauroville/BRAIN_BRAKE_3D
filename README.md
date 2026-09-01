# BRAIN_BRAKE_3D

The 3D work for THE BRAIN BRAKE: the brass key, modelled in Python, rendered in Blender. It lives
apart from the film repository and the animator site so it never competes with them for space.

## Layout

    mesh/        the obj and anything else geometric
    scripts/     the python that builds, lights and renders
    renders/     ignored by git. Output lands here and is never committed, because it regenerates.
    stills/      the handful of renders actually chosen, small jpg only

## Rendering, headless

Blender never needs opening. From the repository root:

    /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_key.py

That imports `mesh/brain_break_key.obj`, builds the two materials (`KEY_REAL` brass and `KEY_DRAWN`
paper), lights it, and writes twelve stills into `renders/`: six brass, six drawn, the key turning.

`scripts/brain_break_key_source.py` regenerates the mesh itself, in plain Python.
`scripts/brain_break_key_blender.py` builds the key inside Blender with both materials.

## The size rule

Keep this repository far under 1 GB. Commit the mesh, the scripts and a few chosen stills as JPEGs.
Never commit a render sequence, never commit a `.blend` with packed textures, never commit anything a
script can produce again. A PNG sequence is an export, not history, and it stays in `renders/`.
