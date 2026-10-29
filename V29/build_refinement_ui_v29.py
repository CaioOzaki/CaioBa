"""v29 compact native-menu panels and the actual startup texture.

In-memory authoring only. Every new button has zero serialized listeners;
runtime owns native routing, matches, unlocks and stats. No game controllers,
physics, canvas raycast dimensions or existing menu emblem are replaced.
"""
from pathlib import Path
import hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
from PIL import Image,ImageDraw,ImageFont
from build_menu_v19 import MenuEditor,IMAGE,RAW_IMAGE,TEXT,BUTTON,set_raw
from build_art_v26 import banner_art
from build_landing_v20 import raw
A=R/'assets/refinement-v29'

def apply_refinement_ui_v29(level0):
    before={i:o.get_raw_data() for i,o in level0.objects.items()};e=MenuEditor(level0)
    def panel(name):
        path='Menu/'+name;t=e.ensure(path,'Menu/Pages/Alert/Background')
        e.rect(t,0,0,800,400);e.color(t,(1.,1.,1.,1.))
        image=e.component(t,IMAGE);b=bytearray(image.get_raw_data());b[60]=1;set_raw(image,b)
        return path,t
    training,root=panel('CC_Training')
    e.label(training+'/CC_TrainingTitle','GUIDED TRAINING',0,171,740,36,29)
    e.label(training+'/CC_TrainingState','SOLO PRACTICE  /  CHOOSE A DRILL',0,133,730,28,17)
    for name,title,x,y in [('Serve','1  SERVE',-185,78),('Receive','2  RECEIVE',185,78),('Set','3  SET',-185,24),('Spike','4  SPIKE',185,24)]:
        e.button(training+'/CC_Train'+name,title,x,y,330,43,19)
    e.label(training+'/CC_TrainingHint','Gold ring: target. Blue ring: your starting spot.',0,-20,730,44,16)
    for name,title,x in [('Easy','EASY',-240),('Standard','STANDARD',0),('Challenge','CHALLENGE',240)]:
        e.button(training+'/CC_Train'+name,title,x,-63,205,33,17)
    e.label(training+'/CC_TrainDifficultyState','STANDARD  /  1.05m TARGET RADIUS',0,-104,730,25,16)
    e.button(training+'/CC_TrainBack','BACK',0,-160,225,36,17);e.active(root,False)
    stats,root=panel('CC_Stats')
    e.label(stats+'/CC_StatsTitle','MATCH STATS',0,170,740,36,29)
    e.label(stats+'/CC_StatsState','PLAY A MATCH TO SEE YOUR STATS',0,126,740,29,17)
    e.label(stats+'/CC_StatsMetrics','\nAces\nAttacks\nReceptions\nErrors\nContacts',-285,7,160,178,20)
    for name,title,x in [('You','YOU',-75),('Blue','BLUE',105),('Red','RED',280)]:
        t=e.label(stats+'/CC_Stats'+name,title+'\n0\n0\n0\n0\n0',x,7,160,178,20)
        e.color(t,{'You':(.98,.95,.87,1.),'Blue':(.40,.80,1.,1.),'Red':(1.,.48,.49,1.)}[name])
    e.label(stats+'/CC_StatsLongest','LONGEST RALLY  0.0s / 0 CONTACTS',0,-108,740,32,18)
    e.button(stats+'/CC_StatsDone','DONE',0,-165,220,36,18);e.active(root,False)
    rewards,root=panel('CC_Rewards')
    e.label(rewards+'/CC_RewardsTitle','SKILL COLLECTIONS',0,177,740,34,28)
    e.label(rewards+'/CC_RewardsState','Complete skills to unlock Sunset, Skyline and Emerald.',0,120,740,66,15)
    for name,title,y in [('Outfit','OUTFIT',65),('Face','EXPRESSION',5),('Accent','ACCENT',-55)]:
        e.label(rewards+'/CC_Reward'+name+'Title',title,-265,y,165,30,17)
        e.button(rewards+'/CC_Reward'+name+'Prev','<',-133,y,54,36,23)
        e.label(rewards+'/CC_Reward'+name+'Value','Base',82,y,305,31,20)
        e.button(rewards+'/CC_Reward'+name+'Next','>',330,y,54,36,23)
    e.label(rewards+'/CC_RewardsHint','Earned through skill. Your base style stays available.',0,-109,740,28,16)
    e.button(rewards+'/CC_RewardsDone','DONE',0,-164,220,36,18);e.active(root,False)
    e.button('Menu/Pages/Start/CC_StatsOpen','MATCH STATS',-120,-140,220,40,18)
    e.rect(e.find('Menu/Pages/Start/CC_CustomizeOpen'),120,-140,220,40)
    e.text(e.find('Menu/Pages/Start/CC_CustomizeOpen/Text'),'CUSTOMIZATION',17)
    e.button('Menu/Pages/InGame/CC_StatsOpen','MATCH STATS',-265,22,200,40,17)
    e.rect(e.find('Menu/Pages/InGame/CC_CustomizeOpen'),0,22,220,40)
    custom='Menu/CC_Customization';e.rect(e.find(custom),0,0,800,400)
    e.rect(e.find(custom+'/CC_CustomTitle'),0,174,740,34)
    e.rect(e.find(custom+'/CC_CustomHint'),0,140,740,24)
    e.rect(e.find(custom+'/CC_MirrorCaption'),-255,-142,220,25)
    e.button(custom+'/CC_RewardsOpen','SKILL COLLECTIONS',-255,-176,210,32,16)
    # Native Solo's Indoor control is relabeled TRAINING only on its first
    # offline format selector. It remains Indoor on the venue selector.
    # No duplicate practice start is added over a live pause/menu page.
    return dict(created_paths=e.created,panels=['Menu/CC_Training','Menu/CC_Stats','Menu/CC_Rewards'],panels_default_active=False,button_listener_count=0,canvas_bounds=[-400,400,-200,200],training_entry='Native SoloPage offset0x50: root runtime changes label/visibility by selector stage',changed_existing_ids=[i for i,b in before.items() if level0.objects[i].get_raw_data()!=b],new_objects=sorted(set(level0.objects)-set(before)))

