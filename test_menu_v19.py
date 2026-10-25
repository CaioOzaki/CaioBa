"""Validate actual v19 serialized UI wiring, modal hit tests and idempotence."""
from pathlib import Path
import argparse, hashlib, json, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
from build_menu_v19 import MenuEditor, build_menu, bind_v19_preview_assets, button_layout, hierarchy, script, BUTTON, IMAGE, TEXT, RAW_IMAGE


class HitTest:
    def __init__(self, menu, page, overlay=False):
        self.file = menu
        self.gs, self.ts, self.paths = hierarchy(menu)
        self.reverse = {t: path for path, t in self.paths.items()}
        self.page, self.overlay = 'Menu/Pages/' + page, overlay
        self.order = []
        def visit(t):
            self.order.append(t)
            for c in self.ts[t]['m_Children']:
                visit(c['m_PathID'])
        visit(self.paths['Menu'])

    def objects(self, t):
        return [self.file.objects[c['component']['m_PathID']]
                for c in self.gs[self.ts[t]['m_GameObject']['m_PathID']]['m_Component']]

    def active(self, t):
        path = self.reverse[t]
        if path == self.page:
            return True
        if path == 'Menu/CC_Customization':
            return self.overlay
        go = self.gs[self.ts[t]['m_GameObject']['m_PathID']]
        if not go['m_IsActive']:
            return False
        parent = self.ts[t]['m_Father']['m_PathID']
        return self.active(parent) if parent in self.ts else True

    def rect(self, t):
        if self.reverse[t] == 'Menu':
            return -400., -200., 800., 400.
        d = self.ts[t]
        parent = d['m_Father']['m_PathID']
        x, y, w, h = self.rect(parent)
        if 'm_SizeDelta' not in d:
            return x, y, w, h
        lo, hi, pivot = d['m_AnchorMin'], d['m_AnchorMax'], d['m_Pivot']
        rw = (hi['x'] - lo['x']) * w + d['m_SizeDelta']['x']
        rh = (hi['y'] - lo['y']) * h + d['m_SizeDelta']['y']
        px = x + (lo['x'] + (hi['x'] - lo['x']) * pivot['x']) * w + d['m_AnchoredPosition']['x']
        py = y + (lo['y'] + (hi['y'] - lo['y']) * pivot['y']) * h + d['m_AnchoredPosition']['y']
        return px - pivot['x'] * rw, py - pivot['y'] * rh, rw, rh

    def button_at(self, x, y):
        for t in reversed(self.order):
            if not self.active(t) or 'm_SizeDelta' not in self.ts[t]:
                continue
            graphics = [o for o in self.objects(t) if script(o) in (IMAGE, TEXT, RAW_IMAGE)]
            if not any(o.get_raw_data()[12] and o.get_raw_data()[60] for o in graphics):
                continue
            rx, ry, width, height = self.rect(t)
            if not (rx <= x <= rx + width and ry <= y <= ry + height):
                continue
            target = t
            while target in self.ts:
                if any(script(o) == BUTTON for o in self.objects(target)):
                    return target
                target = self.ts[target]['m_Father']['m_PathID']
            return None  # The modal backdrop intentionally consumes this ray.
        return None

    def assert_button(self, path):
        target = self.paths[path]
        x, y, w, h = self.rect(target)
        for fx in (.2, .5, .8):
            for fy in (.2, .5, .8):
                assert self.button_at(x + w * fx, y + h * fy) == target, (path, fx, fy)
        return 9


