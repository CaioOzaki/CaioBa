"""Read-only final v20 audit against the v19 backup and narrow asset builders.

Reconstructs the six allowed upgrades in memory, using existing artwork only.
Writes this audit report and an isolated expected-bot binding report; never
writes working assets, source artwork, fixtures, the installed game or GitHub.
"""
from pathlib import Path
from collections import Counter
from unittest.mock import patch
import hashlib
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import numpy as np
import UnityPy
from PIL import Image
import build_bots_v20 as bots
from build_customization_fix_v20 import apply_customization_fix, mip_report
from build_scene_v20 import build_scene_assets, SETTINGS_ROWS
from build_landing_v20 import add_landing_marks
from fix_gloves_v16 import hierarchy
from test_bots_assets_v20 import validate as validate_bots

BASE = R / 'versions/cloudcourt-v19-antes-v20'
WORK = R / 'working/VolleyballFever_Data'
CHANGED = ['resources.assets', 'sharedassets0.assets', 'level0', 'level1', 'level2', 'level3']
DATA = CHANGED + ['globalgamemanagers.assets', 'sharedassets1.assets',
    'sharedassets2.assets', 'sharedassets3.assets', 'sharedassets4.assets',
    'resources.resource', 'sharedassets0.resource', 'sharedassets1.resource',
    'sharedassets2.resource', 'sharedassets4.resource']
REPORT = R / 'analysis/v20-final-assets-audit.json'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def asset(path):
    return UnityPy.load(str(path)).file


def original_art_snapshot():
    return {str(p.relative_to(R)): sha(p) for directory in
        [R/'assets/bots-v20', R/'assets/customization-v19']
        for p in directory.rglob('*') if p.is_file()}


def expected_upgrades():
    """No PNG authoring or working-file save; serialize expected data in memory."""
    files = {name: asset(BASE/name) for name in CHANGED}
    scope = bots.authoring()
    models = [bots.character(scope, i)[0] for i in range(9)]
    atlases = [Image.open(bots.A/f'bot-{i+1:02d}-atlas.png').convert('RGB') for i in range(9)]
    catalog = json.loads((bots.A/'catalog.json').read_text(encoding='utf-8'))
    isolated = R/'analysis/v20-expected-bot-report'
    isolated.mkdir(parents=True, exist_ok=True)
    # The helper emits bindings. Redirect only that report, keeping art intact.
    with patch.object(bots, 'A', isolated):
        bot_report = bots.apply_bots_assets_v20(files['sharedassets0.assets'],
                                               (scope, models, atlases, catalog))
    customization = apply_customization_fix(files['resources.assets'])
    scenes = build_scene_assets(files)
    landing = {name: add_landing_marks(files[name], files['resources.assets'])
               for name in ('level1', 'level2', 'level3')}
    result = {name: file.save() for name, file in files.items()}
    return result, bot_report, customization, scenes, landing


