"""THE BRAIN BRAKE key: light it properly and render.

    blender --background --python scripts/render_key_v2.py

Writes into renders/. Twelve stills: six brass, six drawn.

WHAT WAS WRONG BEFORE, so it is not repeated. The key is 26 mm across and the
lights were sized and placed in metres, so relative to the object they were
enormous and infinitely far away, which gives flat even illumination and no
form. Brass also had nothing to reflect: a metal with a plain colour world
around it is just a brown surface, because what makes metal look like metal is
what it reflects, not its own colour.

So: an environment that has something in it, lights sized to the object, a
ground plane to catch a shadow, and enough subdivision that the round parts are
round.
"""
import bpy, os, math, mathutils

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ = os.path.join(HERE, 'mesh', 'brain_break_key.obj')
if not os.path.exists(OBJ):
    OBJ = os.path.join(HERE, 'mesh', 'key.obj')
OUT = os.path.join(HERE, 'renders')
os.makedirs(OUT, exist_ok=True)

PAPER = (1.0, 0.973, 0.898, 1.0)
TURNS = 6

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ------------------------------------------------------------------ the key
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

# smooth shading with an angle, so the flat faces of the bit stay crisp while
# the shaft and the head read as round
bpy.ops.object.shade_smooth()
try:
    bpy.ops.object.modifier_add(type='BEVEL')
    b = key.modifiers[-1]
    b.width = 0.00018          # a fifth of a millimetre, so edges catch light
    b.segments = 2
    b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(35)
except Exception as e:
    print('bevel skipped:', e)

# ------------------------------------------------------------------ materials
def principled(name, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    for k, v in kw.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return m

# brass: metal is defined by what it reflects, so roughness does the work
real = principled('KEY_REAL',
                  **{'Base Color': (0.78, 0.56, 0.20, 1.0),
                     'Metallic': 1.0,
                     'Roughness': 0.22})
# the drawn key: no metal, no specular, flat as paper
drawn = principled('KEY_DRAWN',
                   **{'Base Color': (0.93, 0.74, 0.28, 1.0),
                      'Metallic': 0.0,
                      'Roughness': 0.95})
try:
    drawn.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.0
except Exception:
    pass

key.data.materials.clear()
key.data.materials.append(real)
key.data.materials.append(drawn)

# ------------------------------------------------------------------ world
w = bpy.data.worlds.new('W')
bpy.context.scene.world = w
w.use_nodes = True
nt = w.node_tree
bg = nt.nodes['Background']
# a gradient rather than a flat colour, so the brass has something to reflect
grad = nt.nodes.new('ShaderNodeTexGradient')
grad.gradient_type = 'EASING'
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.72, 0.68, 0.60, 1.0)
ramp.color_ramp.elements[1].color = (1.0, 0.98, 0.93, 1.0)
tex = nt.nodes.new('ShaderNodeTexCoord')
mp = nt.nodes.new('ShaderNodeMapping')
mp.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
nt.links.new(tex.outputs['Generated'], mp.inputs['Vector'])
nt.links.new(mp.outputs['Vector'], grad.inputs['Vector'])
nt.links.new(grad.outputs['Color'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 1.6

# ------------------------------------------------------------------ ground
bpy.ops.mesh.primitive_plane_add(size=1.2, location=(0, 0, -0.02))
floor = bpy.context.object
floor.name = 'PAPER'
floor.data.materials.append(principled('PAPER',
                                       **{'Base Color': PAPER,
                                          'Roughness': 0.95,
                                          'Metallic': 0.0}))

# ------------------------------------------------------------------ lights
# sized against a 26 mm object, not against a room
def area(name, loc, energy, size, rot_to=(0, 0, 0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.size = size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    v = mathutils.Vector(rot_to) - mathutils.Vector(loc)
    o.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    return o

area('KEY_LIGHT',  (0.09, -0.07,  0.10), 22, 0.11)
area('FILL',       (-0.11, -0.05, 0.03),  5, 0.16)
area('RIM',        (0.01,  0.10,  0.06), 12, 0.07)

# ------------------------------------------------------------------ camera
cd = bpy.data.cameras.new('CAM')
cd.lens = 100                       # long lens, so the key does not distort
cam = bpy.data.objects.new('CAM', cd)
bpy.context.collection.objects.link(cam)
cam.location = (0.0, -0.24, 0.05)
bpy.context.scene.camera = cam
t = cam.constraints.new('TRACK_TO')
t.target = key
t.track_axis = 'TRACK_NEGATIVE_Z'
t.up_axis = 'UP_Y'

# ------------------------------------------------------------------ render
sc = bpy.context.scene
sc.render.engine = 'CYCLES'          # metal wants ray tracing
try:
    sc.cycles.samples = 128
    sc.cycles.use_denoising = True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    sc.cycles.device = 'GPU'
except Exception as e:
    print('gpu not set, running on cpu:', e)

sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.look = 'AgX - Medium High Contrast' if hasattr(sc.view_settings, 'look') else 'None'

made = []
for slot, label in ((0, 'REAL'), (1, 'DRAWN')):
    for p in key.data.polygons:
        p.material_index = slot
    for i in range(TURNS):
        key.rotation_euler = (math.radians(12 + i*3), 0, math.radians(i * (360.0/TURNS)))
        n = 'KEY_%s_%02d.png' % (label, i+1)
        sc.render.filepath = os.path.join(OUT, n)
        bpy.ops.render.render(write_still=True)
        made.append(n)
        print('  wrote', n)

print('\nDONE. %d images in %s' % (len(made), OUT))
