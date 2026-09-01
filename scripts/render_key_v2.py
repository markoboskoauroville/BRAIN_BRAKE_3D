"""THE BRAIN BRAKE key: a proper studio render, brass and drawn.

    Blender --background --python scripts/render_key_v2.py

Writes into renders/. Twelve stills, six brass and six drawn, the key turning.

WHY THE FIRST ATTEMPT LOOKED BAD, so it is not repeated:

    Metal renders as flat brown plastic unless it has something to reflect.
    Three small lights against a plain background give it nothing to mirror, and
    brass is almost entirely reflection. This builds a studio: a bright dome, a
    large soft key light, and two visible reflector cards. The cards are what
    make the shaft read as a round metal rod.

    It also uses Cycles rather than EEVEE. EEVEE approximates reflection and
    metal is exactly where that approximation shows.
"""
import bpy, os, math, mathutils

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ  = os.path.join(HERE, 'mesh', 'brain_break_key.obj')
if not os.path.exists(OBJ):
    OBJ = os.path.join(HERE, 'mesh', 'key.obj')
OUT  = os.path.join(HERE, 'renders')
os.makedirs(OUT, exist_ok=True)

PAPER = (1.0, 0.973, 0.898, 1.0)
TURNS = 6

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)

# ---------------------------------------------------------------- the key
if hasattr(bpy.ops.wm, 'obj_import'):
    bpy.ops.wm.obj_import(filepath=OBJ)
else:
    bpy.ops.import_scene.obj(filepath=OBJ)
key = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
key.name = 'KEY'
bpy.context.view_layer.objects.active = key
key.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
key.location = (0, 0, 0)
bpy.ops.object.shade_smooth()

# a bevel so the edges catch light. Sharp edges are the other reason metal
# looks like plastic: real objects have a highlight along every edge.
bev = key.modifiers.new('bevel', 'BEVEL')
bev.width = 0.00018
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(35)

# ---------------------------------------------------------------- materials
def principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes['Principled BSDF']

real, b = principled('KEY_REAL')
b.inputs['Base Color'].default_value = (0.74, 0.53, 0.20, 1.0)
b.inputs['Metallic'].default_value = 1.0
b.inputs['Roughness'].default_value = 0.22
for n in ('Anisotropic', 'Specular IOR Level', 'Specular'):
    if n in b.inputs:
        b.inputs[n].default_value = 0.5 if 'Specular' in n else 0.3

drawn, d = principled('KEY_DRAWN')
d.inputs['Base Color'].default_value = (0.93, 0.75, 0.30, 1.0)
d.inputs['Metallic'].default_value = 0.0
d.inputs['Roughness'].default_value = 1.0
for n in ('Specular IOR Level', 'Specular'):
    if n in d.inputs:
        d.inputs[n].default_value = 0.0

key.data.materials.clear()
key.data.materials.append(real)
key.data.materials.append(drawn)

# ---------------------------------------------------------------- the studio
w = bpy.data.worlds.new('STUDIO')
bpy.context.scene.world = w
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = PAPER
bg.inputs['Strength'].default_value = 1.6      # the dome the brass reflects

def card(name, loc, rot, size, energy):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = size
    o = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return o

# large and close, so the highlight running down the shaft is long and soft
card('KEY_LIGHT',  (0.16, -0.20,  0.22), (math.radians(52), 0, math.radians(28)), (0.45, 0.25), 140)
card('FILL',       (-0.24, -0.16, 0.04), (math.radians(84), 0, math.radians(-52)), (0.40, 0.30), 32)
card('RIM',        (0.02,  0.26,  0.16), (math.radians(-58), 0, 0), (0.35, 0.20), 70)

# ---------------------------------------------------------------- camera
cd = bpy.data.cameras.new('CAM')
cd.lens = 100                                   # long lens, no distortion on a small object
cam = bpy.data.objects.new('CAM', cd)
bpy.context.collection.objects.link(cam)
cam.location = (0.0, -0.34, 0.05)
bpy.context.scene.camera = cam
t = cam.constraints.new('TRACK_TO')
t.target = key
t.track_axis = 'TRACK_NEGATIVE_Z'
t.up_axis = 'UP_Y'

# ---------------------------------------------------------------- render
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
try:
    sc.cycles.device = 'GPU'
except Exception:
    pass
sc.cycles.samples = 128
sc.cycles.use_denoising = True
sc.render.resolution_x = 2752
sc.render.resolution_y = 1536
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'
try:
    sc.view_settings.view_transform = 'AgX'     # keeps the brass highlight from clipping
except Exception:
    pass
sc.view_settings.look = 'None'

made = []
for slot, label in ((0, 'REAL'), (1, 'DRAWN')):
    for p in key.data.polygons:
        p.material_index = slot
    for i in range(TURNS):
        key.rotation_euler = (math.radians(12 + i*3), 0, math.radians(i * (360.0 / TURNS)))
        name = 'KEY_%s_%02d.png' % (label, i + 1)
        sc.render.filepath = os.path.join(OUT, name)
        bpy.ops.render.render(write_still=True)
        made.append(name)

print('')
print('=' * 62)
print('%d images in %s' % (len(made), OUT))
print('LOOK AT ONE BEFORE REPORTING SUCCESS. A render that writes files and')
print('produces black images is the classic failure and the count will not')
print('tell you.')
print('=' * 62)
