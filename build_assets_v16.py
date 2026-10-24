"""Reproducible asset-only candidate built from verified v15 input. Never writes installation."""
import sys,json,copy,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from PIL import Image
from cartoon_font_v16 import make_font
ROOT=Path(os.environ.get('VOLLEY_RIOT_GAME_DIRECTORY',r'C:\Program Files (x86)\Steam\steamapps\common\Volleyball'))/'VolleyballFever_Data'
BASE=R/'visuals-v16';ART=R/'assets/volley-riot-v16';DEST=BASE/'VolleyballFever_Data';DEST.mkdir(parents=True,exist_ok=True)
G=TypeTreeGenerator(UnityPy.load(str(ROOT/'level0')).file.unity_version)
G.load_local_dll_folder(str(R/'tools/dump/DummyDll'))
ENVS={};changes=[]
EXPECTED={'resources.assets': '8e1859c53851a4ab648689604a28623ed472549b1b1812ed9320cee9b5b6c190', 'sharedassets3.assets': 'e26590efba15f25deefc000aade0e39c84ece7a51ffbacd40e69151d1c4ac0be', 'globalgamemanagers.assets': '28343ec56ca06085c66702d7da42bf156e055b6073e0eb4cabfdcb013c2f464c', 'sharedassets0.assets': '8afcd89656b39ff310a819dba1a4b7dcb3b440223708578070b68c8f1452dc0b', 'level0': '8e35b9ce80f0181b7d592e21dc6ad8ff32e68af177c788a004f4b59e25b0a5a1', 'level1': '52a520a1c1f945e582b35e6ff7ee909ac0f171edd7bc3133b5c3468b3cb0daf6', 'level2': 'c36b6ea4b16d2a883a2a399816f8ea594d651ced5116ced30aab58e26e9d1227', 'level3': '95d0adc51fead74a776a12f141b4d9eb4a89c6c9adc736877ccd776ae942d2bc'}
def load(f):
 if f not in ENVS:
  assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==EXPECTED[f], (f,'Use the verified v15 rostos baseline')
  e=UnityPy.load(str(ROOT/f));e.typetree_generator=G;ENVS[f]=e
 return ENVS[f].file
def read(f,p):return load(f).objects[p].read_typetree()
def put(f,p,d,reason):
 o=load(f).objects[p]; before=o.get_raw_data();old=o.read_typetree();o.save_typetree(old)
 assert o.get_raw_data()==before,('roundtrip failure',f,p)
 o.save_typetree(d);changes.append({'file':f,'id':p,'reason':reason})
def clone(f,p,d):
 af=load(f);n=max(af.objects)+1;o=copy.copy(af.objects[p]);o.path_id=n;o.data=None;af.objects[n]=o;o.save_typetree(d);return n
def ptr(p,f=0):return {'m_FileID':f,'m_PathID':p}
def color(hexv,a=1):return dict(zip(('r','g','b','a'),[int(hexv[i:i+2],16)/255 for i in (0,2,4)]+[a]))
NAVY=color('10233f');CREAM=color('fff5dc');RED=color('e74750');BLUE=color('2468df')
def texture(f,p,path):
 o=load(f).objects[p];t=o.read();im=Image.open(path)
 # Resize solely for the original UV asset resolution; no creative image edits.
 im=im.resize((t.m_Width,t.m_Height),Image.Resampling.LANCZOS)
 t.set_image(im,target_format=4 if im.mode=='RGBA' else 3);t.m_Name='Volley Riot / '+t.m_Name;t.save()
 changes.append({'file':f,'id':p,'reason':'new Volley Riot texture'})
