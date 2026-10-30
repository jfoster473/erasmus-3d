# Runs the full build with every printed line stamped with the seconds since the start, and a summary of
# where the time went at the end (round 26: "review what can be done to make the game build run faster").
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P builder/time_build.py > bigfiles/built/barcelona/build.log 2>&1
#
# The build itself is unchanged: this only wraps print(), exec() of the world scripts, and a few slow calls.

import builtins, os, sys, time
import bpy

T0 = time.time()
_print = builtins.print
STAGES = []          # (label, seconds)


def stamped(*a, **k):
    if k.get('file') in (None, sys.stdout):
        _print('[%6.1f]' % (time.time() - T0), *a, **k)
    else:
        _print(*a, **k)


builtins.print = stamped

# each world script the build exec()s becomes a stage
_exec = builtins.exec


_open = builtins.open
LAST_PY = ['?']


def tracking_open(f, *a, **k):
    if isinstance(f, str) and f.endswith('.py'):
        LAST_PY[0] = os.path.basename(f)
    return _open(f, *a, **k)


builtins.open = tracking_open


def timed_exec(src, g=None, l=None, *rest):
    if g is None:                       # exec(src) on its own runs in the caller's namespace
        fr = sys._getframe(1)
        g, l = fr.f_globals, fr.f_locals
    name = LAST_PY[0] if isinstance(src, str) else '?'
    if not isinstance(src, str) or len(src) < 2000:          # (small snippets: not a stage)
        return _exec(src, g, l, *rest)
    t = time.time()
    _print('[%6.1f] STAGE start: %s' % (time.time() - T0, name))
    try:
        return _exec(src, g, l, *rest)
    finally:
        STAGES.append((name, time.time() - t))
        _print('[%6.1f] STAGE done in %.1f s: %s' % (time.time() - T0, time.time() - t, name))


builtins.exec = timed_exec

# Blender's own slow calls
_calls = {}


class Timed:
    """An operator that counts its calls and time, and otherwise behaves as itself (.poll() and the rest)."""

    def __init__(self, f, label):
        self.f, self.label = f, label

    def __call__(self, *a, **k):
        t = time.time()
        try:
            return self.f(*a, **k)
        finally:
            n, s = _calls.get(self.label, (0, 0.0))
            _calls[self.label] = (n + 1, s + time.time() - t)

    def __getattr__(self, a):
        return getattr(self.f, a)


class OpsProxy:
    def __init__(self, inner, label):
        self.inner, self.label = inner, label

    def __getattr__(self, a):
        v = getattr(self.inner, a)
        if callable(v):
            return Timed(v, self.label + '.' + a)
        return v


bpy.ops.import_scene = OpsProxy(bpy.ops.import_scene, 'import_scene')
bpy.ops.export_scene = OpsProxy(bpy.ops.export_scene, 'export_scene')
bpy.ops.object = OpsProxy(bpy.ops.object, 'object')

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'build_assets.py')).read()
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': '__main__'}
try:
    _exec(compile(src, g['__file__'], 'exec'), g)
finally:
    _print('\n===== TIMINGS (total %.1f s) =====' % (time.time() - T0))
    for label, s in STAGES:
        _print('%7.1f s  %s' % (s, label))
    for label, (n, s) in sorted(_calls.items(), key=lambda kv: -kv[1][1]):
        if s > 1:
            _print('%7.1f s  %4d x  bpy.ops.%s' % (s, n, label))
