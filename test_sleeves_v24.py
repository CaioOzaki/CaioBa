"""Offline serialized v23-to-v24 isolation and exact cuff partition audit."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from build_sleeves_v24 import build_resources_v24,OUTFIT_RGB,outfit_colors
from fix_gloves_v16 import hierarchy

def run():
    src=UnityPy.load(str(R/'versions/cloudcourt-v23-antes-v24/resources.assets')).file
    f=UnityPy.load(str(R/'visuals-v24-sleeves/resources.assets')).file
    report=json.loads((R/'visuals-v24-sleeves/sleeves-v24-report.json').read_text())
    allowed={r[k] for r in report['hands'] for k in ('transform','filter')}
    assert set(report['changed_existing_ids'])==allowed
    for i,o in src.objects.items():
        if i not in allowed:assert o.get_raw_data()==f.objects[i].get_raw_data(),(i,o.type.name)
        else:
            old=o.read_typetree();new=f.objects[i].read_typetree()
            if o.type.name=='Transform':
                assert {k for k in old if old[k]!=new[k]}=={'m_Children'}
                assert old['m_Children']==new['m_Children'][:-1]
            else:
                assert o.type.name=='MeshFilter';old['m_Mesh']=new['m_Mesh'];assert old==new
    sleeves={}
    for r in report['hands']:
        old=src.objects[r['original_mesh']].read_typetree();new=f.objects[r['mesh']].read_typetree();s=f.objects[r['sleeve_mesh']].read_typetree()
        assert old['m_VertexData']==new['m_VertexData'],'all approved hand positions, normals, UVs remain exact'
        ot=np.frombuffer(bytes(old['m_IndexBuffer']),'<u2').reshape(-1,3);nt=np.frombuffer(bytes(new['m_IndexBuffer']),'<u2').reshape(-1,3);st=np.frombuffer(bytes(s['m_IndexBuffer']),'<u2').reshape(-1,3)
        cuff=np.all((ot>=425)&(ot<850),axis=1)
        assert np.array_equal(nt,ot[~cuff]) and np.array_equal(st+425,ot[cuff])
        ov=np.frombuffer(bytes(old['m_VertexData']['m_DataSize']),'<f4').reshape(-1,12);sv=np.frombuffer(bytes(s['m_VertexData']['m_DataSize']),'<f4').reshape(-1,12)
        assert np.array_equal(ov[425:850,:10],sv[:,:10])
        assert np.all(sv[:,10]==.5625) and np.all(sv[:,11]==.9375)
        side='L' if '/Hand Root L/' in r['path'] else 'R';sleeves[side]=(sv,st)
        tr=f.objects[r['sleeve_transform']].read_typetree();assert tr['m_Father']['m_PathID']==r['transform']
        assert tr['m_LocalPosition']==dict(x=0.,y=0.,z=0.) and tr['m_LocalScale']==dict(x=1.,y=1.,z=1.)
    l,lt=sleeves['L'];r,rt=sleeves['R'];assert np.array_equal(lt[:,[0,2,1]],rt)
    assert np.array_equal(l[:,[0,3]],-r[:,[0,3]]) and np.array_equal(l[:,[1,2,4,5]],r[:,[1,2,4,5]])
    g,t,p=hierarchy(f)
    for path,tid in p.items():
        if not path.endswith('/CC_WinThumb'):continue
        go=g[t[tid]['m_GameObject']['m_PathID']]
        for c in go['m_Component']:
            i=c['component']['m_PathID'];assert src.objects[i].get_raw_data()==f.objects[i].get_raw_data()
    snapshot={i:o.get_raw_data() for i,o in f.objects.items()};build_resources_v24(f)
    again=UnityPy.load(f.save()).file
    assert set(snapshot)==set(again.objects) and all(b==again.objects[i].get_raw_data() for i,b in snapshot.items()),'idempotence'
    assert outfit_colors(f)==OUTFIT_RGB
    result=dict(passed=True,changed_existing_ids=sorted(allowed),added_objects=len(report['added_ids']),all_original_meshes_materials_textures_colliders_scripts_byte_identical=True,all_v23_hand_vertex_data_exact=True,only_cuff_triangles_partitioned=True,mirrored_sleeves=True,bot_overlay_components_unchanged=True,atlas_samples_verified=True,idempotent=True)
    (R/'analysis/v24-sleeves-assets-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
