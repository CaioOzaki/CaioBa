"""Read-only audit of integrated v21 assets against the immutable v20.1 backup.

Checks authorized unions independently, actual typed references and collision
mesh contents, plus cross-module material/hand/roof/bot contracts after reload.
"""
from pathlib import Path
import hashlib,json,struct,sys
from collections import Counter
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler
from fix_gloves_v16 import hierarchy
from build_bots_v20 import FAMILY
from build_customization_fix_v20 import mip_report
from build_english_v21 import inventory_visible_text,PORTUGUESE_MARKERS
BASE=R/'versions/cloudcourt-v20-1-antes-v21';CAND=R/'visuals-v21-integrated'
NAMES=['level0','level1','level2','level3','level4','resources.assets']+[f'sharedassets{i}.assets' for i in range(5)]
EXISTING_ALLOWED={
 'level0':{556,622,1143,1146,1153,1155,1156,1232},
 'level1':set(),'level2':set(),'level3':{164,199,262,280,316},
 'resources.assets':{5,6,7,8,40,629,638,665,666,699,792,797,1308,1312,1317,1321},
 'sharedassets0.assets':{74,77,78,79,80,83,86,87,91,93,96,98,99,104,105,107,108,111,112,113,114,115,116,117,119,120,122,123,124,126,127,128,130},
 'sharedassets1.assets':{3},'sharedassets3.assets':{3}}
ADDED_ALLOWED={'level0':set(range(1242,1301)),'level1':set(range(280,284)),'level2':set(range(318,322)),
 'level3':set(range(356,364)),'resources.assets':set(range(1333,1375)),'sharedassets1.assets':{68,69,70}}

def load(n,candidate=False):
    p=(CAND/n) if candidate and (CAND/n).exists() else BASE/n
    if not p.exists():p=R/'working/VolleyballFever_Data'/n
    return UnityPy.load(str(p)).file
def h(b):return hashlib.sha256(b).hexdigest()
def vertices(o):
    m=MeshHandler(o.read());m.process();return np.asarray(m.m_Vertices)
def pointers(d,path=''):
    if isinstance(d,dict):
        if set(d)=={'m_FileID','m_PathID'}:yield path,d
        else:
            for k,v in d.items():yield from pointers(v,path+'/'+k)
    elif isinstance(d,list):
        for i,v in enumerate(d):yield from pointers(v,path+'/'+str(i))

