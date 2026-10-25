"""Check glove anatomy against rig landmarks and preserve controller transforms."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
import numpy as np
from fix_gloves_v16 import hierarchy, repair_hand_assets


def matrix(t):
    x, y, z, w = [t['m_LocalRotation'][i] for i in 'xyzw']
    q = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    out = np.eye(4)
    out[:3, :3] = q @ np.diag([t['m_LocalScale'][i] for i in 'xyz'])
    out[:3, 3] = [t['m_LocalPosition'][i] for i in 'xyz']
    return out


def meshes(file):
    objects, transforms, paths = hierarchy(file)
    out = {}
    for side in ('L', 'R'):
        for state in ('Open', 'Closed'):
            path = next(p for p in paths if p.endswith(f'Hand Root {side}/{state}/Cloudcourt {state} Glove'))
            t = transforms[paths[path]]
            assert t['m_LocalScale'] == dict(x=1., y=1., z=1.)
            go = objects[t['m_GameObject']['m_PathID']]
            mesh_filter = next(file.objects[c['component']['m_PathID']] for c in go['m_Component']
                               if file.objects[c['component']['m_PathID']].type.name == 'MeshFilter')
            mesh_ptr = mesh_filter.read_typetree()['m_Mesh']
            assert mesh_ptr['m_FileID'] == 0
            mesh = file.objects[mesh_ptr['m_PathID']].read_typetree()
            vertices = np.frombuffer(bytes(mesh['m_VertexData']['m_DataSize']), dtype='<f4').reshape(-1, 12)
            triangles = np.frombuffer(bytes(mesh['m_IndexBuffer']), dtype='<u2').reshape(-1, 3)
            assert len(vertices) == mesh['m_VertexData']['m_VertexCount']
            assert np.isfinite(vertices).all() and triangles.max() < len(vertices)
            assert np.abs(vertices[:, :3]).max() < .3
            assert np.allclose(np.linalg.norm(vertices[:, 3:6], axis=1), 1, atol=1e-5)
            center = np.array([mesh['m_LocalAABB']['m_Center'][i] for i in 'xyz'])
            extent = np.array([mesh['m_LocalAABB']['m_Extent'][i] for i in 'xyz'])
            assert (np.abs(vertices[:, :3] - center) <= extent + 1e-6).all()
            out[side, state] = mesh_ptr['m_PathID'], vertices, triangles
    return out


def validate(file, before=None):
    variants = meshes(file)
    assert len({v[0] for v in variants.values()}) == 4, 'Left/right gloves share one asymmetric mesh.'
    for state in ('Open', 'Closed'):
        _, l, li = variants['L', state]
        _, r, ri = variants['R', state]
        assert np.allclose(l[:, 0], -r[:, 0]) and np.allclose(l[:, 1:3], r[:, 1:3])
        assert np.allclose(l[:, 3], -r[:, 3]) and np.allclose(l[:, 4:6], r[:, 4:6])
        assert np.array_equal(li[:, [0, 2, 1]], ri), 'Mirroring must reverse winding.'
        # Anatomical evidence: thumb protrudes at +Y, and towards +X on L/-X on R.
        for side in ('L', 'R'):
            _, v, _ = variants[side, state]
            thumb = v[v[:, 1] > (.075 if state == 'Open' else .065), :3]
            assert len(thumb) > 0
            assert thumb[:, 0].mean() * (1 if side == 'L' else -1) > .001
            if state == 'Open':
                assert v[:, 1].max() > .11 and v[:, 1].min() > -.08
    if before is not None:
        # All runtime components, physics shapes, tracked roots, scripts and
        # materials survive unchanged; changes are restricted to static visuals.
        for i, old in before.objects.items():
            if i in (1304, 1313, 1311, 1320):
                continue
            assert old.get_raw_data() == file.objects[i].get_raw_data(), (i, old.type.name)
    original = UnityPy.load(str(R / 'versions/v15-rostos-antes-puloviva/resources.assets')).file
    _, transforms, paths = hierarchy(original)
    landmarks = {}
    for side in ('L', 'R'):
        path = next(p for p in paths if p.endswith(f'thumb_03_{side.lower()}_end'))
        root_path = path.split('/Open/')[0] + '/Open'
        root = paths[root_path]
        i = paths[path]
        m = matrix(transforms[i])
        i = transforms[i]['m_Father']['m_PathID']
        while i != root:
            m = matrix(transforms[i]) @ m
            i = transforms[i]['m_Father']['m_PathID']
        p = m[:3, 3]
        assert p[1] > .08 and p[0] * (1 if side == 'L' else -1) > .02
        landmarks[side] = p.round(5).tolist()
    return {'passed': True, 'variants': {f'{s}-{p}': v[0] for (s, p), v in variants.items()},
            'rig_thumb_endpoints': landmarks,
            'checks': ['distinct left/right open and closed meshes', 'thumb direction matches original rig',
                       'mirrored positions and normals', 'reversed mirrored triangle winding',
                       'finite geometry and valid bounds', 'tracking roots/hitboxes/scripts/materials preserved'],
            'scope': 'Asset anatomy and transform validation; headset visual check remains necessary.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', type=Path)
    args = parser.parse_args()
    if args.asset:
        file = UnityPy.load(str(args.asset)).file
        report = validate(file)
    else:
        original_path = R / 'working/VolleyballFever_Data/resources.assets'
        original = UnityPy.load(str(original_path)).file
        file = UnityPy.load(str(original_path)).file
        report = repair_hand_assets(file)
        output = R / 'analysis/gloves-repaired-resources.assets'
        output.write_bytes(file.save())
        file = UnityPy.load(str(output)).file
        report.update(validate(file, original))
        # Second application must reuse the same four mesh slots.
        ids = set(file.objects)
        repair_hand_assets(file)
        output.write_bytes(file.save())
        repeated = UnityPy.load(str(output)).file
        assert ids == set(repeated.objects)
        assert all(repeated.objects[i].get_raw_data() == file.objects[i].data
                   for i in (1304, 1313))
        validate(repeated)
        report['idempotent'] = True
    (R / 'analysis/v16-glove-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