def check_markers(scene, oldids):
    added = set(scene.objects)-oldids
    counts = Counter(scene.objects[i].type.name for i in added)
    assert counts == Counter(GameObject=3, Transform=3, Mesh=1, Texture2D=2,
                             Material=2, MeshRenderer=2, MeshFilter=2), counts
    gs, ts, paths = hierarchy(scene)
    root = paths['CC_LandingMarks']
    root_t = ts[root]
    root_g = gs[root_t['m_GameObject']['m_PathID']]
    assert root_g['m_IsActive'] and len(root_g['m_Component']) == 1
    assert root_t['m_Father']['m_PathID'] == 0
    assert root_t['m_LocalPosition'] == dict(x=0., y=0., z=0.)
    assert len(root_t['m_Children']) == 2
    mesh_ids = set()
    rows = []
    for name, rgba in [('In', (34,222,96,255)), ('Out', (248,55,64,255))]:
        transform = ts[paths['CC_LandingMarks/'+name]]
        go = gs[transform['m_GameObject']['m_PathID']]
        assert not go['m_IsActive'] and transform['m_Father']['m_PathID'] == root
        assert abs(transform['m_LocalPosition']['y']-.014) < 1e-7
        components = [scene.objects[c['component']['m_PathID']] for c in go['m_Component']]
        assert Counter(o.type.name for o in components) == Counter(Transform=1, MeshRenderer=1, MeshFilter=1)
        renderer = next(o for o in components if o.type.name == 'MeshRenderer').read_typetree()
        assert renderer['m_Enabled'] and not renderer['m_CastShadows'] and not renderer['m_ReceiveShadows']
        assert len(renderer['m_Materials']) == 1 and renderer['m_Materials'][0]['m_FileID'] == 0
        material = scene.objects[renderer['m_Materials'][0]['m_PathID']].read_typetree()
        shader = material['m_Shader']
        assert shader['m_PathID'] == 74
        assert scene.externals[shader['m_FileID']-1].path.replace('\\','/').rsplit('/',1)[-1] == 'resources.assets'
        texture_ref = dict(material['m_SavedProperties']['m_TexEnvs'])['_MainTex']['m_Texture']
        assert texture_ref['m_FileID'] == 0
        texture = scene.objects[texture_ref['m_PathID']].read()
        assert texture.m_Width == texture.m_Height == 4 and texture.m_TextureFormat == 4
        assert texture.image.convert('RGBA').getextrema() == tuple((v,v) for v in rgba)
        mf = next(o for o in components if o.type.name == 'MeshFilter').read_typetree()
        assert mf['m_Mesh']['m_FileID'] == 0
        mesh_ids.add(mf['m_Mesh']['m_PathID'])
        rows.append(dict(name=name, initially_active=False, rgba=rgba))
    assert len(mesh_ids) == 1
    mesh = scene.objects[mesh_ids.pop()].read_typetree()
    vd = mesh['m_VertexData']; count = vd['m_VertexCount']; raw = bytes(vd['m_DataSize'])
    assert count == 98
    stride = len(raw)//count
    pos = np.ndarray((count,3), dtype='<f4', buffer=raw,
                     offset=vd['m_Channels'][0]['offset'], strides=(stride,4))
    assert np.allclose(pos[:,1], 0)
    assert np.allclose(np.linalg.norm(pos[:,[0,2]],axis=1), [.22,.29]*49, atol=1e-6)
    triangles = np.frombuffer(bytes(mesh['m_IndexBuffer']), '<u2').reshape(-1,3)
    assert len(triangles) == 96 and triangles.max() < count
    return dict(added_objects=len(added), object_types=dict(counts), markers=rows,
                vertices=count, triangles=len(triangles), colliders_added=0)


