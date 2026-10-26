"""Exact serialized contracts for v22 environment corrective deltas."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,UnityPy
from build_environment_v22 import *
from build_scene_v20 import _apply,_vertices,_world
ALLOW={'resources.assets':[7,8],'sharedassets1.assets':[68,71,72],'sharedassets3.assets':[3],
       'level1':[284,285,286,287],'level2':[322,323,324,325],'level3':[357,360]}

def validate(files,baseline,report):
    assert report['changed_objects']==ALLOW
    for n,f in files.items():
        old=baseline[n];assert delta(f,snapshot(old))==ALLOW[n],n
        assert set(old.objects)<=set(f.objects)
        for i,o in old.objects.items():
            if i not in ALLOW[n]:assert o.get_raw_data()==f.objects[i].get_raw_data(),(n,i)
            if 'Collider' in o.type.name:
                assert o.get_raw_data()==f.objects[i].get_raw_data()
                if o.type.name=='MeshCollider':
                    ref=o.read_typetree()['m_Mesh'];fid=ref['m_FileID'];mid=ref['m_PathID']
                    owner=n if not fid else old.externals[fid-1].path.split('/')[-1]
                    if mid and owner in baseline:assert baseline[owner].objects[mid].get_raw_data()==files[owner].objects[mid].get_raw_data(),(n,i,owner,mid)
    for n in ('level1','level2'):
        f=files[n];gs,ts,ps=hierarchy(f);g=gs[ts[ps['Cloudcourt Dry Sand Runoff']]['m_GameObject']['m_PathID']]
        for c in g['m_Component']:
            o=f.objects[c['component']['m_PathID']]
            if o.type.name=='MeshRenderer':
                d=o.read_typetree();assert (d['m_CastShadows'],d['m_ReceiveShadows'],d['m_LightProbeUsage'],d['m_ReflectionProbeUsage'],d['m_LightmapIndex'])==(0,1,0,0,65535)
        # All original palms/renderers, Sun, probes, terrain, water and lightmap
        # data remain exact bytes. Thus runtime player and ball shadows survive.
        assert sum(1 for p in ps if '/Cloudcourt Fan Palm ' in p)==17
    s=files['sharedassets1.assets'];m=named(s,'Mesh','Cloudcourt Dry Sand Runoff');v=_vertices(m)
    assert len(v)==4 and np.allclose(v[:,1],.004) and np.allclose(v.min(0),[-12,.004,-18]) and np.allclose(v.max(0),[12,.004,18])
    assert len(m.read_typetree()['m_IndexBuffer'])//6==2
    sk=named(s,'Mesh','Cloudcourt Orla Skyline');d=sk.read_typetree();assert len(d['m_SubMeshes'])==1 and len(d['m_IndexBuffer'])//6==1572
    assert _vertices(sk)[:,0].max()<-30 and _vertices(sk)[:,1].max()>34
    mat=named(s,'Material','Cloudcourt Dry Sand').read_typetree();fl=dict(mat['m_SavedProperties']['m_Floats']);assert all(fl[k]==0 for k in ['_Glossiness','_Metallic','_SpecularHighlights','_GlossyReflections'])
    assert mat['m_Shader']==ptr(148,4)
    for i in (7,8):assert not any(t['m_Texture']['m_PathID'] for k,t in files['resources.assets'].objects[i].read_typetree()['m_SavedProperties']['m_TexEnvs'])
    assert report['arena']['board_outer_size_m'][0]>report['arena']['board_outer_size_m'][1]
    assert report['arena']['board_outer_size_m'][1]<3
    # Ground clearance: exact flat terrain (height/collider object preserved).
    h=baseline['sharedassets1.assets'].objects[67].read_typetree()['m_Heightmap'];N=h['m_Resolution']
    x=-33.539940834+np.arange(N)*h['m_Scale']['x'];z=-85.263917923+np.arange(N)*h['m_Scale']['z']
    H=-3.668615818+np.array(h['m_Heights']).reshape(N,N)/32766*h['m_Scale']['y'];region=H[np.ix_(abs(z)<=18,abs(x)<=12)]
    assert np.ptp(region)<1e-10 and -.001<region.min()<.001 and region.max()<.004
    f=baseline['resources.assets'];gs,ts,ps=hierarchy(f);t=ps['GameRules/Field-Regular-900x450/PlayLine'];v=_apply(_world(ts,t),_vertices(f.objects[61]));above=v[v[:,1]>.004,1];assert above.min()>.02
    return dict(passed=True,exact_whitelists=True,colliders_and_collision_meshes_exact=True,terrain_exact=True,
        sun_bot_ball_palm_shadow_settings_exact=True,original_palms_static_and_exact=True,skyline_triangles=1572,skyline_draws=1,
        dry_surface_triangles=2,dry_surface_draws=1,surface_y_m=.004,flat_terrain_y_m=float(region.min()),court_line_visible_top_min_y_m=float(above.min()),
        board_size_m=report['arena']['board_outer_size_m'],headset_capture=False)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=R/'working/VolleyballFever_Data');p.add_argument('--fixture-dir',type=Path,default=R/'visuals-v22-environment');a=p.parse_args()
    baseline={n:UnityPy.load(str(a.source_dir/n)).file for n in NAMES};files={n:UnityPy.load(str(a.fixture_dir/n)).file for n in NAMES}
    report=json.loads((a.fixture_dir/'environment-report.json').read_text());result=validate(files,baseline,report)
    raw={n:snapshot(f) for n,f in files.items()};build_environment_assets_v22(files)
    for n,f in files.items():assert snapshot(f)==raw[n],('not idempotent',n,delta(f,raw[n]))
    result['idempotent']=True;(a.fixture_dir/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
