"""Cloudcourt VR visual checkpoint, built from preserved v15-rostos files."""
from pathlib import Path
import sys,json,copy,struct,math,re,shutil
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import UnityPy
from UnityPy.files.ObjectReader import ObjectReader
from UnityPy.streams import EndianBinaryReader
_original_set_raw_data=ObjectReader.set_raw_data
def _set_readable_data(self,data):
 _original_set_raw_data(self,data)
 self.reader=EndianBinaryReader(data,endian=self.reader.endian);self.byte_start=0;self.byte_size=len(data)
ObjectReader.set_raw_data=_set_readable_data
BASE=R/'versions/v15-rostos-antes-puloviva';OUT=R/'visuals-v16';A=R/'assets/cloudcourt-v16';A.mkdir(exist_ok=True)
env=UnityPy.load(str(R/'working/VolleyballFever_Data'))
files={}
for name in ['resources.assets','sharedassets0.assets','sharedassets1.assets','sharedassets3.assets','level0','level1','level2','level3']:
 p=R/'characters-v16'/name if name in ['resources.assets','sharedassets0.assets'] else BASE/name
 f=UnityPy.load(str(p)).file;f.parent=env;files[name]=f
def ptr(i,f=0):return {'m_FileID':f,'m_PathID':i}
def vec(x,y,z):return {'x':float(x),'y':float(y),'z':float(z)}
def clone(dest,source,data=None):
 o=copy.copy(source);o.assets_file=dest;o.path_id=max(dest.objects)+1
 st=copy.deepcopy(source.serialized_type)
 if source.assets_file is not dest and st.script_type_index>=0:
  script=copy.deepcopy(source.assets_file.script_types[st.script_type_index])
  if script.local_serialized_file_index:
   script.local_serialized_file_index=external_index(source.assets_file,dest,script.local_serialized_file_index)
  try:st.script_type_index=dest.script_types.index(script)
  except ValueError:st.script_type_index=len(dest.script_types);dest.script_types.append(script)
 match=next((i for i,t in enumerate(dest.types) if t.class_id==source.class_id and t.script_type_index==st.script_type_index and getattr(t,'script_id',None)==getattr(st,'script_id',None)),None)
 if match is None:match=len(dest.types);dest.types.append(st)
 o.type_id=match;o.serialized_type=dest.types[match];
 o.set_raw_data(source.get_raw_data());dest.objects[o.path_id]=o
 if data is not None:o.save_typetree(data)
 return o.path_id
def hierarchy(f):
 gs={o.path_id:o.read_typetree() for o in f.objects.values() if o.type.name=='GameObject'};ts={o.path_id:o.read_typetree() for o in f.objects.values() if o.type.name in ['Transform','RectTransform']}
 def path(i):
  t=ts[i];p=t['m_Father']['m_PathID'];return (path(p)+'/' if p in ts else '')+gs[t['m_GameObject']['m_PathID']]['m_Name']
 return gs,ts,{path(i):i for i in ts}
def string_replace(raw,old,new):
 a=old.encode();b=new.encode();needle=struct.pack('<I',len(a))+a+b'\0'*((-len(a))%4);value=struct.pack('<I',len(b))+b+b'\0'*((-len(b))%4)
 return raw.replace(needle,value)
