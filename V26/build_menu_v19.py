"""Add the v19 customization overlay and online map controls to v18's menu.

Only level0 changes. Default output is an isolated fixture, never working/ or
the Steam installation. Re-running on the result reuses the named nodes.
Native code owns opening/closing the overlay, updating previews, and room map
properties; no PageController or match callbacks are cloned into this panel.
"""
from pathlib import Path
import argparse, copy, hashlib, json, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
from UnityPy.streams import EndianBinaryReader
from fix_cloudcourt_menu_v16 import hierarchy

BUTTON, IMAGE, TEXT, RAW_IMAGE, CURVED = 463, 1430, 572, 114, 465


def ptr(i):
    return {'m_FileID': 0, 'm_PathID': i}


def script(obj):
    raw = obj.get_raw_data()
    return struct.unpack_from('<q', raw, 20)[0] if obj.type.name == 'MonoBehaviour' and len(raw) >= 28 else None


def set_raw(obj, data):
    obj.set_raw_data(bytes(data))
    # UnityPy otherwise continues reading the pre-edit bytes until reload.
    obj.reader = EndianBinaryReader(bytes(data), endian=obj.reader.endian)
    obj.byte_start, obj.byte_size = 0, len(data)


def save_tree(obj, data):
    obj.save_typetree(data)
    set_raw(obj, obj.data)


def button_layout(raw):
    """Locate m_TargetGraphic and m_OnClick after five animation strings."""
    offset = 224
    for _ in range(5):
        size = struct.unpack_from('<I', raw, offset)[0]
        assert size < 128 and offset + 4 + size <= len(raw)
        offset = (offset + 4 + size + 3) & ~3
    # Interactable occupies four aligned bytes, then the target PPtr.
    return offset + 4, offset + 16