texture('resources.assets',42,ART/'post-pad.png')
texture('resources.assets',52,ART/'net-tape.png')
texture('sharedassets3.assets',13,ART/'court.png')
texture('globalgamemanagers.assets',3,ART/'logo.png')
from repair_hair_v16 import repaired_model
hair=repaired_model()
put('sharedassets0.assets',4325,hair.serialize(read('sharedassets0.assets',4325),'Volley Riot Long Hair'),'continuous rear hair coverage')
from make_hands_v16 import glove
for side,pid in enumerate([69,70]):put('resources.assets',pid,glove(read('resources.assets',pid),side),'authored rounded glove with articulated fingers')
glove_tex=clone('resources.assets',40,read('resources.assets',40))
texture('resources.assets',glove_tex,ART/'glove-fabric.png')
hand_material=read('resources.assets',14)
hand_material['m_Name']='Volley Riot fabric glove'
hand_material['m_SavedProperties']['m_TexEnvs']=[('_MainTex',{'m_Texture':ptr(glove_tex),'m_Scale':{'x':1.,'y':1.},'m_Offset':{'x':0.,'y':0.}})]
hand_material['m_SavedProperties']['m_Colors']=[('_Color',color('ffffff'))]
hand_material['m_SavedProperties']['m_Floats']=[(k,.15 if k=='_Glossiness' else v) for k,v in hand_material['m_SavedProperties']['m_Floats']]
put('resources.assets',14,hand_material,'new glove fabric and matte finish')

# Keep the known-working native legacy font for VR menus. Lilita One is used
# by the static SDF score and point-message fonts below.
atlas,glyphs,chars,legacy,ascent,descent=make_font(ART/'LilitaOne-Regular.ttf')
atlas.save(ART/'LilitaOne-SDF.png')
atlas_alpha=Image.new('RGBA',atlas.size,(255,255,255,255));atlas_alpha.putalpha(atlas)
for ff in ['sharedassets0.assets','resources.assets']:
 af=load(ff)
 for obj in list(af.objects.values()):
  if obj.type.name!='MonoBehaviour':continue
  try:fd=obj.read_typetree()
  except Exception:continue
  if 'm_GlyphTable' not in fd:continue
  tid=fd['m_AtlasTextures'][0]['m_PathID'];assert fd['m_AtlasTextures'][0]['m_FileID']==0
  td=af.objects[tid].read();td.set_image(atlas_alpha,target_format=1);td.m_Name='Lilita One SDF Atlas';td.save()
  fd['m_Name']='Lilita One SDF';fd['m_GlyphTable']=glyphs;fd['m_CharacterTable']=chars;fd['m_glyphInfoList']=legacy
  fd['m_AtlasWidth']=1024;fd['m_AtlasHeight']=1024;fd['m_AtlasPadding']=6;fd['m_AtlasPopulationMode']=0
  fd['m_FaceInfo'].update(m_FamilyName='Lilita One',m_PointSize=44,m_LineHeight=float(ascent+descent),m_AscentLine=float(ascent),m_CapLine=32.,m_DescentLine=float(-descent),m_MeanLine=24.)
  fd['m_fontInfo'].update(Name='Lilita One',PointSize=44.,CharacterCount=len(chars),LineHeight=float(ascent+descent),Ascender=float(ascent),CapHeight=32.,Descender=float(-descent),AtlasWidth=1024.,AtlasHeight=1024.,Padding=6.)
  fd['m_KerningTable']={'kerningPairs':[]};fd['m_FontFeatureTable']={'m_GlyphPairAdjustmentRecords':[]}
  put(ff,obj.path_id,fd,'static cartoon SDF font with Latin-1 accents')
  matid=fd['material']['m_PathID'];mat=read(ff,matid)
  mat['m_SavedProperties']['m_Floats']=[(k,1024. if k in ['_TextureWidth','_TextureHeight'] else 7. if k=='_GradientScale' else v) for k,v in mat['m_SavedProperties']['m_Floats']]
  put(ff,matid,mat,'SDF atlas metrics')