def ui_text(o,text,size=None):
 raw=o.get_raw_data();length=struct.unpack_from('<I',raw,128)[0];assert length<2000 and 132+length<=len(raw)
 end=132+((length+3)//4)*4;b=text.encode('utf-8');raw=bytearray(raw[:128]+struct.pack('<I',len(b))+b+b'\0'*((-len(b))%4)+raw[end:]);struct.pack_into('<4f',raw,44,.98,.95,.87,1)
 if size:struct.pack_into('<i',raw,84,size);struct.pack_into('<i',raw,100,max(size,28))
 o.set_raw_data(bytes(raw))
def tex(f,i,im):t=f.objects[i].read();t.set_image(im,mipmap_count=1);t.save()
def color(s):return dict(zip('rgba',[int(s[i:i+2],16)/255 for i in [1,3,5]]+[1.]))
def material(f,template,name,texture):
 d=copy.deepcopy(template.read_typetree());d['m_Name']=name;d['m_ShaderKeywords']='';d['m_SavedProperties']['m_TexEnvs']=[('_MainTex',{'m_Texture':ptr(texture),'m_Scale':dict(x=1.,y=1.),'m_Offset':dict(x=0.,y=0.)})];d['m_SavedProperties']['m_Colors']=[('_Color',color('#ffffff')),('_EmissionColor',color('#000000'))];return clone(f,template,d)
def texture_new(f,template,name,im):
 d=template.read_typetree();d['m_Name']=name;i=clone(f,template,d);tex(f,i,im);return i
def external_index(src,dst,index):
 if not index or src is dst:return index
 path=src.externals[index-1].path
 for i,e in enumerate(dst.externals):
  if e.path==path:return i+1
 dst.externals.append(copy.deepcopy(src.externals[index-1]));return len(dst.externals)
def clone_tree(src,dst,root,parent=0,name=None):
 gs,ts,_=hierarchy(src);ids=[]
 def collect(t):
  g=ts[t]['m_GameObject']['m_PathID'];ids.append(g)
  for c in gs[g]['m_Component']:ids.append(c['component']['m_PathID'])
  for c in ts[t]['m_Children']:collect(c['m_PathID'])
 collect(root);mapping={i:clone(dst,src.objects[i]) for i in dict.fromkeys(ids)}
 def remap(d):
  if isinstance(d,dict):
   if set(d)=={'m_FileID','m_PathID'} and d['m_FileID']==0 and d['m_PathID'] in mapping:return ptr(mapping[d['m_PathID']])
   return {k:remap(v) for k,v in d.items()}
  if isinstance(d,list):return [remap(v) for v in d]
  return d
 for i,j in mapping.items():
  old=src.objects[i];new=dst.objects[j]
  if old.type.name=='MonoBehaviour':
   raw=old.get_raw_data()
   for a,b in mapping.items():raw=raw.replace(struct.pack('<iq',0,a),struct.pack('<iq',0,b))
   # Common globalgamemanagers/sharedassets0 references have the same indexes.
   assert src.externals[0].path==dst.externals[0].path and src.externals[1].path==dst.externals[1].path
   if len(raw)>=88 and struct.unpack_from('<q',raw,20)[0]==572:
    raw=bytearray(raw);old_file=struct.unpack_from('<i',raw,72)[0];struct.pack_into('<i',raw,72,external_index(src,dst,old_file));raw=bytes(raw)
   new.set_raw_data(raw)
  else:new.save_typetree(remap(old.read_typetree()))
 rt=dst.objects[mapping[root]].read_typetree();rt['m_Father']=ptr(parent);dst.objects[mapping[root]].save_typetree(rt)
 if parent:
  d=dst.objects[parent].read_typetree();d['m_Children'].append(ptr(mapping[root]));dst.objects[parent].save_typetree(d)
 if name:
  g=mapping[ts[root]['m_GameObject']['m_PathID']];d=dst.objects[g].read_typetree();d['m_Name']=name;dst.objects[g].save_typetree(d)
 return mapping

# Repository-native mesh authoring definitions; avoid the old map generator's side effects.
scope={'__file__':str(R/'create_puloviva_characters.py')};source=(R/'create_puloviva_characters.py').read_text();exec(source[:source.index('MODELS=')],scope)
Model=scope['Model'];palette=Image.new('RGB',(1024,1024),'#f8efdc');dr=ImageDraw.Draw(palette)
for i,c in enumerate(['#f8efdc','#238fe0','#ff5967','#172b46','#ffcd58','#8de2dd','#d5dde5','#ffffff']):
 x=512+(i%4)*128;y=(i//4)*128;dr.rectangle((x,y,x+127,y+127),fill=c)
palette.save(A/'luvas-e-detalhes.png');rf=files['resources.assets'];tid=texture_new(rf,rf.objects[42],'Cloudcourt Detail Palette',palette);mat=material(rf,rf.objects[7],'Cloudcourt Soft Gloves',tid)
def static_mesh(m,name):return clone(rf,rf.objects[67],m.serialize(rf.objects[67].read_typetree(),name,False))
def visual(f,parent,name,meshid,materialid):
 # Clone ordinary renderer components, excluding colliders and scripts.
 go=rf.objects[246].read_typetree() if 246 in rf.objects else None
 gs,ts,paths=hierarchy(rf);template_t=next(i for i,t in ts.items() if any(rf.objects[c['component']['m_PathID']].type.name=='MeshFilter' for c in gs[t['m_GameObject']['m_PathID']]['m_Component']))
 template_g=gs[ts[template_t]['m_GameObject']['m_PathID']];newgo=copy.deepcopy(template_g);newgo['m_Name']=name;newgo['m_IsActive']=True;newgo['m_Component']=[];gid=clone(f,rf.objects[ts[template_t]['m_GameObject']['m_PathID']],newgo)
 tr=copy.deepcopy(ts[template_t]);tr['m_GameObject']=ptr(gid);tr['m_Father']=ptr(parent);tr['m_Children']=[];tr['m_LocalPosition']=vec(0,0,0);tr['m_LocalRotation']=dict(x=0.,y=0.,z=0.,w=1.);tr['m_LocalScale']=vec(1,1,1);trid=clone(f,rf.objects[template_t],tr);newgo['m_Component']=[{'component':ptr(trid)}]
 for typ in ['MeshFilter','MeshRenderer']:
  o=next(rf.objects[c['component']['m_PathID']] for c in template_g['m_Component'] if rf.objects[c['component']['m_PathID']].type.name==typ);d=o.read_typetree();d['m_GameObject']=ptr(gid)
  if typ=='MeshFilter':d['m_Mesh']=ptr(meshid)
  else:
   d['m_Materials']=[ptr(materialid)];d['m_Enabled']=True;d['m_StaticBatchInfo']=dict(firstSubMesh=0,subMeshCount=0);d['m_StaticBatchRoot']=ptr(0);d['m_LightmapIndex']=65535
  newgo['m_Component'].append({'component':ptr(clone(f,o,d))})
 f.objects[gid].save_typetree(newgo)
 if parent:
  d=f.objects[parent].read_typetree();d['m_Children'].append(ptr(trid));f.objects[parent].save_typetree(d)
 return trid
gs,ts,paths=hierarchy(rf)
for state in ['Open','Closed']:
 m=Model();m.softbox((0,0,.045),(.028,.060,.067),0,0);m.softbox((0,0,-.025),(.032,.066,.023),0,1)
 if state=='Open':
  for j,y in enumerate([-.046,-.015,.016,.047]):m.limb((0,y,.085),(0,y,.17+(1-abs(j-1.5)/2)*.035),.016,.018,0,0)
  m.limb((0,-.045,.025),(0,-.10,.09),.023,.024,0,0)
 else:
  m.softbox((0,0,.105),(.033,.059,.036),0,0);m.softbox((.018,-.048,.069),(.023,.023,.042),0,0)
 mid=static_mesh(m,'Cloudcourt '+state+' Glove')
 for p,t in list(paths.items()):
  if p.endswith('Hand Root L/'+state) or p.endswith('Hand Root R/'+state):visual(rf,t,'Cloudcourt '+state+' Glove',mid,mat)
for o in list(rf.objects.values()):
 if o.type.name=='SkinnedMeshRenderer':
  d=o.read_typetree();gid=d['m_GameObject']['m_PathID'];n=gs.get(gid,{}).get('m_Name','')
  if any(x in n for x in ['Pr_LowPolyHand','Pr_Hand']):d['m_Enabled']=False;o.save_typetree(d)
# MeshRenderer hand variants may coexist with skinned variants.
for p,t in paths.items():
 if 'Hand Root' in p and ('Pr_LowPolyHand' in p or 'Pr_Hand' in p):
  for c in gs[ts[t]['m_GameObject']['m_PathID']]['m_Component']:
   o=rf.objects[c['component']['m_PathID']]
   if o.type.name in ['SkinnedMeshRenderer','MeshRenderer']:d=o.read_typetree();d['m_Enabled']=False;o.save_typetree(d)
ants=Model()
for x in [-4.48,4.48]:
 for j in range(10):ants.softbox((x,2.4+.08*j+.04,0),(.018,.041,.018),0,2 if j%2==0 else 7)
mid=static_mesh(ants,'Cloudcourt visual antennas');field=paths['GameRules/Field-Regular-900x450'];visual(rf,field,'Cloudcourt Antennas - visual only',mid,mat)

# Additional wall banners and gold roof trim, without colliders.
decor=Model()
for side in [-1,1]:
 for z in [-14,-8,0,8,14]:
  decor.softbox((side*11.72,6.4,z),(.06,1.25,.55),0,1 if side<0 else 2)
  decor.softbox((side*11.6,7.8,z),(.10,.10,.68),0,4)
 decor.softbox((0,10,side*17.8),(10,.08,.06),0,4)
df=files['level3'];dm=clone(df,rf.objects[67],decor.serialize(rf.objects[67].read_typetree(),'Cloudcourt arena ribbons',False));dt=texture_new(df,rf.objects[42],'Cloudcourt Ribbon Palette',palette)
md=copy.deepcopy(rf.objects[mat].read_typetree());md['m_Shader']['m_FileID']=external_index(rf,df,md['m_Shader']['m_FileID']);md['m_SavedProperties']['m_TexEnvs'][0][1]['m_Texture']=ptr(dt);dmat=clone(df,rf.objects[mat],md);visual(df,0,'Cloudcourt Arena Banners',dm,dmat)

# Original UI font and rounded panel art.
f=files['sharedassets0.assets'];font=f.objects[188].read_typetree();font['m_Name']='Cloudcourt Bubble';font['m_FontData']=(A/'CloudcourtBubble.ttf').read_bytes();font['m_FontNames']=['Cloudcourt Bubble'];f.objects[188].save_typetree(font)
panel=Image.new('RGBA',(32,32),(0,0,0,0));d=ImageDraw.Draw(panel);d.rounded_rectangle((0,0,31,31),10,fill='#ffcf58');d.rounded_rectangle((2,2,29,29),8,fill='#172b46');panel.save(A/'menu-card.png');tex(f,71,panel)

# Court texture: UV bottom is negative world Z, therefore blue.
fontpath=A/'CloudcourtBubble.ttf';court=Image.new('RGB',(1536,1536),'#fa5b68');d=ImageDraw.Draw(court);d.rectangle((0,768,1536,1536),fill='#248fda')
for y in [0,512,768,1024,1530]:d.rectangle((0,y,1536,y+6),fill='#fff0d8')
for x in [0,1530]:d.rectangle((x,0,x+6,1536),fill='#fff0d8')
for y,title in [(285,'RED TEAM'),(1260,'BLUE TEAM')]:
 layer=Image.new('RGBA',court.size);ld=ImageDraw.Draw(layer);ld.text((768,y),'CLOUDCOURT',font=ImageFont.truetype(str(fontpath),104),fill='#fff1dc',anchor='mm');ld.text((768,y+100),title,font=ImageFont.truetype(str(fontpath),48),fill='#172b46',anchor='mm')
 if y<768:layer=layer.rotate(180);# Printed inward for the red team's viewpoint.
 # Keep the brand in its own half after rotating the lettering around its center.
 if y<768:
  layer=Image.new('RGBA',court.size);text=Image.new('RGBA',(1300,250));td=ImageDraw.Draw(text);td.text((650,80),'CLOUDCOURT',font=ImageFont.truetype(str(fontpath),104),fill='#fff1dc',anchor='mm');td.text((650,180),title,font=ImageFont.truetype(str(fontpath),48),fill='#172b46',anchor='mm');text=text.rotate(180);layer.paste(text,(118,160),text)
 court.paste(layer,(0,0),layer)
court.save(A/'quadra-azul-vermelha.png');tex(files['sharedassets3.assets'],13,court)
# Replace the old padding brand; the existing square post models remain.
pad=Image.new('RGB',(512,1024),'#172b46');d=ImageDraw.Draw(pad)
for j,ch in enumerate('CLOUDCOURT'):d.text((256,68+j*106),ch,font=ImageFont.truetype(str(fontpath),110),fill='#ffcf58',anchor='mm')
pad.save(A/'postes.png');tex(rf,42,pad)

# Menu layout and visible text. Keep technical Steam/Photon identifiers intact.
f=files['level0'];gs,ts,paths=hierarchy(f)
for p,t in paths.items():
 if '/Discord Button' in p or p=='Menu/Pages/Intro':g=gs[ts[t]['m_GameObject']['m_PathID']];g['m_IsActive']=False;f.objects[ts[t]['m_GameObject']['m_PathID']].save_typetree(g)
 for c in gs[ts[t]['m_GameObject']['m_PathID']]['m_Component']:
  o=f.objects[c['component']['m_PathID']]
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if len(raw)>=132 and struct.unpack_from('<q',raw,20)[0]==572:
   count=struct.unpack_from('<I',raw,128)[0]
   if count>3000 or 132+count>len(raw):continue
   text=raw[132:132+count].decode('utf-8');new=text
   for old in ['CAIOBA','Caioba','CaioBa','Houston','HOUSTON','Volleyball Fever']:new=new.replace(old,'CLOUDCOURT VR')
   if p.endswith('InRoom/Buttons/Team A Button/Text'):new='BLUE TEAM'
   if p.endswith('InRoom/Buttons/Team B Button/Text'):new='RED TEAM'
   if '/Intro/' in p:new=''
   if p.endswith('Start/Title'):new='CLOUDCOURT VR'
   ui_text(o,new,min(struct.unpack_from('<i',raw,84)[0],24))
  elif len(raw)>=124 and struct.unpack_from('<q',raw,20)[0]==1430:
   b=bytearray(raw);struct.pack_into('<4f',b,44,1.,1.,1.,1.);o.set_raw_data(bytes(b))
def move(t,x,y,w=190,h=34):
 d=f.objects[t].read_typetree();d['m_AnchoredPosition']=dict(x=float(x),y=float(y));d['m_LocalPosition']=vec(x,y,0);d['m_SizeDelta']=dict(x=float(w),y=float(h));f.objects[t].save_typetree(d)
move(paths['Menu/Pages/InGame/Resume Button'],0,134,200,36);move(paths['Menu/Pages/InGame/Leave Button'],0,-118,200,34)
for name,label,x,y in [('PuloTeams','CHANGE TEAMS',0,88),('PuloSkin0','COOL',-101,26),('PuloSkin1','NERD',101,26),('PuloSkin2','SMIRK',-101,-22),('PuloSkin3','GOOFY',101,-22)]:
 mapping=clone_tree(f,f,paths['Menu/Pages/InGame/Resume Button'],paths['Menu/Pages/InGame'],name);move(mapping[paths['Menu/Pages/InGame/Resume Button']],x,y,192 if name!='PuloTeams' else 200,36)
 ui_text(f.objects[mapping[1009]],label,14)

# Two large, live wall scoreboards. UI references use global/shared font files.
src=rf;dst=files['level3']
for index,z in enumerate([17.65,-17.65]):
 mapping=clone_tree(src,dst,1182,0,'CloudBoard'+str(index));root=mapping[1182];d=dst.objects[root].read_typetree();d['m_LocalPosition']=vec(0,6.8,z);d['m_AnchoredPosition']=dict(x=0.,y=6.8);d['m_LocalRotation']=dict(x=0.,y=float(index),z=0.,w=float(1-index));d['m_LocalScale']=vec(.013,.013,.013);d['m_SizeDelta']=dict(x=650.,y=240.);dst.objects[root].save_typetree(d)
 for old in [1174,1176,1180,1186]:
  g=dst.objects[mapping[src.objects[old].read_typetree()['m_GameObject']['m_PathID']]].read_typetree();g['m_IsActive']=False;dst.objects[mapping[src.objects[old].read_typetree()['m_GameObject']['m_PathID']]].save_typetree(g)
 ui_text(dst.objects[mapping[1241]],'<color=#75CFFF>00</color> : <color=#FF7278>00</color>',76)
 ui_text(dst.objects[mapping[1220]],'CLOUDCOURT VR',28)
 d=dst.objects[mapping[1188]].read_typetree();d['m_AnchoredPosition']=dict(x=0.,y=-10.);d['m_SizeDelta']=dict(x=640.,y=150.);dst.objects[mapping[1188]].save_typetree(d)
 d=dst.objects[mapping[1178]].read_typetree();d['m_AnchoredPosition']=dict(x=0.,y=76.);d['m_SizeDelta']=dict(x=620.,y=60.);dst.objects[mapping[1178]].save_typetree(d)

# Restore the v15 40 cm net raise onto the character generator's original rig baseline.
old=UnityPy.load(str(BASE/'resources.assets')).file
for ident,o in old.objects.items():
 if o.type.name!='Transform' or ident not in rf.objects:continue
 d=o.read_typetree();g=old.objects[d['m_GameObject']['m_PathID']].read_typetree()
 if 'Net' in g['m_Name']:
  now=rf.objects[ident].read_typetree();now['m_LocalPosition']=d['m_LocalPosition'];now['m_LocalScale']=d['m_LocalScale'];rf.objects[ident].save_typetree(now)
# Align scene net planes with the authoritative court center. Keep the height unchanged.
for scene in ['level1','level2','level3']:
 ff=files[scene];gg,tt,pp=hierarchy(ff)
 for ident,t in tt.items():
  if gg[t['m_GameObject']['m_PathID']]['m_Name']=='Net net' and abs(t['m_LocalPosition']['z'])>1:
   t['m_LocalPosition']['z']-=.0180001;ff.objects[ident].save_typetree(t)
# Main menu uses the two-column arrangement designed in Figma.
f=files['level0'];gs,ts,paths=hierarchy(f)
for path,x,y in [('Menu/Pages/Start/Solo Button',-112,30),('Menu/Pages/Start/Online Button',112,30),('Menu/Pages/Start/Settings Button',-112,-60),('Menu/Pages/Start/Quit Button',112,-60)]:
 if path in paths:move(paths[path],x,y,210,64)
for title,y,size in [('CLOUDCOURT VR',146,36),('Big rallies. Good company.',99,14)]:
 mapping=clone_tree(f,f,paths['Menu/Pages/InGame/Resume Button/Text'],paths['Menu/Pages/Start'],'Cloudcourt '+title);t=mapping[paths['Menu/Pages/InGame/Resume Button/Text']];move(t,0,y,700,48);ui_text(f.objects[mapping[1009]],title,size)

# Sync CurvedUI's serialized vertex colors with the edited Graphic colors.
f=files['level0'];gg,tt,pp=hierarchy(f)
for gid,g in gg.items():
 graphic=None;effects=[]
 for c in g['m_Component']:
  o=f.objects[c['component']['m_PathID']]
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if len(raw)<28:continue
  script=struct.unpack_from('<q',raw,20)[0]
  if script in (572,1430) and len(raw)>=60:graphic=raw[44:60]
  if script==465 and len(raw)==96:effects.append(o)
 if graphic:
  for o in effects:
   raw=bytearray(o.get_raw_data());raw[68:84]=graphic;o.set_raw_data(bytes(raw))

# Apply the menu hit-test and shared VR splash fixes to every fresh rebuild.
from fix_cloudcourt_menu_v16 import fix_menu_assets
files['globalgamemanagers.assets']=UnityPy.load(str(R/'working/VolleyballFever_Data/globalgamemanagers.assets')).file
fix_menu_assets(files['level0'],files['globalgamemanagers.assets'])

# Compact point message and scoreboard styling, including world-space variants.
for name,f in files.items():
 for o in list(f.objects.values()):
  if o.type.name in ['GameObject','Material','Mesh','Texture2D']:
   try:d=o.read_typetree()
   except Exception:continue
   if 'm_Name' in d and any(k in d['m_Name'] for k in ['Caioba','CAIOBA','Houston','HOUSTON']):d['m_Name']=re.sub('Caioba|CAIOBA|Houston|HOUSTON','Cloudcourt',d['m_Name']);o.save_typetree(d)
 if name=='resources.assets':
  for i in [1178,1175,1177]:
   if i not in f.objects:continue
   d=f.objects[i].read_typetree();d['m_LocalScale']=vec(.7,.7,.7);f.objects[i].save_typetree(d)
 (OUT/name).write_bytes(f.save())
report={'brand':'Cloudcourt VR','source':'v15-rostos','antennas_visual_only':True,'glove_models':['open','closed'],'menu_skin_buttons':4,'wall_scoreboards':2,'court_colors':{'negative_z':'blue','positive_z':'red'},'VR_tested':False}
(OUT/'cloudcourt-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
