"""Recolor only BOT 5's hair palette and eyebrows in the installed v16 assets."""
from pathlib import Path
import hashlib, json, shutil, sys, importlib.util

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import UnityPy
import numpy as np
from PIL import Image

H = lambda data: hashlib.sha256(data).hexdigest()
baseline = R / 'versions/cloudcourt-v16-antes-cabelo'
manifest = json.loads((R / 'distribution/Cloudcourt-v16-checkpoint/patch.json').read_text())
live = Path('C:/APPS/STEAM/steamapps/common/Volleyball')
baseline.mkdir(parents=True, exist_ok=True)
for record in manifest['files']:
    source = R / 'working' / record['path']
    target = baseline / Path(record['path']).name
    if target.exists():
        assert H(target.read_bytes()) == record['modified_sha256']
    else:
        assert H(source.read_bytes()) == record['modified_sha256'], record['path']
        assert H((live / record['path']).read_bytes()) == record['modified_sha256'], record['path']
        shutil.copyfile(source, target)

source = R / 'create_puloviva_characters.py'
if not (baseline / source.name).exists():
    shutil.copyfile(source, baseline / source.name)
    for image in (R / 'assets/cloudcourt-v16').glob('*.png'):
        shutil.copyfile(image, baseline / image.name)
text = source.read_text(encoding='utf-8')
text = text.replace("'#342b27','#e4dfd9','#f1f0e9'", "'#342b27','#171b24','#f1f0e9'")
text = text.replace('White hair is geometry;', 'Hair is geometry;')
source.write_text(text, encoding='utf-8')
spec = importlib.util.spec_from_file_location('cloudcourt_characters', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.HAIRS[4] == '#171b24'
assert module.SHIRTS[4] == module.SHOES[4] == '#762f49'

path = R / 'working/VolleyballFever_Data/sharedassets0.assets'
asset = UnityPy.load(str(baseline / path.name)).file
before = {i: H(o.get_raw_data()) for i, o in asset.objects.items()}
texture_ids = set()
for obj in asset.objects.values():
    if obj.type.name != 'Material':
        continue
    data = obj.read_typetree()
    if not data['m_Name'].startswith(('SimpleCitizens_Grandma_', 'SimpleCitizens_Cheerleader_')):
        continue
    tex = next(v['m_Texture'] for k, v in data['m_SavedProperties']['m_TexEnvs'] if k == '_MainTex')
    assert tex['m_FileID'] == 0
    texture_ids.add(tex['m_PathID'])
assert texture_ids
for i in texture_ids:
    texture = asset.objects[i].read()
    texture.set_image(module.ATLASES[4], mipmap_count=1)
    texture.save()
path.write_bytes(asset.save())
result = UnityPy.load(str(path)).file
changed = {i for i, o in result.objects.items() if H(o.get_raw_data()) != before[i]}
assert changed == texture_ids, (changed, texture_ids)
for i in texture_ids:
    actual = np.array(result.objects[i].read().image.convert('RGB'))
    assert np.array_equal(actual, np.array(module.ATLASES[4]))
for image in (R / 'assets/cloudcourt-v16').glob('*.png'):
    if image.name not in {'bot-05-atlas.png', 'bot-05-rosto.png', 'bot-05-modelo.png', 'bots-visuais.png'}:
        assert image.read_bytes() == (baseline / image.name).read_bytes(), image.name
report = {'checkpoint': 'Cloudcourt-v16-cabelo-preto', 'changed_texture_ids': sorted(changed),
          'other_unity_objects_unchanged': len(before) - len(changed),
          'hair': '#171b24', 'shirt_and_shoes': '#762f49',
          'scope': 'Shared bot appearance used by solo and online; no protocol or gameplay changes.',
          'asset_sha256': H(path.read_bytes())}
(R / 'analysis/v16-hair-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