class MenuEditor:
    def __init__(self, file):
        self.file = file
        self.created = []

    def paths(self):
        return hierarchy(self.file)

    def find(self, path):
        return self.paths()[2][path]

    def component(self, transform, wanted):
        go = self.file.objects[self.file.objects[transform].read_typetree()['m_GameObject']['m_PathID']].read_typetree()
        return next((self.file.objects[c['component']['m_PathID']] for c in go['m_Component']
                     if script(self.file.objects[c['component']['m_PathID']]) == wanted), None)

    def active(self, transform, state):
        goid = self.file.objects[transform].read_typetree()['m_GameObject']['m_PathID']
        obj = self.file.objects[goid]
        go = obj.read_typetree()
        go['m_IsActive'] = bool(state)
        save_tree(obj, go)

    def rect(self, transform, x, y, width, height):
        obj = self.file.objects[transform]
        d = obj.read_typetree()
        d['m_AnchorMin'] = d['m_AnchorMax'] = dict(x=.5, y=.5)
        d['m_Pivot'] = dict(x=.5, y=.5)
        d['m_AnchoredPosition'] = dict(x=float(x), y=float(y))
        d['m_LocalPosition'] = dict(x=float(x), y=float(y), z=0.)
        d['m_SizeDelta'] = dict(x=float(width), y=float(height))
        d['m_LocalScale'] = dict(x=1., y=1., z=1.)
        save_tree(obj, d)
        effect = self.component(transform, CURVED)
        if effect:
            raw = bytearray(effect.get_raw_data())
            assert len(raw) == 96
            struct.pack_into('<2f', raw, 60, width, height)
            set_raw(effect, raw)

    def color(self, transform, rgba):
        for wanted in (IMAGE, TEXT, RAW_IMAGE):
            graphic = self.component(transform, wanted)
            if graphic:
                raw = bytearray(graphic.get_raw_data())
                struct.pack_into('<4f', raw, 44, *rgba)
                set_raw(graphic, raw)
        effect = self.component(transform, CURVED)
        if effect:
            raw = bytearray(effect.get_raw_data())
            struct.pack_into('<4f', raw, 68, *rgba)
            set_raw(effect, raw)

    def clone(self, source):
        obj = copy.copy(source)
        obj.path_id = max(self.file.objects) + 1
        obj.assets_file = self.file
        set_raw(obj, source.get_raw_data())
        self.file.objects[obj.path_id] = obj
        return obj.path_id

    def ensure(self, path, template):
        gs, ts, paths = self.paths()
        if path in paths:
            return paths[path]
        parent_path, name = path.rsplit('/', 1)
        parent, source = paths[parent_path], paths[template]
        ids = []
        def collect(t):
            gid = ts[t]['m_GameObject']['m_PathID']
            ids.append(gid)
            ids.extend(c['component']['m_PathID'] for c in gs[gid]['m_Component'])
            for child in ts[t]['m_Children']:
                collect(child['m_PathID'])
        collect(source)
        mapping = {old: self.clone(self.file.objects[old]) for old in dict.fromkeys(ids)}
        def remap(d):
            if isinstance(d, dict):
                if set(d) == {'m_FileID', 'm_PathID'} and d['m_FileID'] == 0 and d['m_PathID'] in mapping:
                    return ptr(mapping[d['m_PathID']])
                return {k: remap(v) for k, v in d.items()}
            if isinstance(d, list):
                return [remap(v) for v in d]
            return d
        for old, new in mapping.items():
            source_obj, obj = self.file.objects[old], self.file.objects[new]
            if source_obj.type.name != 'MonoBehaviour':
                save_tree(obj, remap(source_obj.read_typetree()))
                continue
            raw = bytearray(source_obj.get_raw_data())
            # Remap only actual pointer fields. A global byte replacement can
            # accidentally rewrite numeric colors/geometry that resemble IDs.
            offsets = [0, 32]
            kind = script(source_obj)
            assert kind in (BUTTON, IMAGE, TEXT, RAW_IMAGE, CURVED), ('unsafe UI template', kind)
            if kind == BUTTON:
                target, event = button_layout(raw)
                offsets = [0, 36, 48, 60, 72, 176, 188, 200, 212, target]
                # No inherited persistent listener should navigate or leave a
                # match. Native button dispatch handles the CC_* controls.
                raw = raw[:event] + struct.pack('<I', 0)
            elif kind in (IMAGE, TEXT, RAW_IMAGE):
                offsets += [72]
            for offset in offsets:
                if offset + 12 > len(raw):
                    continue
                fileid, pathid = struct.unpack_from('<iq', raw, offset)
                if not fileid and pathid in mapping:
                    struct.pack_into('<q', raw, offset + 4, mapping[pathid])
            set_raw(obj, raw)
        root = mapping[source]
        d = self.file.objects[root].read_typetree()
        d['m_Father'] = ptr(parent)
        pd = self.file.objects[parent].read_typetree()
        d['m_RootOrder'] = len(pd['m_Children'])
        save_tree(self.file.objects[root], d)
        pd['m_Children'].append(ptr(root))
        save_tree(self.file.objects[parent], pd)
        goid = mapping[ts[source]['m_GameObject']['m_PathID']]
        go = self.file.objects[goid].read_typetree()
        go['m_Name'], go['m_IsActive'] = name, True
        save_tree(self.file.objects[goid], go)
        self.created.append(path)
        return root

    def text(self, transform, text, size=18):
        obj = self.component(transform, TEXT)
        assert obj
        raw = bytearray(obj.get_raw_data())
        length = struct.unpack_from('<I', raw, 128)[0]
        assert length < 3000 and 132 + length <= len(raw)
        suffix = raw[132 + ((length + 3) & ~3):]
        encoded = text.encode('utf-8')
        raw = raw[:128] + struct.pack('<I', len(encoded)) + encoded + b'\0' * (-len(encoded) % 4) + suffix
        struct.pack_into('<i', raw, 84, size)
        struct.pack_into('<i', raw, 100, max(size, 28))
        raw[60] = 0  # Decorative text must never swallow the controller ray.
        set_raw(obj, raw)
        self.color(transform, (.98, .95, .87, 1.))

    def label(self, path, text, x, y, width, height=28, size=18):
        t = self.ensure(path, 'Menu/Pages/InGame/Resume Button/Text')
        self.rect(t, x, y, width, height)
        self.text(t, text, size)
        self.active(t, True)
        return t

    def button(self, path, text, x, y, width=200, height=40, size=17):
        t = self.ensure(path, 'Menu/Pages/InGame/Resume Button')
        self.rect(t, x, y, width, height)
        self.active(t, True)
        self.color(t, (1., 1., 1., 1.))
        child = self.find(path + '/Text')
        self.text(child, text, size)
        image = self.component(t, IMAGE)
        raw = bytearray(image.get_raw_data())
        raw[60] = 1
        set_raw(image, raw)
        return t