def validate(path, source):
    before = UnityPy.load(str(source)).file
    menu = UnityPy.load(str(path)).file
    e = MenuEditor(menu)
    g, t, paths = hierarchy(menu)
    panel = paths['Menu/CC_Customization']
    assert not g[t[panel]['m_GameObject']['m_PathID']]['m_IsActive']
    # Pure visual panel: it owns no PageController/scene/team callback scripts.
    panel_components = [menu.objects[c['component']['m_PathID']]
                        for c in g[t[panel]['m_GameObject']['m_PathID']]['m_Component']]
    assert {script(o) for o in panel_components if o.type.name == 'MonoBehaviour'} == {1430, 465}
    for path_name in ['Menu/Pages/Settings/Sets Button', 'Menu/Pages/Settings/Points Button',
                      'Menu/Pages/Solo/Beach Night'] + ['Menu/Pages/InGame/PuloSkin' + str(i) for i in range(4)]:
        assert not g[t[paths[path_name]]['m_GameObject']['m_PathID']]['m_IsActive'], path_name
    # Original runtime handler fields and all original interactive components
    # retain their bytes, including Resume/Leave and settings button references.
    for ident in (1004, 712, 905, 808, 859, 907, 890, 792, 769, 999, 1006, 981):
        assert menu.objects[ident].get_raw_data() == before.objects[ident].get_raw_data(), ident

    nodes, buttons = 0, 0
    for name, tr in paths.items():
        if '/CC_' not in name:
            continue
        nodes += 1
        for o in HitTest(menu, 'Start').objects(tr):
            if script(o) == BUTTON:
                buttons += 1
                raw = o.get_raw_data()
                target, event = button_layout(raw)
                assert struct.unpack_from('<I', raw, event)[0] == 0
                fileid, graphic = struct.unpack_from('<iq', raw, target)
                assert fileid == 0 and graphic == e.component(tr, IMAGE).path_id, name
                assert len(raw) == event + 4
            elif script(o) in (TEXT, RAW_IMAGE):
                assert o.get_raw_data()[60] == 0, name

    assert buttons == 9  # Two Open + two map controls + four appearance + Done.
    hits = 0
    for page in ('Start', 'InGame'):
        hit = HitTest(menu, page)
        hits += hit.assert_button('Menu/Pages/' + page + '/CC_CustomizeOpen')
    hit = HitTest(menu, 'Online')
    for name in ('CC_MapPrev', 'CC_MapNext', 'Buttons/Create Room Button', 'Buttons/Join Room Button', 'Buttons/Back Button'):
        hits += hit.assert_button('Menu/Pages/Online/' + name)
    hit = HitTest(menu, 'InGame', overlay=True)
    for name in ('CC_FacePrev', 'CC_FaceNext', 'CC_OutfitPrev', 'CC_OutfitNext', 'CC_CustomizeBack'):
        hits += hit.assert_button('Menu/CC_Customization/' + name)
    assert hit.button_at(0, 134) is None  # Underlying Resume cannot receive it.
    assert hit.button_at(0, 82) is None  # Underlying Change Teams cannot receive it.
    # The builder must not duplicate controls or slowly grow reference tables.
    original = path.read_bytes()
    reapplied = build_menu(menu)
    assert reapplied['created_nodes'] == []
    result = menu.save()
    assert result == original, ('not byte-idempotent', hashlib.sha256(result).hexdigest())
    binding = R / 'assets/customization-v19/unity-bindings.json'
    bound_previews = []
    if binding.exists():
        bound = UnityPy.load(result).file
        bound_previews = bind_v19_preview_assets(bound, binding)
        data = bound.save()
        bound = UnityPy.load(data).file
        be = MenuEditor(bound)
        for rec in bound_previews:
            tr = be.find('Menu/CC_Customization/' + rec['name'])
            raw = be.component(tr, RAW_IMAGE).get_raw_data()
            fid, tid = struct.unpack_from('<iq', raw, 72)
            assert (fid, tid) == (rec['external_file'], rec['texture'])
            assert bound.externals[fid - 1].path == 'resources.assets'
            assert all(abs(x - y) < 1e-6 for x, y in zip(struct.unpack_from('<4f', raw, 84), rec['uv']))
            assert struct.unpack_from('<f', raw, 56)[0] == 1. and raw[60] == 0
        bind_v19_preview_assets(bound, binding)
        build_menu(bound)
        assert bound.save() == data, 'Rebuild must preserve serialized preview art bindings.'
    return {'passed': True, 'buttons': buttons, 'sampled_button_hits': hits,
            'idempotent_exact_bytes': True, 'original_controller_and_event_fields_unchanged': True,
            'no_original_game_assets_rebuilt': True,
            'modal_blocks_underlying_controls': True, 'bound_previews': bound_previews, 'VR_tested': False,
            'scope': 'Serialized event/pointer and 2D UI hit-test validation; headset input is native work tested separately.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--asset', type=Path, default=R / 'visuals-v19-menu/level0')
    ap.add_argument('--source', type=Path, default=R / 'versions/cloudcourt-v18-antes-v19/level0')
    args = ap.parse_args()
    report = validate(args.asset, args.source)
    (R / 'analysis/v19-menu-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