def main():
    metadata=json.loads((CAND/'build-report.json').read_text(encoding='utf8'))
    files={n:load(n,True) for n in NAMES};old={n:load(n) for n in NAMES}
    missing=[];opaque=[];files_report={};ref_count=0;colliders=0;collider_meshes=0;builtin_refs=[]
    def resolve(name,reference):
        if not reference['m_PathID']:return None,None
        target=name
        if reference['m_FileID']:
            f=files[name];fid=reference['m_FileID']
            assert 1<=fid<=len(f.externals),(name,'invalid external',reference)
            target=Path(f.externals[fid-1].path.replace('\\','/')).name
        if target not in files:
            p=BASE/target
            if not p.exists():p=R/'working/VolleyballFever_Data'/target
            if not p.exists():return target,None
            files[target]=UnityPy.load(str(p)).file
        return target,files[target].objects.get(reference['m_PathID'])
    for name in NAMES:
        f=files[name];b=old[name];assert set(b.objects)<=set(f.objects),('removed object',name)
        changed={i for i,o in b.objects.items() if o.get_raw_data()!=f.objects[i].get_raw_data()};added=set(f.objects)-set(b.objects)
        assert changed==EXISTING_ALLOWED.get(name,set()),('unauthorized changes',name,changed)
        assert added==ADDED_ALLOWED.get(name,set()),('unauthorized additions',name,added)
        assert not any('Collider' in f.objects[i].type.name or f.objects[i].type.name in ('Rigidbody','Animator','Animation') for i in added),('unexpected new physics/animation',name)
        if name in metadata['files']:
            row=metadata['files'][name];assert changed==set(row['changed']) and added==set(row['added'])
            assert h((CAND/name).read_bytes())==row['sha256']
        # Existing gameplay, animation, tracking, scripts and collision shapes.
        for i,o in b.objects.items():
            typ=o.type.name
            if 'Collider' in typ or typ in ('Rigidbody','PhysicMaterial','TerrainData','Shader','Animator','Animation','AnimationClip'):
                assert o.get_raw_data()==f.objects[i].get_raw_data(),('physics/animation changed',name,i,typ)
            if 'Collider' in typ:colliders+=1
            if typ=='MeshCollider':
                ref=o.read_typetree()['m_Mesh']
                if ref['m_PathID']:
                    target,obj=resolve(name,ref)
                    if obj is None:
                        assert target in ('unity default resources','unity_builtin_extra'),('unresolved collision mesh',name,i,target,ref)
                        builtin_refs.append(dict(file=name,id=i,target=target,reference=ref));continue
                    if target not in old:old[target]=load(target)
                    assert old[target].objects[obj.path_id].get_raw_data()==obj.get_raw_data(),('collision mesh content changed',name,i,target,obj.path_id)
                    collider_meshes+=1
            if typ=='Transform':
                a=o.read_typetree();c=f.objects[i].read_typetree()
                assert all(a[k]==c[k] for k in ('m_LocalPosition','m_LocalRotation','m_LocalScale','m_Father')),(name,i,'tracking/physics transform changed')
            if typ in ('MeshRenderer','SkinnedMeshRenderer') and i in changed:
                a=o.read_typetree();c=f.objects[i].read_typetree()
                assert {k for k in a if a[k]!=c[k]}=={'m_Materials'},('non-material renderer field changed',name,i)
        for i in changed|added:
            o=f.objects[i]
            if o.type.name=='MonoBehaviour':
                raw=o.get_raw_data();refs=[('/m_GameObject',dict(m_FileID=struct.unpack_from('<i',raw,0)[0],m_PathID=struct.unpack_from('<q',raw,4)[0])),('/m_Script',dict(m_FileID=struct.unpack_from('<i',raw,16)[0],m_PathID=struct.unpack_from('<q',raw,20)[0]))]
                if i in added:assert refs[1][1]['m_PathID'] in (463,572,1430,465,114),('new non-UI script',name,i,refs[1])
            else:refs=list(pointers(o.read_typetree()))
            for path,ref in refs:
                if not ref['m_PathID']:continue
                target,obj=resolve(name,ref);ref_count+=1
                if obj is None:
                    if target in ('unity default resources','unity_builtin_extra'):builtin_refs.append(dict(file=name,id=i,field=path,target=target,reference=ref))
                    else:missing.append(dict(file=name,id=i,field=path,target=target,reference=ref))
        files_report[name]=dict(changed=sorted(changed),added=sorted(added),objects=len(f.objects))
    assert not missing,('missing introduced references',missing)
    # Every renderer's mesh/material references must resolve to the right class.
    checked_renderers=0
    for name in NAMES:
        for i,o in files[name].objects.items():
            if o.type.name not in ('MeshFilter','MeshRenderer','SkinnedMeshRenderer'):continue
            d=o.read_typetree()
            if 'm_Mesh' in d and d['m_Mesh']['m_PathID']:
                target,obj=resolve(name,d['m_Mesh']);assert target in ('unity default resources','unity_builtin_extra') or obj is not None and obj.type.name=='Mesh',(name,i,'mesh reference')
            for ref in d.get('m_Materials',[]):
                if not ref['m_PathID']:continue
                target,obj=resolve(name,ref);assert target in ('unity default resources','unity_builtin_extra') or obj is not None and obj.type.name=='Material',(name,i,'material reference')
            checked_renderers+=1
    # All nine bot meshes and every material/renderer/rig remain v20.1 bytes.
    botfile=files['sharedassets0.assets'];b=old['sharedassets0.assets'];botmeshes=[];bot1textures=[]
    for i,o in b.objects.items():
        if o.type.name=='Mesh':
            assert o.get_raw_data()==botfile.objects[i].get_raw_data()
            if o.read_typetree()['m_Name'].startswith('Cloudcourt_Bot_'):botmeshes.append(i)
        if o.type.name in ('Material','Transform','SkinnedMeshRenderer','GameObject'):assert o.get_raw_data()==botfile.objects[i].get_raw_data()
        if o.type.name=='Material':
            d=o.read_typetree();name=d['m_Name']
            if name.startswith('SimpleCitizens_') and FAMILY[name.split('_')[1]]==0:
                ref=next(v['m_Texture'] for k,v in d['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex');assert ref['m_FileID']==0
                ident=ref['m_PathID'];bot1textures.append(ident);assert b.objects[ident].get_raw_data()==botfile.objects[ident].get_raw_data()
    assert len(botmeshes)==9 and bot1textures
    # Actual rendered roof uses its separate new visual mesh, not collider7.
    scene=files['level3'];roofref=scene.objects[199].read_typetree()['m_Mesh'];assert roofref==dict(m_FileID=0,m_PathID=356)
    roof=scene.objects[356];d=roof.read_typetree();v=vertices(roof);tri=np.frombuffer(bytes(d['m_IndexBuffer']),dtype='<u2').reshape(-1,3)
    surface=tri[d['m_SubMeshes'][0]['indexCount']//3:];normals=np.cross(v[surface[:,1]]-v[surface[:,0]],v[surface[:,2]]-v[surface[:,0]])
    nondeg=surface[np.linalg.norm(normals,axis=1)>1e-5]
    assert len(nondeg)==12
    # Reversing a quad legitimately changes its internal diagonal. Compare
    # signed area coverage of each geometric plane rather than triangle IDs.
    for sign in (-1,1):
        roofplane=[t for t in nondeg if np.all(sign*v[t,0]>=-1e-5) and not np.allclose(v[t,2],18) and not np.allclose(v[t,2],-18)]
        assert len(roofplane)==4
        p=v[roofplane];ns=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0])
        assert np.allclose(ns.sum(axis=0),0,atol=1e-4) and (ns[:,1]>0).sum()==2 and (ns[:,1]<0).sum()==2
    for z in (-18.,18.):
        gables=[t for t in nondeg if np.allclose(v[t,2],z)];assert len(gables)==2
        assert np.max(v[gables,1])>16 and np.min(v[gables,1])<14
        p=v[gables];ns=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);assert np.allclose(ns.sum(axis=0),0,atol=1e-4)
    assert scene.objects[224].read_typetree()['m_Mesh']==dict(m_FileID=0,m_PathID=7)
    assert scene.objects[7].get_raw_data()==old['level3'].objects[7].get_raw_data()
    # Opaque static palm and one-draw skyline resolve to actual Standard shader.
    palm=files['sharedassets1.assets'].objects[3].read_typetree();target,shader=resolve('sharedassets1.assets',palm['m_Shader'])
    assert shader.read_typetree()['m_ParsedForm']['m_Name']=='Standard' and not palm['m_ShaderKeywords']
    skyline=files['sharedassets1.assets'].objects[68].read_typetree();assert len(skyline['m_SubMeshes'])==1 and len(skyline['m_IndexBuffer'])//6==1572
    for name in ('level1','level2'):
        gs,ts,ps=hierarchy(files[name]);t=ps['Cloudcourt Orla Skyline'];go=gs[ts[t]['m_GameObject']['m_PathID']]
        rend=next(files[name].objects[c['component']['m_PathID']] for c in go['m_Component'] if files[name].objects[c['component']['m_PathID']].type.name=='MeshRenderer')
        assert len(rend.read_typetree()['m_Materials'])==1
    # Scoreboard board slots resolve to plain black/white and image overlays off.
    for i,expected in ((358,0.),(359,1.)):
        mat=scene.objects[i].read_typetree();c=dict(mat['m_SavedProperties']['m_Colors'])['_Color']
        assert max(c[k] for k in ('r','g','b'))<.04 if expected==0 else all(c[k]==1 for k in ('r','g','b'))
    assert scene.objects[280].get_raw_data()[12]==scene.objects[316].get_raw_data()[12]==0
    board=scene.objects[357].read_typetree();extent=board['m_LocalAABB']['m_Extent'];assert abs(extent['x']-extent['y'])<1e-6
    resource=files['resources.assets']
    for i in (7,8):
        d=resource.objects[i].read_typetree();assert all(not val['m_Texture']['m_PathID'] for _,val in d['m_SavedProperties']['m_TexEnvs'])
        assert max(dict(d['m_SavedProperties']['m_Colors'])['_Color'][k] for k in ('r','g','b'))<.03
    for i in (5,6):assert dict(resource.objects[i].read_typetree()['m_SavedProperties']['m_Colors'])['_Color']==dict(r=1.,g=1.,b=1.,a=1.)
    # No repainted branding/detail atlas shared with player or glove artwork.
    assert resource.objects[42].get_raw_data()==old['resources.assets'].objects[42].get_raw_data()
    ball=resource.objects[40].read();assert ball.m_TextureFormat==3 and ball.m_MipCount==11
    from build_environment_v21 import ball_art
    assert np.array_equal(np.asarray(ball.image),np.asarray(ball_art())),'Ball must be our lettering-free original art'
    for ident in metadata['bots']['changed_object_ids']:
        t=botfile.objects[ident].read();assert (t.m_Width,t.m_Height,t.m_TextureFormat,t.m_MipCount)==(1024,1024,3,11)
        assert t.image.convert('RGBA').getextrema()[3]==(255,255)
    # Avatar neutral texture and player atlases retain opaque mip contents after
    # environment edits; four new hand meshes bind only the neutral hand mat.
    hands=metadata['hands'];mat=resource.objects[hands['material']].read_typetree()
    assert dict(mat['m_SavedProperties']['m_TexEnvs'])['_MainTex']['m_Texture']==dict(m_FileID=0,m_PathID=hands['texture'])
    for ident in (hands['texture'],1329,1330):
        t=resource.objects[ident].read();levels=mip_report(t);assert all(m['alpha_min']==255 for m in levels);opaque.append(dict(texture=ident,mip_levels=len(levels)))
    gs,ts,ps=hierarchy(resource)
    for tid in hands['hand_visuals']+hands['bot_visuals']:
        go=gs[ts[tid]['m_GameObject']['m_PathID']];assert not go['m_IsActive']
        assert {resource.objects[c['component']['m_PathID']].type.name for c in go['m_Component']}=={'Transform','MeshFilter','MeshRenderer'}
    rows=inventory_visible_text({n:files[n] for n in NAMES});assert len(rows)==119 and not [r for r in rows if PORTUGUESE_MARKERS.search(r['text'])]
    result=dict(passed=True,candidate=str(CAND),exact_authorized_unions=True,files=files_report,
      introduced_references_checked=ref_count,missing_references=missing,typed_renderer_references_checked=checked_renderers,
      engine_builtin_references=builtin_refs,
      unchanged_colliders=colliders,unchanged_collider_referenced_meshes=collider_meshes,
      physics_animation_tracking_unchanged=True,bot_meshes_exact=botmeshes,bot1_texture_ids_exact=sorted(set(bot1textures)),
      roof_new_visual_mesh=356,roof_collider_mesh_unchanged=7,gables_filled_and_double_sided=True,
      palms_static_standard_shader=True,skyline_one_opaque_draw=True,scoreboard_square_white_with_black_border=True,
      posts_untextured_black_without_branding=True,net_tapes_plain_white=True,ball_original_art_no_text_or_logo=True,
      avatar_opaque_mips=opaque,visible_english_text_fields=len(rows),cross_module_conflicts=[],
      scope='Reloaded candidate asset audit only; no live install, Quest/headset or two-PC playtest.')
    (R/'analysis/v21-integration-assets.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','engine_builtin_references')},indent=2))

if __name__=='__main__':main()