def audit():
    snapshots = {name: sha(WORK/name) for name in DATA}
    art_before = original_art_snapshot()
    expected, bot_report, customization, scenes, landing = expected_upgrades()
    assert len(scenes['level0']['changed_object_ids']) == 47
    assert scenes['level3']['changed_object_ids'] == [262]
    assert len(bot_report['texture_profiles']) == len(bot_report['renderer_ids']) == 48
    assert len(bot_report['mesh_ids']) == 9
    protected = Counter()
    rows = []
    markers = {}
    atlas_mips = {}
    allowed = {'resources.assets': {1329,1330},
               'sharedassets0.assets': set(bot_report['changed_object_ids']),
               'level0': set(scenes['level0']['changed_object_ids']),
               'level1': set(), 'level2': set(), 'level3': {262}}
    for name in CHANGED:
        before = asset(BASE/name)
        after = asset(WORK/name)
        target = UnityPy.load(expected[name]).file
        oldids, ids = set(before.objects), set(after.objects)
        removed, added = oldids-ids, ids-oldids
        different = {i for i in oldids & ids if before.objects[i].get_raw_data() != after.objects[i].get_raw_data()}
        assert not removed, (name, 'Removed objects', removed)
        assert different == allowed[name] & oldids, (name, 'Changed objects', sorted(different ^ (allowed[name]&oldids)))
        assert ids == set(target.objects), (name, 'Expected object IDs mismatch')
        mismatch = [i for i in ids if after.objects[i].type != target.objects[i].type or
                    after.objects[i].get_raw_data() != target.objects[i].get_raw_data()]
        assert not mismatch, (name, 'In-memory reconstruction mismatch', mismatch)
        # Byte identity also covers serialized type tables, external references,
        # headers and all non-object metadata, beyond the object-level whitelist.
        assert hashlib.sha256(expected[name]).hexdigest() == snapshots[name], (name, 'File reconstruction mismatch')
        if name == 'sharedassets0.assets':
            assert added == set(bot_report['mesh_ids'][7:])
            assert after.objects[188].type.name == 'Font'
            assert after.objects[188].get_raw_data() == before.objects[188].get_raw_data()
        elif name in ('level1','level2','level3'):
            assert len(added) == 15
            markers[name] = check_markers(after, oldids)
        else:
            assert not added, (name, added)
        for i, obj in before.objects.items():
            kind = obj.type.name
            if 'Collider' in kind or kind in ('Rigidbody', 'Animator', 'Animation', 'AudioClip', 'Font', 'Material'):
                assert i not in different, (name, 'Protected component changed', i, kind)
                protected[kind] += 1
            if kind in ('Transform','RectTransform') and i not in allowed[name]:
                assert i not in different
                protected[kind] += 1
        if name == 'resources.assets':
            for ident in (1329,1330):
                tex = after.objects[ident].read()
                assert tex.m_TextureFormat == 12 and tex.m_Width == tex.m_Height == 1536
                mips = mip_report(tex)
                assert len(mips) == 9 and all(m['alpha_min'] == m['alpha_max'] == 255 for m in mips)
                atlas_mips[ident] = mips
        if name == 'level0':
            gs, ts, paths = hierarchy(after)
            for row, names in enumerate(SETTINGS_ROWS):
                for column, label in enumerate(names):
                    t = ts[paths['Menu/Pages/Settings/'+label]]
                    assert t['m_AnchoredPosition'] == dict(x=-124. if column == 0 else 124., y=float(132-row*44))
                    assert t['m_SizeDelta'] == dict(x=216., y=36.)
        if name == 'level3':
            old = before.objects[262].read_typetree()
            new = after.objects[262].read_typetree()
            assert old['m_IndexBuffer'] == new['m_IndexBuffer']
            a, b = old['m_VertexData'], new['m_VertexData']
            count = a['m_VertexCount']; stride = len(a['m_DataSize'])//count
            x_offset = a['m_Channels'][0]['offset']
            av = np.frombuffer(bytes(a['m_DataSize']),np.uint8).reshape(count,stride)
            bv = np.frombuffer(bytes(b['m_DataSize']),np.uint8).reshape(count,stride)
            unchanged_channels = [k for k in range(stride) if not x_offset <= k < x_offset+4]
            assert np.array_equal(av[:,unchanged_channels], bv[:,unchanged_channels])
        rows.append(dict(name=name, sha256=snapshots[name], bytes=(WORK/name).stat().st_size,
                         changed_existing_ids=sorted(different), added_ids=sorted(added),
                         unrelated_old_objects_byte_identical=len(oldids-different),
                         expected_reconstruction_byte_identical=True))
    identical_files = []
    for name in DATA:
        if name in CHANGED:
            continue
        assert snapshots[name] == sha(BASE/name), ('Unexpected modified data file', name)
        identical_files.append(name)
    bot_checks = validate_bots(WORK/'sharedassets0.assets')
    assert original_art_snapshot() == art_before, 'Audit changed artist inputs.'
    assert snapshots == {name: sha(WORK/name) for name in DATA}, 'Working assets changed during audit.'
    return dict(passed=True, baseline=str(BASE), final_assets=str(WORK), files=rows,
                unchanged_data_files=identical_files, unchanged_data_file_count=len(identical_files),
                protected_old_object_counts=dict(protected), player_atlas_mips=atlas_mips,
                opaque_player_mips_verified=18, bot_validation=bot_checks,
                settings_objects_changed=47, landing_markers=markers,
                banner_check=dict(mesh_id=262, indices_and_non_X_vertex_channels_unchanged=True,
                    structural_boxes_checked=scenes['level3']['structural_boxes_checked'],
                    old_intersections=scenes['level3']['old_intersections'],
                    new_intersections=scenes['level3']['new_intersections'],
                    minimum_clearance_m=min(c['minimum_structure_clearance_m'] for c in scenes['level3']['components'])),
                font_188_byte_identical=True, artist_inputs_unchanged=True,
                working_assets_unchanged_during_audit=True, installed_game_modified=False,
                scope='Serialized assets only; headset gameplay and two-computer online tests remain manual.')


if __name__ == '__main__':
    report = audit()
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'], changed_files=len(report['files']),
        unchanged_data_files=report['unchanged_data_file_count'], settings_objects=47,
        opaque_mips=18+report['bot_validation']['opaque_mips_verified'],
        markers_per_court=15, output=str(REPORT))))
