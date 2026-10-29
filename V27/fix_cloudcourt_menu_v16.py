"""Repair decorative UI raycast occlusion and the shared menu/VR splash logo."""
from pathlib import Path
import struct, sys, json

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
from PIL import Image, ImageDraw, ImageFont


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


def splash_logo():
    """Original logotype and volleyball artwork, using the project's OFL font."""
    image = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    cream, gold, blue, coral, navy = '#fff1dc', '#ffcf58', '#248fda', '#fa5b68', '#172b46'
    draw.rounded_rectangle((152, 236, 1896, 804), radius=100, fill=navy, outline=gold, width=12)
    draw.ellipse((850, 92, 1198, 440), fill=cream, outline=navy, width=12)
    draw.arc((876, 118, 1172, 414), 190, 355, fill=blue, width=25)
    draw.arc((900, 110, 1194, 416), 62, 225, fill=coral, width=25)
    draw.arc((850, 152, 1146, 448), 267, 63, fill=navy, width=16)
    font = str(R / 'assets/cloudcourt-v16/CloudcourtBubble.ttf')
    draw.text((1024, 532), 'CLOUDCOURT', font=ImageFont.truetype(font, 216), anchor='mm', fill=cream)
    draw.rounded_rectangle((912, 674, 1136, 766), radius=35, fill=gold)
    draw.text((1024, 710), 'VR', font=ImageFont.truetype(font, 76), anchor='mm', fill=navy)
    image.save(R / 'assets/cloudcourt-v16/logo.png')
    return image


def fix_menu_assets(menu, globals_asset):
    objects, transforms, paths = hierarchy(menu)
    titles = ['Menu/Pages/Start/Cloudcourt CLOUDCOURT VR',
              'Menu/Pages/Start/Cloudcourt Big rallies. Good company.']
    for path in titles:
        i = paths[path]
        data = transforms[i]
        # The cloned label used stretch anchors. Its effective 1500x448 rect
        # covered all four buttons although the visible title occupied one line.
        data['m_AnchorMin'] = data['m_AnchorMax'] = {'x': .5, 'y': .5}
        data['m_Pivot'] = {'x': .5, 'y': .5}
        data['m_SizeDelta'] = {'x': 700., 'y': 48.}
        menu.objects[i].save_typetree(data)
    disabled = []
    for path in ['Menu/Pages/Start/Splash', 'Menu/Pages/Intro', 'Menu/Pages/DailyChallenge']:
        go = transforms[paths[path]]['m_GameObject']['m_PathID']
        data = objects[go]
        data['m_IsActive'] = False
        menu.objects[go].save_typetree(data)
        disabled.append(path)
    decorative, buttons = [], []
    for path, i in paths.items():
        if not path.startswith('Menu/'):
            continue
        go = objects[transforms[i]['m_GameObject']['m_PathID']]
        components = [menu.objects[c['component']['m_PathID']] for c in go['m_Component']]
        has_button = any(o.type.name == 'MonoBehaviour' and len(o.get_raw_data()) >= 28
                         and struct.unpack_from('<q', o.get_raw_data(), 20)[0] == 463 for o in components)
        for obj in components:
            if obj.type.name == 'MonoBehaviour':
                raw = bytearray(obj.get_raw_data())
                if len(raw) < 72:
                    continue
                script = struct.unpack_from('<q', raw, 20)[0]
                if script in (572, 114):  # Text and RawImage are decorative.
                    raw[60] = 0
                    obj.set_raw_data(bytes(raw))
                    decorative.append(obj.path_id)
                elif script == 1430 and has_button:
                    raw[60] = 1
                    obj.set_raw_data(bytes(raw))
                    buttons.append(obj.path_id)
            elif obj.type.name == 'CanvasGroup' and path == 'Menu/Pages/Intro':
                data = obj.read_typetree()
                data['m_BlocksRaycasts'] = False
                data['m_Interactable'] = False
                obj.save_typetree(data)
    # Texture 3 is also PlayerSettings.m_VirtualRealitySplashScreen and the
    # texture of both menu RawImages. Replacing that source fixes the headset's
    # loading card as well as any code that reactivates an inherited splash.
    texture = globals_asset.objects[3].read()
    assert texture.m_Name in ('Logo', 'Cloudcourt VR Logo')
    texture.m_Name = 'Cloudcourt VR Logo'
    texture.set_image(splash_logo(), mipmap_count=1)
    texture.save()
    return {'centered_title_anchors': titles, 'disabled_old_widgets': disabled,
            'decorative_graphics_ignore_rays': len(decorative),
            'button_graphics_accept_rays': len(buttons),
            'VR_and_menu_logo': 'globalgamemanagers.assets:3',
            'native_input_unchanged': True}


if __name__ == '__main__':
    root = R / 'working/VolleyballFever_Data'
    menu = UnityPy.load(str(root / 'level0')).file
    globals_asset = UnityPy.load(str(root / 'globalgamemanagers.assets')).file
    report = fix_menu_assets(menu, globals_asset)
    (root / 'level0').write_bytes(menu.save())
    (root / 'globalgamemanagers.assets').write_bytes(globals_asset.save())
    (R / 'analysis/v16-menu-repair.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
