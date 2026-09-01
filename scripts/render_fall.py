"""THE BRAIN BRAKE key: the fall. Section 28 of the film MEMORY made into frames.

    Blender --background --python scripts/render_fall.py

Six and a half seconds at 25 fps, 162 frames, into renders/FALL/ as a PNG
sequence with alpha. Never committed: renders/ is ignored and this regenerates.

Three things change together and none of them alone: it turns, it grows, and it
crosses from KEY_DRAWN to KEY_REAL. The growth is not a scale animation. The
key approaches the camera at constant speed, and perspective does the growing:
a twelfth of the frame width when released, a tenth past the cloud, an eighth
past the house, a sixth past the avenue, a third nearly landed, most of the
frame at the hand. Those stage sizes from section 28 sit on the curve of a
constant velocity approach almost exactly, which is the point: it is the same
object the whole way down, it simply gets nearer.

The background is transparent. The places it falls past, the cloud bank, the
house of the body, the avenue, are the film's own frames and are composited
behind it later. The paper dome still lights the key and lives in its
reflections.
"""
import bpy, os, math

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ  = os.path.join(HERE, 'mesh', 'brain_break_key.obj')
OUT  = os.path.join(HERE, 'renders', 'FALL')
os.makedirs(OUT, exist_ok=True)

# 255,248,229 display sRGB converted to linear, so the render lands on it exactly
PAPER   = (1.0, 0.9387, 0.7836, 1.0)
FPS     = 25
FRAMES  = 162            # 6.48 seconds
KEY_LEN = 0.030          # the key is about 26 mm plus the bow

# camera distances for the stage sizes: fraction = KEY_LEN / (0.36 * d) with a
# 100 mm lens on the default 36 mm sensor. 1/12 of the frame -> 1.0 m,
# 0.8 of the frame -> 0.104 m. Linear in between: constant approach speed.
D_START = KEY_LEN * 12 / 0.36
D_END   = KEY_LEN / (0.36 * 0.8)

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

bev = key.modifiers.new('bevel', 'BEVEL')
bev.width = 0.00018
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(35)

# ------------------------------------------------- one material, two shaders
# a Mix Shader crossfades pencil to brass. No single frame is the moment.
m = bpy.data.materials.new('KEY_CROSSING')
m.use_nodes = True
nt = m.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out   = nt.nodes.new('ShaderNodeOutputMaterial')
mix   = nt.nodes.new('ShaderNodeMixShader')
drawn = nt.nodes.new('ShaderNodeBsdfPrincipled')
real  = nt.nodes.new('ShaderNodeBsdfPrincipled')

drawn.inputs['Base Color'].default_value = (0.86, 0.66, 0.22, 1.0)
drawn.inputs['Metallic'].default_value = 0.0
drawn.inputs['Roughness'].default_value = 1.0
for n in ('Specular IOR Level', 'Specular'):
    if n in drawn.inputs:
        drawn.inputs[n].default_value = 0.0

real.inputs['Base Color'].default_value = (0.74, 0.53, 0.20, 1.0)
real.inputs['Metallic'].default_value = 1.0
real.inputs['Roughness'].default_value = 0.22

nt.links.new(drawn.outputs['BSDF'], mix.inputs[1])   # fac 0: fully pencil
nt.links.new(real.outputs['BSDF'],  mix.inputs[2])   # fac 1: fully brass
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])

key.data.materials.clear()
key.data.materials.append(m)

fac = mix.inputs['Fac']
fac.default_value = 0.0
fac.keyframe_insert('default_value', frame=1)
fac.default_value = 1.0
fac.keyframe_insert('default_value', frame=FRAMES)   # bezier ease at both ends

# ---------------------------------------------------------------- the studio
w = bpy.data.worlds.new('STUDIO')
bpy.context.scene.world = w
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = PAPER
bg.inputs['Strength'].default_value = 1.0

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

card('KEY_LIGHT',  (0.16, -0.20,  0.22), (math.radians(52), 0, math.radians(28)), (0.45, 0.25), 3)
card('FILL',       (-0.24, -0.16, 0.04), (math.radians(84), 0, math.radians(-52)), (0.40, 0.30), 0.75)
card('RIM',        (0.02,  0.26,  0.16), (math.radians(-58), 0, 0), (0.35, 0.20), 1.5)

# ---------------------------------------------------------------- camera
cd = bpy.data.cameras.new('CAM')
cd.lens = 100
cam = bpy.data.objects.new('CAM', cd)
bpy.context.collection.objects.link(cam)
cam.location = (0.0, -D_START, 0.0)
bpy.context.scene.camera = cam
t = cam.constraints.new('TRACK_TO')
t.target = key
t.track_axis = 'TRACK_NEGATIVE_Z'
t.up_axis = 'UP_Y'

# --------------------------------------------- the approach and the turning
# the key comes to the camera, linearly: constant speed, hyperbolic growth,
# exactly the section 28 stage sizes. LINEAR interpolation so it never jumps.
key.location = (0, 0, 0)
key.keyframe_insert('location', frame=1)
key.location = (0, -(D_START - D_END), 0)
key.keyframe_insert('location', frame=FRAMES)

# two and a half slow turns, never twice at the same angle, with a lazy tumble
key.rotation_euler = (math.radians(8), 0, 0)
key.keyframe_insert('rotation_euler', frame=1)
key.rotation_euler = (math.radians(38), math.radians(25), math.radians(900))
key.keyframe_insert('rotation_euler', frame=FRAMES)

for fc in key.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'

# ---------------------------------------------------------------- render
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
try:
    sc.cycles.device = 'GPU'
except Exception:
    pass
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.fps = FPS
sc.frame_start = 1
sc.frame_end = FRAMES
sc.render.resolution_x = 2752
sc.render.resolution_y = 1536
sc.render.film_transparent = True                 # the film's places go behind
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
try:
    sc.view_settings.view_transform = 'Standard'  # the paper colour is the film
except Exception:
    pass
sc.view_settings.look = 'None'
sc.render.filepath = os.path.join(OUT, 'FALL_')

bpy.ops.render.render(animation=True)

print('')
print('=' * 62)
print('%d frames in %s' % (FRAMES, OUT))
print('LOOK AT THE FIRST, A MIDDLE AND THE LAST FRAME BEFORE REPORTING.')
print('=' * 62)
