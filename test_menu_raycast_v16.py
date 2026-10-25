"""Regression for the shipped menu's actual RectTransforms and Graphic flags.

Models straight-on hit testing in canvas coordinates, before CurvedUI's curvature
mapping. This tests the asset occlusion bug, not headset tracking/rendering.
"""
from pathlib import Path
import sys, json, struct, hashlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
import numpy as np
from PIL import Image
from fix_cloudcourt_menu_v16 import hierarchy


def script(obj):
    return struct.unpack_from('<q', obj.get_raw_data(), 20)[0] if obj.type.name == 'MonoBehaviour' else None


class Menu:
    def __init__(self, path):
        self.file = UnityPy.load(str(path)).file
        self.go, self.t, self.paths = hierarchy(self.file)
        self.root = self.paths['Menu']
        self.start = self.paths['Menu/Pages/Start']
        self.order = []
        def visit(i):
            self.order.append(i)
            for child in self.t[i]['m_Children']:
                visit(child['m_PathID'])
        visit(self.root)

    def components(self, i):
        return [self.file.objects[c['component']['m_PathID']]
                for c in self.go[self.t[i]['m_GameObject']['m_PathID']]['m_Component']]

    def active(self, i):
        if i == self.start:
            return True  # Navigation activates the main page at runtime.
        if not self.go[self.t[i]['m_GameObject']['m_PathID']]['m_IsActive']:
            return False
        parent = self.t[i]['m_Father']['m_PathID']
        return self.active(parent) if parent in self.t else True

    def rect(self, i):
        t = self.t[i]
        if i == self.root:
            return (-400., -200., 800., 400.)
        parent = t['m_Father']['m_PathID']
        x, y, w, h = self.rect(parent)
        lo, hi, pivot = t['m_AnchorMin'], t['m_AnchorMax'], t['m_Pivot']
        width = (hi['x'] - lo['x']) * w + t['m_SizeDelta']['x']
        height = (hi['y'] - lo['y']) * h + t['m_SizeDelta']['y']
        px = x + (lo['x'] + (hi['x'] - lo['x']) * pivot['x']) * w + t['m_AnchoredPosition']['x']
        py = y + (lo['y'] + (hi['y'] - lo['y']) * pivot['y']) * h + t['m_AnchoredPosition']['y']
        return (px - pivot['x'] * width, py - pivot['y'] * height, width, height)

    def button_at(self, x, y):
        for i in reversed(self.order):
            if not self.active(i):
                continue
            graphics = [o for o in self.components(i) if script(o) in (572, 114, 1430)]
            if not any(o.get_raw_data()[12] and o.get_raw_data()[60] for o in graphics):
                continue
            rx, ry, w, h = self.rect(i)
            if not (rx <= x <= rx + w and ry <= y <= ry + h):
                continue
            target = i
            while target in self.t:
                if any(script(o) == 463 for o in self.components(target)):
                    return target
                target = self.t[target]['m_Father']['m_PathID']
            return None  # A decorative topmost Graphic swallowed the hit.
        return None


base = R / 'versions/cloudcourt-v16-antes-menu-fix'
before = Menu(base / 'level0')
after = Menu(R / 'working/VolleyballFever_Data/level0')
samples, blocked_before = 0, 0
for button in ['Solo Button', 'Online Button', 'Settings Button', 'Quit Button']:
    target = after.paths['Menu/Pages/Start/' + button]
    x, y, w, h = after.rect(target)
    for fx in (.2, .5, .8):
        for fy in (.2, .5, .8):
            px, py = x + fx * w, y + fy * h
            blocked_before += before.button_at(px, py) != target
            assert after.button_at(px, py) == target, (button, fx, fy)
            samples += 1
assert blocked_before == samples == 36

# The controls, input modules and UnityEvent listeners retain their original bytes.
for i, obj in after.file.objects.items():
    if script(obj) in (463, 474, 1052, 601, 1228):
        assert obj.get_raw_data() == before.file.objects[i].get_raw_data(), i
for path in ['Menu/Pages/Start/Splash', 'Menu/Pages/Intro', 'Menu/Pages/DailyChallenge']:
    assert not after.active(after.paths[path])
for path in ['Menu/Pages/Start/Cloudcourt CLOUDCOURT VR',
             'Menu/Pages/Start/Cloudcourt Big rallies. Good company.']:
    t = after.t[after.paths[path]]
    assert t['m_AnchorMin'] == t['m_AnchorMax'] == {'x': .5, 'y': .5}

g = UnityPy.load(str(R / 'working/VolleyballFever_Data/globalgamemanagers.assets')).file
old = UnityPy.load(str(base / 'globalgamemanagers.assets')).file
changed = [i for i, o in g.objects.items() if o.get_raw_data() != old.objects[i].get_raw_data()]
assert changed == [3], changed
image = g.objects[3].read().image.convert('RGBA')
expected = Image.open(R / 'assets/cloudcourt-v16/logo.png').convert('RGBA')
a, b = np.array(image).astype(float), np.array(expected).astype(float)
assert np.array_equal(a[:, :, 3], b[:, :, 3])
# Keep the original DXT5 format; compare visible colors allowing its block loss.
error = np.abs(a[:, :, :3] * a[:, :, 3:4] / 255 - b[:, :, :3] * b[:, :, 3:4] / 255).mean()
assert error < 4, error
settings = UnityPy.load(str(R / 'working/VolleyballFever_Data/globalgamemanagers')).file.objects[1].read_typetree()
assert settings['m_VirtualRealitySplashScreen'] == {'m_FileID': 1, 'm_PathID': 3}
assert [e.path for e in after.file.externals][:1] == ['globalgamemanagers.assets']
for i in (727, 752):
    assert struct.unpack_from('<iq', after.file.objects[i].get_raw_data(), 72) == (1, 3)

assert hashlib.sha256((R / 'working/GameAssembly.dll').read_bytes()).digest() == hashlib.sha256((base / 'GameAssembly.dll').read_bytes()).digest()
report = {'passed': True, 'previously_blocked_points': blocked_before,
          'button_hit_points_now_routed': samples, 'buttons': 4,
          'button_events_and_input_modules_unchanged': True,
          'old_menu_logo_disabled': True, 'VR_and_menu_logo_replaced': True,
          'other_global_objects_unchanged': len(g.objects) - 1,
          'scope': 'Serialized Unity assets and canvas hit-test regression; headset playtest pending.'}
(R / 'analysis/v16-menu-raycast-tests.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
