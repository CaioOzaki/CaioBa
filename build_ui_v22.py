"""Keep customization fully inside the original CurvedUI raycast canvas.

v21 enlarged only the modal to 490px and moved Done below the canvas's
400px collider. Preserve the root canvas, pages and controllers; fit the
modal's new hand controls into its original raycast bounds instead.
"""
from pathlib import Path
import argparse, hashlib, json, sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy
from build_menu_v19 import MenuEditor

def build_menu(file):
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    e=MenuEditor(file);p='Menu/CC_Customization'
    e.rect(e.find(p),0,0,800,400)
    for name,x,w in [('CC_HandToneTitle',-190,130),('CC_HandToneLabel',70,220),
                     ('CC_HandTonePrev',-70,60),('CC_HandToneNext',260,60),
                     ('CC_HandToneSwatch',-245,34)]:
        e.rect(e.find(p+'/'+name),x,-145,w,30 if name.endswith(('Prev','Next')) else 28)
    e.rect(e.find(p+'/CC_CustomizeBack'),0,-181,180,32)
    return {'changed_existing_ids':[i for i,b in before.items() if file.objects[i].get_raw_data()!=b],
            'created_ids':sorted(set(file.objects)-set(before)),
            'canvas_unchanged':file.objects[e.find('Menu')].get_raw_data()==before[e.find('Menu')],
            'modal_height':400,'done_center_y':-181,'done_bottom_y':-197,
            'reason':'v21 Done center -213 lay below the unchanged canvas collider at -200'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v21-antes-v22/level0')
    ap.add_argument('--output',type=Path,default=R/'visuals-v22-ui/level0');a=ap.parse_args()
    assert a.output.resolve()!=a.source.resolve() and not any(x in ('working','sources') for x in a.output.relative_to(R).parts)
    f=UnityPy.load(str(a.source)).file;report=build_menu(f);data=f.save()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(data)
    report.update(source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest())
    a.output.with_name('ui-v22-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
