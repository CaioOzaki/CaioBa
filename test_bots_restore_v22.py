"""Isolated four-profile historical mesh/face restoration contracts for v22."""
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from build_bot_restore_v22 import build_bot_restore_v22,bindings,PROFILES,BASE
from build_environment_v21 import snapshot,delta
H=lambda b:hashlib.sha256(b).hexdigest()

def mesh_for(f,n):
    return next(o for o in f.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']==f'Cloudcourt_Bot_{n+1}')

def validate():
    src=R/'versions/cloudcourt-v21-antes-v22/sharedassets0.assets'
    before=UnityPy.load(str(src)).file;f=UnityPy.load(str(src)).file;historical=UnityPy.load(str(BASE)).file
    report=build_bot_restore_v22(f);texmap=bindings(f);oldmap=bindings(historical);rows=[]
    assert set(before.objects)==set(f.objects),'Object count/hierarchy must be preserved'
    whitelist=set(report['mesh_ids']+report['renderer_ids']+report['texture_ids'])
    for i,o in before.objects.items():
        if i not in whitelist:assert o.get_raw_data()==f.objects[i].get_raw_data(),('non-targeted object changed',i,o.type.name)
    for n,label in PROFILES.items():
        new=mesh_for(f,n);old=mesh_for(historical,n);base=mesh_for(before,n)
        a=new.read_typetree();b=base.read_typetree();h=old.read_typetree()
        assert new.get_raw_data()==old.get_raw_data(),(label,'historical mesh bytes')
        stride=len(h['m_VertexData']['m_DataSize'])//h['m_VertexData']['m_VertexCount'];assert stride>=48
        assert a['m_VertexData']['m_DataSize'][:6194*stride]==b['m_VertexData']['m_DataSize'][:6194*stride],(label,'body/head vertex streams altered')
        # Body/head triangles remain the same; differing suffix is the actual hair.
        def body_indices(d):
            dtype='<u2' if d['m_IndexFormat']==0 else '<u4';ix=np.frombuffer(bytes(d['m_IndexBuffer']),dtype=dtype).reshape(-1,3)
            return ix[np.all(ix<6194,axis=1)]
        assert np.array_equal(body_indices(a),body_indices(b)),(label,'body/head topology altered')
        for key in ['m_BindPose','m_BoneNameHashes','m_RootBoneNameHash']:
            assert a.get(key)==b.get(key)==h.get(key),(label,key)
        rendered=[]
        for i,o in f.objects.items():
            if o.type.name!='SkinnedMeshRenderer':continue
            d=o.read_typetree()
            if d['m_Mesh']!={'m_FileID':0,'m_PathID':new.path_id}:continue
            prior=copy.deepcopy(before.objects[i].read_typetree());expected=copy.deepcopy(prior);expected['m_AABB']=h['m_LocalAABB']
            assert d==expected,(label,'renderer changed beyond historical visual bounds',i)
            assert d['m_Bones']==prior['m_Bones'] and d['m_RootBone']==prior['m_RootBone'];rendered.append(i)
        assert rendered
        sid=next(i for i,p in oldmap.items() if p==n);ref=np.array(historical.objects[sid].read().image.convert('RGB'))
        targets=[i for i,p in texmap.items() if p==n]
        for tid in targets:
            image=np.array(f.objects[tid].read().image.convert('RGB'));baseimage=np.array(before.objects[tid].read().image.convert('RGB'))
            assert np.array_equal(image[:512,:512],ref[:512,:512]),(label,'head pixels mismatch')
            assert np.array_equal(image[128:256,512:768],ref[128:256,512:768]),(label,'hair palette mismatch')
            assert np.array_equal(image[512:],baseimage[512:]),(label,'v21 approved outfit changed')
            # Everything outside the two exact historical regions is preserved.
            mask=np.ones((1024,1024),bool);mask[:512,:512]=False;mask[128:256,512:768]=False
            assert np.array_equal(image[mask],baseimage[mask]),(label,'unrequested atlas pixels changed')
            t=f.objects[tid].read_typetree();assert t['m_TextureFormat']==3 and t['m_MipCount']==11
        rows.append(dict(profile=label,mesh_id=new.path_id,mesh_historical_sha256=H(old.get_raw_data()),
            body_head_prefix_vertices=6194,body_head_vertex_stride=stride,body_head_topology_exact=True,
            bones_bindposes_root_exact=True,renderer_ids=rendered,texture_ids=targets,
            historical_head_pixel_sha256=H(ref[:512,:512].tobytes()),
            approved_v21_outfit_pixels_exact=True,other_atlas_regions_exact=True))
    # Round trip verifies the actual saved fixture, not only in-memory assumptions.
    out=R/'visuals-v22-bots';out.mkdir(exist_ok=True);path=out/'sharedassets0.assets';path.write_bytes(f.save())
    reloaded=UnityPy.load(str(path)).file
    assert snapshot(reloaded)==snapshot(f),'Serialized reload mismatch'
    final=snapshot(f);again=build_bot_restore_v22(f);assert snapshot(f)==final,('not idempotent',delta(f,final))
    result=dict(passed=True,profiles=rows,changed=report['changed'],whitelist=sorted(whitelist),
                all_other_objects_exact=True,colliders_physics_hierarchy_materials_animations_exact=True,
                exact_historical_mesh_bytes=True,body_head_6194_vertex_prefix_exact=True,
                approved_v21_outfits_exact=True,bindpose_bone_hashes_skinning_prefix_exact=True,
                serialized_roundtrip_exact=True,idempotent=True,baseline=str(src),historical_reference=str(BASE))
    (R/'analysis/v22-bot-restore-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':validate()