def build_menu(menu):
    e = MenuEditor(menu)
    # Preserve original controller fields/references; only hide unused widgets.
    hidden = ['Menu/Pages/Settings/Sets Button', 'Menu/Pages/Settings/Points Button',
              'Menu/Pages/Solo/Beach Night']
    for path in hidden:
        e.active(e.find(path), False)
    e.text(e.find('Menu/Pages/Solo/Beach Day/Text'), 'Beach', 19)
    for i in range(4):
        e.active(e.find('Menu/Pages/InGame/PuloSkin' + str(i)), False)

    e.button('Menu/Pages/Start/CC_CustomizeOpen', 'CUSTOMIZATION', 0, -140, 260, 40, 18)
    e.button('Menu/Pages/InGame/CC_CustomizeOpen', 'CUSTOMIZATION', 0, 22, 240, 44, 18)
    e.rect(e.find('Menu/Pages/InGame/PuloTeams'), 0, 82, 240, 40)

    # Map selection sits before Create Room: Activated on the CreateRoom page
    # immediately creates the room, so controls on that page would be too late.
    online = 'Menu/Pages/Online'
    e.active(e.find(online + '/Text'), False)
    e.label(online + '/CC_MapTitle', 'HOST MAP', 0, 94, 340, 25, 17)
    e.label(online + '/CC_MapLabel', 'Indoor', 0, 52, 235, 34, 24)
    e.button(online + '/CC_MapPrev', '<', -157, 52, 56, 38, 23)
    e.button(online + '/CC_MapNext', '>', 157, 52, 56, 38, 23)
    for name, y in [('Create Room Button', -12), ('Join Room Button', -66), ('Back Button', -132)]:
        e.rect(e.find(online + '/Buttons/' + name), 0, y, 250, 40)

    panel = 'Menu/CC_Customization'
    p = e.ensure(panel, 'Menu/Pages/Alert/Background')
    e.rect(p, 0, 0, 800, 400)
    e.color(p, (1., 1., 1., 1.))
    image = e.component(p, IMAGE)
    raw = bytearray(image.get_raw_data())
    raw[60] = 1  # Modal backdrop blocks clicks into the previous page.
    set_raw(image, raw)
    e.label(panel + '/CC_CustomTitle', 'MAKE IT YOURS', 0, 155, 650, 46, 32)
    e.label(panel + '/CC_CustomHint', 'Pick a face. Mix an outfit.', 0, 115, 650, 27, 16)
    e.label(panel + '/CC_FaceTitle', 'FACE', -165, 79, 240, 28, 19)
    e.label(panel + '/CC_OutfitTitle', 'OUTFIT', 165, 79, 240, 28, 19)
    for kind, x in [('Face', -165), ('Outfit', 165)]:
        # Native v19 binds the separate 3x3 face/outfit atlases and uvRect.
        # A transparent empty RawImage never flashes the inherited splash logo.
        t = e.ensure(panel + '/CC_' + kind + 'Preview', 'Menu/Pages/Start/Splash')
        e.rect(t, x, 14, 126, 96)
        e.active(t, True)
        obj = e.component(t, RAW_IMAGE)
        raw = bytearray(obj.get_raw_data())
        bound = struct.unpack_from('<q', raw, 76)[0] != 0
        if not bound:
            struct.pack_into('<iq', raw, 72, 0, 0)
            struct.pack_into('<4f', raw, 84, 0., 0., 1., 1.)
        raw[60] = 0
        set_raw(obj, raw)
        if not bound:
            e.color(t, (1., 1., 1., 0.))
    e.label(panel + '/CC_FaceLabel', 'Cool  1 / 9', -165, -63, 258, 29, 17)
    e.label(panel + '/CC_OutfitLabel', 'Black Suit  3 / 9', 165, -63, 258, 29, 17)
    for name, label, x, y in [
        ('CC_FacePrev', '<', -260, -105), ('CC_FaceNext', '>', -70, -105),
        ('CC_OutfitPrev', '<', 70, -105), ('CC_OutfitNext', '>', 260, -105),
        ('CC_CustomizeBack', 'DONE', 0, -161)]:
        e.button(panel + '/' + name, label, x, y, 180 if name.endswith('Back') else 70, 40, 22 if label != 'DONE' else 18)
    e.active(p, False)
    return {'created_nodes': e.created,
            'overlay': panel, 'overlay_default_active': False,
            'customize_open_on': ['Menu/Pages/Start', 'Menu/Pages/InGame'],
            'map_chooser': online, 'hidden': hidden + ['Menu/Pages/InGame/PuloSkin' + str(i) for i in range(4)],
            'preview_names': ['CC_FacePreview', 'CC_OutfitPreview'],
            'native_work_required': ['Open/close overlay without page navigation',
                                     'Bind preview textures, uvRects and Graphic color alpha=1',
                                     'Update independent face/outfit names',
                                     'Hide old PuloSkin buttons in in_game_active_hook',
                                     'Solo layout: show Beach Night only in format selector (stage=0)',
                                     'Store host map before CreateRoom and sync to joining clients'],
            'changes_only': 'level0', 'VR_tested': False}


