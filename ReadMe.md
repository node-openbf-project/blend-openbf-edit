# blend-openbf-edit
Official OpenBF blender add-on that does the following:

Carries data into OpenBF:
- Physics settings
- Collision shapes/config
- Light / Shadow data
- Path/Curve data

## Useage
- TODO

## Installing
- TODO

## How it's used:
1. Blender used for gfx/anim/physics design

2. OpenBF UI (feature of this script) property tab (Object Properties) controls what gets added

3. glTF exporter exports w/ custom data attributes given by this add-on

4. OpenBF importer handles reading config data from userData/customProperties and mirrors environment from blender.

See OpenBF Wiki for importing glTF w/ extra data:
https://github.com/node-openbf-project/node-openbf-client/wiki