"""Add an English graphics selector inside the existing CurvedUI bounds.

In-memory helper only edits level0; standalone writes an isolated fixture.
"""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_menu_v19 import MenuEditor,IMAGE,set_raw

def build_menu_v24(file):
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    e=MenuEditor(file);settings='Menu/Pages/Settings';panel='Menu/CC_Graphics'
    # This original control only changes eye resolution. The new selector owns
    # that same rendering setting plus textures, shadows, antialiasing/effects.
    e.active(e.find(settings+'/Resolution Button'),False)
    e.button(settings+'/CC_GraphicsOpen','GRAPHICS: ULTRA',124,-44,228,36,16)
    root=e.ensure(panel,'Menu/Pages/Alert/Background')
    e.rect(root,0,0,800,400);e.color(root,(1.,1.,1.,1.))
    image=e.component(root,IMAGE);raw=bytearray(image.get_raw_data());raw[60]=1;set_raw(image,raw)
    e.label(panel+'/CC_GraphicsTitle','GRAPHICS',0,150,700,45,32)
    e.label(panel+'/CC_GraphicsHint','Choose your balance of detail and smoothness.',0,106,700,30,18)
    for name,label,x in [('Low','LOW',-252),('Medium','MEDIUM',-84),('High','HIGH',84),('Ultra','[ ULTRA ]',252)]:
        e.button(panel+'/CC_Graphics'+name,label,x,48,152,42,19)
    e.label(panel+'/CC_GraphicsDetails','100% render scale | 4x MSAA\nFull textures | Soft shadows, 150 m | Full effects',0,-28,740,72,19)
    e.label(panel+'/CC_GraphicsLocal','Applies instantly. Saved on this device.',0,-100,720,30,17)
    e.button(panel+'/CC_GraphicsBack','DONE',0,-168,200,38,19)
    e.active(root,False)
    return dict(changed_existing_ids=sorted(i for i,b in before.items() if file.objects[i].get_raw_data()!=b),
                created_ids=sorted(set(file.objects)-set(before)),created_paths=e.created,
                canvas_bounds_unchanged=True,canvas_added_overlay_child=True,
                presets=['LOW','MEDIUM','HIGH','ULTRA'],default='ULTRA',original_resolution_control_hidden=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v23-antes-v24/level0')
    ap.add_argument('--output',type=Path,default=R/'visuals-v24-graphics/level0');a=ap.parse_args()
    assert a.output.resolve()!=a.source.resolve() and not any(x in ('working','sources') for x in a.output.relative_to(R).parts)
    f=UnityPy.load(str(a.source)).file;report=build_menu_v24(f);data=f.save()
    a.output.parent.mkdir(exist_ok=True,parents=True);a.output.write_bytes(data)
    report.update(source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest())
    a.output.with_name('graphics-v24-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