def bind_v19_preview_assets(menu, bindings):
    """Bind art before runtime so previews work even before avatars are loaded.

    bindings can be the dictionary, or the generated unity-bindings.json path.
    Apply after the art builder has created the referenced resources textures.
    """
    if isinstance(bindings, (str, Path)):
        bindings = json.loads(Path(bindings).read_text(encoding='utf-8'))
    e = MenuEditor(menu)
    index = next((i + 1 for i, ext in enumerate(menu.externals)
                  if ext.path.replace('\\', '/').rsplit('/', 1)[-1].lower() == 'resources.assets'), None)
    if index is None:
        ext = copy.copy(menu.externals[0])
        ext.path, ext.type, ext.guid = 'resources.assets', 0, b'\0' * 16
        menu.externals.append(ext)
        index = len(menu.externals)
    records = []
    for kind, selected in [('face', 0), ('outfit', int(bindings.get('default_outfit', 2)))]:
        name = 'CC_' + kind.title() + 'Preview'
        transform = e.find('Menu/CC_Customization/' + name)
        obj = e.component(transform, RAW_IMAGE)
        raw = bytearray(obj.get_raw_data())
        texture = int(bindings['texture_ids'][kind])
        struct.pack_into('<iq', raw, 72, index, texture)
        size = 1 / 3 if kind == 'face' else 1 / 6
        uv = (selected % 3 / 3, (2 - selected // 3) / 3, size, size)
        struct.pack_into('<4f', raw, 84, *uv)
        raw[60] = 0
        set_raw(obj, raw)
        e.color(transform, (1., 1., 1., 1.))
        records.append({'name': name, 'external_file': index, 'texture': texture, 'uv': list(uv)})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=R / 'working/VolleyballFever_Data')
    parser.add_argument('--output', type=Path, default=R / 'visuals-v19-menu')
    args = parser.parse_args()
    source = args.source / 'level0' if args.source.is_dir() else args.source
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    original = source.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    backup = output / ('level0-before-v19-' + sha[:16] + '.backup')
    if not backup.exists():
        backup.write_bytes(original)
    menu = UnityPy.load(original).file
    report = build_menu(menu)
    result = menu.save()
    (output / 'level0').write_bytes(result)
    report.update(source=str(source), source_sha256=sha, backup=str(backup),
                  output=str(output / 'level0'), output_sha256=hashlib.sha256(result).hexdigest())
    (output / 'menu-v19-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