for f in ['level0','resources.assets','sharedassets0.assets','level1','level2','level3','sharedassets3.assets']:
 af=load(f)
 for o in list(af.objects.values()):
  if o.type.name not in ['GameObject','MonoBehaviour','Material','Mesh']:continue
  try:d=o.read_typetree()
  except Exception:continue
  changed=False
  if 'm_Name' in d and 'caioba' in d['m_Name'].lower():
   import re
   d['m_Name']=re.sub('caioba','Volley Riot',d['m_Name'],flags=re.I);changed=True
  if o.type.name=='GameObject' and 'Discord' in d['m_Name']:
   d['m_IsActive']=False;changed=True
  if 'm_Text' in d:
   for a,b in [('Play','PLAY'),('Resume','RESUME'),('Leave','LEAVE'),('Settings\n','OPTIONS')]:
    if d['m_Text']==a:d['m_Text']=b
   for a,b in [('Join Team A','TIME VERMELHO'),('Join Team B','TIME AZUL'),('Team 1','Time Vermelho'),('Team 2','Time Azul')]:d['m_Text']=d['m_Text'].replace(a,b)
   if 'Discord' in d['m_Text']:d['m_Text']=''
   if 'm_FontData' in d:
    fid=0 if f=='sharedassets0.assets' else next((i+1 for i,x in enumerate(af.externals) if x.path=='sharedassets0.assets'),None)
    if fid is not None:d['m_FontData']['m_Font']=ptr(188,fid)
   d['m_Color']=CREAM.copy();changed=True
  if f=='level0' and 'm_Colors' in d and 'm_NormalColor' in d['m_Colors']:
   d['m_Colors'].update(m_NormalColor=NAVY.copy(),m_HighlightedColor=BLUE.copy(),m_PressedColor=RED.copy(),m_SelectedColor=BLUE.copy());changed=True
  if f=='level0' and 'm_Sprite' in d and 'm_Color' in d:
   gd=read(f,d['m_GameObject']['m_PathID']);name=gd['m_Name'].lower()
   if name in ['background','panel']:d['m_Color']={**NAVY,'a':.96};changed=True
  if 'm_text' in d:
   d['m_fontStyle']=0
   if d['m_text'] not in ['0 - 0','']:
    d['m_fontSize']*=0.65;d['m_fontSizeBase']=d['m_fontSize']
   changed=True
  if 'characterParent' in d:
   pid=d['characterParent']['m_PathID'];tr=read(f,pid);tr['m_LocalScale']['y']*=1.10
   put(f,pid,tr,'bot visual height +10%')
  if changed:put(f,o.path_id,d,'identity, UI typography or subtle point message')

from menu_visibility_v16 import apply_menu_visibility
changes.append({'file':'level0','reason':'high-contrast menu and CurvedUI cache synchronization',**apply_menu_visibility(load('level0'))})

# Antennas are segmented visual cubes, without ANY collider or rule component.
f='sharedassets3.assets';mats=[]
for label,c in [('red',RED),('cream',CREAM),('navy',NAVY),('blue',BLUE)]:
 d=read(f,5);d['m_Name']='Volley Riot / '+label
 d['m_SavedProperties']['m_Colors']=[('_Color',c),('_EmissionColor',{**c,'r':c['r']*.16,'g':c['g']*.16,'b':c['b']*.16})]
 mats.append(clone(f,5,d))
f='level3'
def cube(name,pos,scale,material):
 go=read(f,35);go['m_Name']=name;go['m_Layer']=0;go['m_Component']=[];gid=clone(f,35,go)
 tr=read(f,101);tr.update(m_GameObject=ptr(gid),m_Father=ptr(0),m_Children=[],m_LocalPosition=dict(zip('xyz',pos)),m_LocalScale=dict(zip('xyz',scale)));tid=clone(f,101,tr)
 mf=read(f,197);mf['m_GameObject']=ptr(gid);mid=clone(f,197,mf)
 mr=read(f,162);mr.update(m_GameObject=ptr(gid),m_Enabled=True,m_Materials=[ptr(material,4)]);rid=clone(f,162,mr)
 go['m_Component']=[{'component':ptr(p)} for p in [tid,mid,rid]];put(f,gid,go,'visual detail without collision')
 return gid