def startup_wordmark_v29():
    im=Image.new('RGBA',(2048,1024),(0,0,0,0));d=ImageDraw.Draw(im)
    emblem=banner_art().crop((118,47,394,323)).convert('RGBA')
    mask=Image.new('L',emblem.size,0);ImageDraw.Draw(mask).ellipse((16,15,260,259),fill=255)
    emblem.putalpha(mask);emblem=emblem.resize((450,450),Image.Resampling.LANCZOS)
    im.alpha_composite(emblem,(220,260))
    fontpath=R/'assets/shared/fonts/CloudcourtBubble.ttf'
    size=166
    while True:
        font=ImageFont.truetype(str(fontpath),size)
        if d.textbbox((0,0),'CLOUDCOURT',font=font)[2]<1160:break
        size-=2
    d.text((1265,434),'CLOUDCOURT',font=font,anchor='mm',fill='#fff1dc',stroke_width=9,stroke_fill='#10223b')
    small=ImageFont.truetype(str(fontpath),46)
    d.text((1265,585),'BIG RALLIES. GOOD COMPANY.',font=small,anchor='mm',fill='#ffd34c',stroke_width=3,stroke_fill='#10223b')
    return im

def apply_startup_wordmark_v29(global_assets):
    before={i:o.get_raw_data() for i,o in global_assets.objects.items()}
    texture=global_assets.objects[3];old=texture.read();assert(old.m_Width,old.m_Height)==(2048,1024)
    image=startup_wordmark_v29();old.set_image(image,target_format=12,mipmap_count=1);old.m_Name='Cloudcourt VR Startup Wordmark v29';old.save();raw(texture,texture.data)
    changed=[i for i,b in before.items() if global_assets.objects[i].get_raw_data()!=b];assert changed==[3]
    A.mkdir(parents=True,exist_ok=True);image.save(A/'startup-wordmark-v29.png')
    preview=Image.new('RGB',image.size,'#08182c');preview.paste(image,mask=image.getchannel('A'));preview.save(A/'startup-wordmark-preview-v29.png')
    (A/'LICENSE.txt').write_text('Cloudcourt v29 menu/startup art\n\nThe startup image combines the original procedural Cloudcourt rising-cloud/volleyball emblem from build_art_v26.py with original lettering rendered using the existing CloudcourtBubble font. No original-game image or downloaded artwork is sampled. The procedural emblem and composition may be used, modified and redistributed with Cloudcourt under CC0-1.0. Preserve the existing font license if distributing that font binary; no font is copied here.\n',encoding='utf-8')
    return dict(changed_objects=changed,texture_id=3,pixels=[2048,1024],format='BC3 opaque-color/transparent-background',current_emblem_reused=True,main_menu_emblem_unchanged=True,preview=str(A/'startup-wordmark-preview-v29.png'))

if __name__=='__main__':
    import argparse,UnityPy
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R/'versions/cloudcourt-v28-antes-v29');p.add_argument('--output',type=Path,default=R/'visuals-v29-ui');a=p.parse_args()
    assert a.source.resolve()!=a.output.resolve() and 'working' not in a.output.resolve().parts
    a.output.mkdir(parents=True,exist_ok=True)
    menu=UnityPy.load(str(a.source/'level0')).file;global_assets=UnityPy.load(str(a.source/'globalgamemanagers.assets')).file
    report=dict(ui=apply_refinement_ui_v29(menu),startup=apply_startup_wordmark_v29(global_assets))
    (a.output/'level0').write_bytes(menu.save());(a.output/'globalgamemanagers.assets').write_bytes(global_assets.save())
    (a.output/'ui-v29-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
