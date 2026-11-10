def objs_snapshot():
    return set(bpy.data.objects)

def img_node_mat(name, paths, strength=1.0):
    """Emissive image material; with two paths, a keyable mix between them (input 'Fac')."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; l = nt.links
    n.remove(n['Principled BSDF'])
    em = n.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength
    imgs = []
    for p in paths:
        t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p); t.extension = 'CLIP'; imgs.append(t)
    if len(imgs) == 1:
        l.new(imgs[0].outputs['Color'], em.inputs['Color']); mix = None
    else:
        mix = n.new('ShaderNodeMixRGB'); mix.inputs['Fac'].default_value = 0
        l.new(imgs[0].outputs['Color'], mix.inputs['Color1']); l.new(imgs[1].outputs['Color'], mix.inputs['Color2'])
        l.new(mix.outputs['Color'], em.inputs['Color'])
    l.new(em.outputs[0], n['Material Output'].inputs['Surface'])
    return m, mix, em

def brick_mat(name, c1, c2, mortar, scale=6, w=0.5, h=0.25, offset=0.5, rough=0.8, vertical=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; l = nt.links
    b = n['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    tc = n.new('ShaderNodeTexCoord'); bk = n.new('ShaderNodeTexBrick')
    bk.inputs['Color1'].default_value = (*c1, 1); bk.inputs['Color2'].default_value = (*c2, 1)
    bk.inputs['Mortar'].default_value = (*mortar, 1); bk.inputs['Scale'].default_value = scale
    bk.inputs['Brick Width'].default_value = w; bk.inputs['Row Height'].default_value = h
    bk.inputs['Mortar Size'].default_value = 0.015; bk.offset = offset
    mp = n.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (D(90) if vertical else 0, 0, 0)
    sep = n.new('ShaderNodeSeparateXYZ'); com = n.new('ShaderNodeCombineXYZ')
    l.new(tc.outputs['Object'], sep.inputs[0])
    if vertical:   # map wall faces: x -> u, z -> v (plus y so side walls also tile)
        add = n.new('ShaderNodeMath'); add.inputs[1].default_value = 0
        l.new(sep.outputs['X'], add.inputs[0]); 
        add2 = n.new('ShaderNodeMath'); l.new(add.outputs[0], add2.inputs[0]); l.new(sep.outputs['Y'], add2.inputs[1])
        l.new(add2.outputs[0], com.inputs['X']); l.new(sep.outputs['Z'], com.inputs['Y'])
    else:
        l.new(sep.outputs['X'], com.inputs['X']); l.new(sep.outputs['Y'], com.inputs['Y'])
    l.new(com.outputs[0], bk.inputs['Vector']); l.new(bk.outputs['Color'], b.inputs['Base Color'])
    return m

def text(body, size, loc, m, rot=(D(90), 0, 0), extrude=0.004, parent=None):
    cu = bpy.data.curves.new('txt', 'FONT'); cu.body = body; cu.size = size
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = extrude
    o = link(bpy.data.objects.new('txt', cu)); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def cyl(name, r, depth, loc, m, rot=(0, 0, 0), verts=48, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    return finish(o, m, parent)


def make_eye_target(C, name):
    return empty(name, (0, -C['r'] - 0.01, C['ez']), C['root'])

def brows_low(C, amount=0.04):
    for i, bp in enumerate(C['brows']):
        sx = -1 if i == 0 else 1
        bp.location.z -= amount; bp.rotation_euler = (0, sx * D(14), 0)

def set_visible(group, vis):
    for o in group:
        o.hide_render = not vis

def world(color, strength):
    w = scene.world or bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (*color, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = strength

def cam_align(obj, axis_vec_local, up_local, dist, offset_up=0.0):
    """Return (location, euler) for a camera looking straight at obj along its local axis."""
    from mathutils import Matrix
    bpy.context.view_layer.update()
    Mw = obj.matrix_world.to_3x3().normalized(); p = obj.matrix_world.translation.copy()
    nrm = (Mw @ Vector(axis_vec_local)).normalized(); up = (Mw @ Vector(up_local)).normalized()
    zc = nrm; yc = (up - zc * up.dot(zc)).normalized(); xc = yc.cross(zc)
    return p + nrm * dist + up * offset_up, Matrix((xc, yc, zc)).transposed().to_euler(), up