for x in [-4.5,4.5]:
 for i in range(16):cube('Volley Riot antenna', (x,1.75+i*.10,0),(.025,.10,.025),mats[i%2])
# Wall protection bands and team accents, outside the playable court.
for z,mat in [(-12.6,mats[0]),(12.6,mats[3])]:
 cube('Volley Riot team wall stripe',(0,2.3,z),(14,.12,.045),mat)
 cube('Volley Riot scoreboard backing',(0,4.6,z),(8.2,1.5,.12),mats[2])
 cube('Volley Riot scoreboard team edge',(0,5.35,z),(8.2,.10,.14),mat)
 for x in [-6.2,6.2]:cube('Volley Riot wall accent',(x,3.1,z),(.22,1.5,.045),mat)

# The two beach scenes share the same centered court. Transfer only native
# visual components; no colliders, scripts or rules are copied.
resource_mats=[]
for label,c in [('red',RED),('cream',CREAM)]:
 d=read('resources.assets',7);d['m_Name']='Volley Riot antenna '+label
 d['m_SavedProperties']['m_TexEnvs']=[];d['m_SavedProperties']['m_Colors']=[('_Color',c)]
 resource_mats.append(clone('resources.assets',7,d))
def transfer(target,source_id,d):
 af=load(target);src=load('level3').objects[source_id];idx=next(i for i,t in enumerate(af.types) if t.class_id==src.serialized_type.class_id)
 n=max(af.objects)+1;o=copy.copy(src);o.assets_file=af;o.path_id=n;o.type_id=idx;o.serialized_type=af.types[idx];o.data=None;af.objects[n]=o;o.save_typetree(d);return n
for target in ['level1','level2']:
 af=load(target);builtin=next(i+1 for i,x in enumerate(af.externals) if x.path.endswith('unity default resources'))
 if not any(x.path=='resources.assets' for x in af.externals):af.externals.append(copy.copy(next(x for x in load('level3').externals if x.path=='resources.assets')))
 resources=next(i+1 for i,x in enumerate(af.externals) if x.path=='resources.assets')
 for x in [-4.5,4.5]:
  for i in range(16):
   go=read('level3',35);go.update(m_Name='Volley Riot antenna',m_Layer=0,m_Component=[]);gid=transfer(target,35,go)
   tr=read('level3',101);tr.update(m_GameObject=ptr(gid),m_Father=ptr(0),m_Children=[],m_LocalPosition=dict(x=x,y=1.75+i*.10,z=0.),m_LocalScale=dict(x=.025,y=.10,z=.025));tid=transfer(target,101,tr)
   mf=read('level3',197);mf.update(m_GameObject=ptr(gid),m_Mesh=ptr(10202,builtin));mid=transfer(target,197,mf)
   mr=read('level3',162);mr.update(m_GameObject=ptr(gid),m_Enabled=True,m_Materials=[ptr(resource_mats[i%2],resources)],m_StaticBatchInfo=dict(firstSubMesh=0,subMeshCount=0));rid=transfer(target,162,mr)
   go['m_Component']=[{'component':ptr(p)} for p in [tid,mid,rid]];put(target,gid,go,'visual-only beach antenna')

manifest=[]
for f,e in ENVS.items():
 if not e.file.is_changed:continue
 blob=e.file.save();(DEST/f).write_bytes(blob)
 # Reopen all changed serialized files and read each native object.
 check=UnityPy.load(blob)
 assert len(check.file.objects)==len(e.file.objects),(f,'object count')
 for o in check.file.objects.values():
  if o.type.name in ['GameObject','Transform','RectTransform','MeshRenderer','MeshFilter','Texture2D','Font','Material']:o.read_typetree()
 manifest.append({'path':'VolleyballFever_Data/'+f,'before':hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),'after':hashlib.sha256(blob).hexdigest(),'objects':len(e.file.objects)})
 print('verified',f,len(blob),flush=True)
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(R/'analysis/v16-asset-changes.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
print('changes',len(changes))
