# Where everything is, for the Blender build and its tools (the restructure, 20 October 2026). One world is built at a
# time: WORLD in the environment, else project.godot's erasmus/world, else "barcelona".
import os, re

BUILDER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILDER)


def _world():
    if os.environ.get('WORLD'):
        return os.environ['WORLD']
    try:
        m = re.search(r'^world="([^"]+)"', open(os.path.join(ROOT, 'project.godot')).read(), re.M)
        return m.group(1) if m else 'barcelona'
    except OSError:
        return 'barcelona'


WORLD = _world()
WORLD_DIR = os.path.join(ROOT, 'worlds', WORLD)
BUILD = os.path.join(WORLD_DIR, 'build')      # the world's own Blender scripts (its ground, buildings, rooms, layout)
DATA = os.path.join(WORLD_DIR, 'data')        # its data (data3d.json: people, missions, items, rooms, the 2D map's tiles)
MAP = os.path.join(WORLD_DIR, 'map')          # the painted map shown with M
# (24 October 2026) The big files sit in bigfiles/, kept off GitHub and handed over by Google Drive (bigfiles/README.md)
BIG = os.path.join(ROOT, 'bigfiles')
OUT = os.path.join(BIG, 'built', WORLD)       # what the build makes: city.glb, interior.glb, scene.json, light maps
MESHY = os.path.join(BIG, 'originals', 'meshy')    # models every world shares, bought from Meshy: people, furniture, houses
MESHY_CACHE = os.path.join(BIG, 'cache', 'meshy')  # those models slimmed and set straight, kept between builds
PROPS = os.path.join(BIG, 'built', 'props')   # made by the build: the bicycle, the window pictures
