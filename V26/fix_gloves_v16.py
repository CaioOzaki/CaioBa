"""Repair Cloudcourt glove anatomy without changing tracked hands or hitboxes.

The original rig's open thumb endpoints in hand-root space are approximately
L=(+.023,+.092,+.129), R=(-.023,+.092,+.129).  Thus both thumbs face local
+Y and the two meshes are mirror images across X.  The first v16 builder used
one mesh with the thumb at -Y for both hands.  New geometry follows the rig's
anatomical frame; the controller/physics transforms are deliberately untouched.
"""
from pathlib import Path
import ast
import copy
import math
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import numpy as np


def _model_class():
    # Reuse the project's own mesh authoring, without its atlas-write side effects.
    tree = ast.parse((R / 'create_puloviva_characters.py').read_text(encoding='utf-8'))
    tree.body = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                 and node.name in {'uv_palette', 'v3', 'aabb', 'Model'}]
    scope = dict(np=np, copy=copy, struct=struct, math=math)
    exec(compile(tree, 'cloudcourt_mesh_authoring', 'exec'), scope)
    return scope['Model']


def glove_model(state, side):
    """Return a rounded left/right glove in the existing hand-root frame."""
    assert state in ('Open', 'Closed') and side in ('L', 'R')
    m = _model_class()()
    m.softbox((0, 0, .045), (.028, .060, .067), 0, 0)
    m.softbox((0, 0, -.025), (.032, .066, .023), 0, 1)
    if state == 'Open':
        for j, y in enumerate([-.046, -.015, .016, .047]):
            m.limb((0, y, .085), (0, y, .17 + (1 - abs(j - 1.5) / 2) * .035),
                   .016, .018, 0, 0)
        # Local +Y is the thumb edge, from the original rig landmarks above.
        m.limb((.002, .045, .025), (.023, .10, .09), .023, .024, 0, 0)
    else:
        m.softbox((0, 0, .105), (.033, .059, .036), 0, 0)
        m.softbox((.018, .048, .069), (.023, .023, .042), 0, 0)
    if side == 'R':
        # Bake the mirror into the mesh. Negative transform scale would reverse
        # front faces and also leak an inverted frame to future visual children.
        m.v = [[-x, y, z] for x, y, z in m.v]
        m.n = [[-x, y, z] for x, y, z in m.n]
        m.tri = [(a, c, b) for a, b, c in m.tri]
    return m


def hierarchy(file):
    objects = {o.path_id: o.read_typetree() for o in file.objects.values()
               if o.type.name == 'GameObject'}
    transforms = {o.path_id: o.read_typetree() for o in file.objects.values()
                  if o.type.name in ('Transform', 'RectTransform')}
    def path(i):
        t = transforms[i]
        parent = t['m_Father']['m_PathID']
        return (path(parent) + '/' if parent in transforms else '') + objects[t['m_GameObject']['m_PathID']]['m_Name']
    return objects, transforms, {path(i): i for i in transforms}


def repair_hand_assets(resources):
    """Mutate only four glove MeshFilters and their visual mesh objects.

    Caller owns file saving.  Safe to apply after build_cloudcourt_v16.py, or to
    an already-built resources.assets. Reapplication reuses its own meshes.
    """
    objects, transforms, paths = hierarchy(resources)
    variants = {}
    for path, transform_id in paths.items():
        for side in ('L', 'R'):
            for state in ('Open', 'Closed'):
                if not path.endswith(f'Hand Root {side}/{state}/Cloudcourt {state} Glove'):
                    continue
                go = objects[transforms[transform_id]['m_GameObject']['m_PathID']]
                filters = [resources.objects[c['component']['m_PathID']] for c in go['m_Component']
                           if resources.objects[c['component']['m_PathID']].type.name == 'MeshFilter']
                assert len(filters) == 1, path
                variants[side, state] = filters[0]
    assert set(variants) == {(s, p) for s in ('L', 'R') for p in ('Open', 'Closed')}, variants
    used, changed, records = set(), set(), []
    for state in ('Open', 'Closed'):
        for side in ('L', 'R'):
            mesh_filter = variants[side, state]
            data = mesh_filter.read_typetree()
            assert data['m_Mesh']['m_FileID'] == 0
            mesh_id = data['m_Mesh']['m_PathID']
            source = resources.objects[mesh_id]
            if mesh_id in used:
                obj = copy.copy(source)
                mesh_id = max(resources.objects) + 1
                obj.path_id = mesh_id
                obj.assets_file = resources
                resources.objects[mesh_id] = obj
                data['m_Mesh']['m_PathID'] = mesh_id
                mesh_filter.save_typetree(data)
                changed.add(mesh_filter.path_id)
            else:
                obj = source
            used.add(mesh_id)
            model = glove_model(state, side)
            obj.save_typetree(model.serialize(source.read_typetree(), f'Cloudcourt {side} {state} Glove', False))
            changed.add(mesh_id)
            records.append(dict(side=side, state=state, mesh_id=mesh_id, filter_id=mesh_filter.path_id))
    return {'variants': records, 'changed_object_ids': sorted(changed),
            'thumb_edge': '+Y', 'mirror_axis': 'X',
            'tracking_roots_and_hitboxes_unchanged': True}


if __name__ == '__main__':
    import argparse
    import json
    import UnityPy
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    assert args.input.resolve() != args.output.resolve(), 'Use a separate output file for this repair.'
    file = UnityPy.load(str(args.input)).file
    report = repair_hand_assets(file)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(file.save())
    print(json.dumps(report, indent=2))
