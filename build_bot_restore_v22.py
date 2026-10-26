"""Recover four historical authored looks without regenerating their faces.

v21 face pixels already matched the pre-v20 artwork, but its new scalp/hair
silhouette did not. Restore the exact historical mesh as well as the face and
hair palette; preserve the approved scout outfit and black tee/beige trousers.
"""
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy,numpy as np
from PIL import Image,ImageDraw,ImageFont
from build_bots_v20 import FAMILY,put,authoring
from build_environment_v21 import set_rgb_full_mips
PROFILES={1:'Curly',2:'Nerd',5:'Grandpa',6:'Side Quiff'}
BASE=R/'versions/cloudcourt-v19-antes-v20/sharedassets0.assets'

def bindings(file):
    result={}
    for o in file.objects.values():
        if o.type.name!='Material':continue
        d=o.read_typetree();name=d['m_Name']
        if not name.startswith('SimpleCitizens_'):continue
        n=FAMILY[name.split('_')[1]]
        if n not in PROFILES:continue
        p=next(v['m_Texture'] for k,v in d['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
        assert p['m_FileID']==0
        result[p['m_PathID']]=n
    return result

def build_bot_restore_v22(file,output=None):
    old=UnityPy.load(str(BASE)).file
    before={i:o.get_raw_data() for i,o in file.objects.items()}
    texture_map=bindings(file);oldmap=bindings(old);mesh_ids=[];renderer_ids=[];heads={};atlases={}
    for n,name in PROFILES.items():
        mesh=next(o for o in file.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==f'Cloudcourt_Bot_{n+1}')
        prior=next(o for o in old.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==f'Cloudcourt_Bot_{n+1}')
        nowtree=mesh.read_typetree();tree=prior.read_typetree()
        # The historical change is the hair after the common body/head region.
        stride=len(tree['m_VertexData']['m_DataSize'])//tree['m_VertexData']['m_VertexCount']
        assert len(nowtree['m_VertexData']['m_DataSize'])//nowtree['m_VertexData']['m_VertexCount']==stride
        assert nowtree['m_VertexData']['m_DataSize'][:6194*stride]==tree['m_VertexData']['m_DataSize'][:6194*stride],name
        assert nowtree['m_BindPose']==tree['m_BindPose'] and nowtree['m_BoneNameHashes']==tree['m_BoneNameHashes']
        mesh.set_raw_data(prior.get_raw_data())
        from build_bots_v20 import readable
        readable(mesh);mesh_ids.append(mesh.path_id)
        for o in file.objects.values():
            if o.type.name!='SkinnedMeshRenderer':continue
            d=o.read_typetree()
            if d['m_Mesh']==dict(m_FileID=0,m_PathID=mesh.path_id):
                d['m_AABB']=copy.deepcopy(tree['m_LocalAABB']);put(o,d);renderer_ids.append(o.path_id)
        target_ids=[i for i,p in texture_map.items() if p==n]
        source_id=next(i for i,p in oldmap.items() if p==n)
        historical=old.objects[source_id].read().image.convert('RGB')
        assert historical.size==(1024,1024)
        for ident in target_ids:
            image=file.objects[ident].read().image.convert('RGB');body=np.array(image)[512:,:,:].copy()
            image.paste(historical.crop((0,0,512,512)),(0,0))
            image.paste(historical.crop((512,128,768,256)),(512,128))
            assert np.array_equal(np.array(image)[512:,:,:],body)
            tex=file.objects[ident].read();set_rgb_full_mips(tex,image);tex.save()
            from build_bots_v20 import readable
            readable(file.objects[ident]);atlases[n]=image
        heads[name]=hashlib.sha256(historical.crop((0,0,512,512)).tobytes()).hexdigest()
    changed=sorted(i for i,o in file.objects.items() if o.get_raw_data()!=before[i])
    assert set(changed)<=set(mesh_ids+renderer_ids+list(texture_map))
    report=dict(profiles=PROFILES,mesh_ids=mesh_ids,renderer_ids=renderer_ids,
                texture_ids=sorted(texture_map),head_pixel_sha256=heads,changed=changed,
                exact_historical_hair_mesh=True,body_6194_vertices_exact=True,
                approved_outfits_preserved=True,physics_and_bones_preserved=True)
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        scope=authoring();gallery=Image.new('RGB',(1200,1220),'#e4ebed');draw=ImageDraw.Draw(gallery)
        font=ImageFont.truetype(str(R/'assets/cloudcourt-v16/CloudcourtBubble.ttf'),24)
        for j,(n,name) in enumerate(PROFILES.items()):
            model=scope['legacy_character_v19'](n)
            atlas=atlases[n];atlas.save(output/f'bot-{n+1:02}-atlas.png')
            im=scope['render_model'](model,atlas,550);im.save(output/f'bot-{n+1:02}-restored.png')
            x=(j%2)*600;y=(j//2)*610;gallery.paste(im,(x+25,y));draw.text((x+300,y+572),name,font=font,fill='#172b46',anchor='mm')
        gallery.save(output/'restored-bots.png');(output/'restoration.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    out=R/'visuals-v22-bots';f=UnityPy.load(str(R/'versions/cloudcourt-v21-antes-v22/sharedassets0.assets')).file
    report=build_bot_restore_v22(f,out);(out/'sharedassets0.assets').write_bytes(f.save());print(json.dumps(report,indent=2))
