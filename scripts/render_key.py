"""THE BRAIN BRAKE key: build it, light it, and render the frames for the site.

HOW TO USE THIS
    Headless, no window needed:

        /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_key.py

    Run it from the repository root. It reads mesh/brain_break_key.obj and
    writes twelve images into renders/, which is not committed.

It does everything: imports the mesh, makes both materials, adds a camera and
lights, sets the background to the film's paper colour, and renders the key
turning, once in brass and once drawn.

Nothing needs clicking in the 3D view. Nothing needs setting up.
"""
import bpy, os, math, mathutils

HERE = os.path.dirname(os.path.abspath(bpy.data.filepath or __file__)) or os.getcwd()
try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    pass
ROOT = os.path.dirname(HERE)
OBJ = os.path.join(ROOT, 'mesh', 'brain_break_key.obj')
OUT = os.path.join(ROOT, 'renders')
os.makedirs(OUT, exist_ok=True)

PAPER = (1.0, 0.973, 0.898, 1.0)          # the film's cream, measured off a frame
TURNS = 6                                  # frames per material

# ----------------------------------------------------------------- clean slate
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ----------------------------------------------------------------- the key
if hasattr(bpy.ops.wm, 'obj_import'):
    bpy.ops.wm.obj_import(filepath=OBJ)
else:
    bpy.ops.import_scene.obj(filepath=OBJ)
key = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
key.name = 'BRAIN_BRAKE_KEY'
bpy.context.view_layer.objects.active = key
key.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
key.location = (0, 0, 0)
bpy.ops.object.shade_smooth()

# ----------------------------------------------------------------- materials
def make(name, colour, metallic, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = colour
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    return m

real  = make('KEY_REAL',  (0.72, 0.50, 0.14, 1.0), 1.0, 0.25)
drawn = make('KEY_DRAWN', (0.93, 0.76, 0.30, 1.0), 0.0, 0.85)
key.data.materials.clear()
key.data.materials.append(real)
key.data.materials.append(drawn)

# ----------------------------------------------------------------- world
w = bpy.data.worlds.new('PAPER') if not bpy.data.worlds else bpy.data.worlds[0]
bpy.context.scene.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = PAPER
# exactly 1.0 with the Standard view transform, so the background pixel IS the
# paper colour rather than clipping to pure white
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

# ----------------------------------------------------------------- lights
def light(name, kind, loc, energy, size=0.35):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    if kind == 'AREA':
        d.size = size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (mathutils.Vector((0,0,0)) - mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler()
    return o

light('KEY_LIGHT',  'AREA', ( 0.22,  -0.18,  0.26), 4)
light('FILL_LIGHT', 'AREA', (-0.26,  -0.14,  0.06), 1)
light('RIM_LIGHT',  'AREA', ( 0.02,   0.28,  0.14), 2)

# ----------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new('CAM')
cam_data.lens = 85
cam = bpy.data.objects.new('CAM', cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.0, -0.30, 0.02)
cam.rotation_euler = (math.radians(84), 0, 0)
bpy.context.scene.camera = cam

t = cam.constraints.new('TRACK_TO')
t.target = key
t.track_axis = 'TRACK_NEGATIVE_Z'
t.up_axis = 'UP_Y'

# ----------------------------------------------------------------- render
sc = bpy.context.scene
for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
    try:
        sc.render.engine = engine
        break
    except TypeError:
        continue
print('render engine: %s' % sc.render.engine)
try:
    sc.eevee.use_raytracing = True
except Exception:
    pass
# Standard view transform, not AgX: AgX turns the paper cream grey and washes
# the brass toward white. The site needs the film's actual paper colour.
try:
    sc.view_settings.view_transform = 'Standard'
except Exception:
    pass
sc.render.resolution_x = 2752
sc.render.resolution_y = 1536
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'

made = []
for slot, label in ((0, 'REAL'), (1, 'DRAWN')):
    for p in key.data.polygons:
        p.material_index = slot
    for i in range(TURNS):
        key.rotation_euler = (math.radians(8 + i*4), 0, math.radians(i * (360.0/TURNS)))
        name = 'KEY_3D_%s_%02d.png' % (label, i + 1)
        sc.render.filepath = os.path.join(OUT, name)
        bpy.ops.render.render(write_still=True)
        made.append(name)

print('')
print('=' * 60)
print('DONE. %d images written to:' % len(made))
print('   %s' % OUT)
for n in made:
    print('   %s' % n)
print('=' * 60)
