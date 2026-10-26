"""Serialized v21 artwork contracts; no headset or multiplayer claims."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import numpy as np,UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler
from build_environment_v21 import build_environment_assets,geometry_class,snapshot,delta,skyline_geometry
from build_bot_appearance_v21 import apply_bot_appearance_v21,appearance_art,PROFILES
from fix_gloves_v16 import hierarchy

def verts(obj):
    h=MeshHandler(obj.read());h.process();return np.asarray(h.m_Vertices)
def validate(files,baseline,report,botreport):
    changes={n:delta(f,snapshot(baseline[n])) for n,f in files.items()}
    expected=report['changed_objects'];expected={**expected,'sharedassets0.assets':botreport['changed_object_ids']}
    assert changes==expected,(changes,expected)
    counts={}
    for n,f in files.items():
        old=baseline[n];counts[n]=len(f.objects)
        assert set(old.objects)<=set(f.objects)
        for i,o in old.objects.items():
            if 'Collider' in o.type.name or o.type.name in ('Shader','TerrainData','TerrainCollider','Rigidbody','Animator','Animation'):
                assert o.get_raw_data()==f.objects[i].get_raw_data(),(n,i,o.type.name)
            if o.type.name=='MeshCollider':
                ref=o.read_typetree()['m_Mesh']
                if ref['m_FileID']==0 and ref['m_PathID']:
                    meshid=ref['m_PathID'];assert old.objects[meshid].get_raw_data()==f.objects[meshid].get_raw_data(),('collider mesh changed',n,meshid)
    for n in ('level1','level2'):
        f=files[n];gs,ts,ps=hierarchy(f)
        for p,i in ps.items():
            if '/Cloudcourt Fan Palm ' not in p:continue
            g=gs[ts[i]['m_GameObject']['m_PathID']]
            for c in g['m_Component']:
                ob=f.objects[c['component']['m_PathID']]
                if ob.type.name=='Animator':assert not ob.read_typetree()['m_Enabled']
        new=[f.objects[i] for i in set(f.objects)-set(baseline[n].objects)]
        assert sorted(o.type.name for o in new)==['GameObject','MeshFilter','MeshRenderer','Transform']
    shared=files['sharedassets1.assets'];palm=shared.objects[3].read_typetree()
    assert palm['m_Shader']==dict(m_FileID=4,m_PathID=148) and not palm['m_ShaderKeywords']
    assert not any('wind' in k.lower() for k,v in palm['m_SavedProperties']['m_Floats'])
    skyline=next(o for o in shared.objects.values() if o.type.name=='Mesh' and o.read_typetree()['m_Name']=='Cloudcourt Orla Skyline')
    d=skyline.read_typetree();assert len(d['m_SubMeshes'])==1
    assert len(d['m_IndexBuffer'])//6==1572 and d['m_VertexData']['m_VertexCount']==3144
    assert np.max(verts(skyline)[:,0])<=-32.1,'City must remain beyond the play/runoff bank'
    for n in ('resources.assets','sharedassets0.assets'):
        f=files[n]
        ids=[40] if n=='resources.assets' else botreport['changed_object_ids']
        for i in ids:
            t=f.objects[i].read();d=t.object_reader.read_typetree()
            assert d['m_TextureFormat']==3 and d['m_MipCount']==11
            assert t.image.convert('RGBA').getextrema()[3]==(255,255)
    f=files['resources.assets']
    for i in (7,8):
        d=f.objects[i].read_typetree();assert dict(d['m_SavedProperties']['m_Colors'])['_Color']['r']<.03
        assert all(not v['m_Texture']['m_PathID'] for k,v in d['m_SavedProperties']['m_TexEnvs'])
    for i in (5,6):assert dict(f.objects[i].read_typetree()['m_SavedProperties']['m_Colors'])['_Color']==dict(r=1.,g=1.,b=1.,a=1.)
    f=files['level3'];roof_id=f.objects[199].read_typetree()['m_Mesh']['m_PathID'];assert roof_id!=7
    roof=f.objects[roof_id].read_typetree();v=verts(f.objects[roof_id]);part=roof['m_SubMeshes'][1]
    tri=np.frombuffer(bytes(roof['m_IndexBuffer']),dtype='<u2').reshape(-1,3)
    ptri=tri[roof['m_SubMeshes'][0]['indexCount']//3:]
    assert len(ptri)==16 #8 roof-facing triangles, 4 gable triangles +4 degenerate quads
    for sign in (-1,1):
        gable=[t for t in ptri if np.allclose(v[t,2],sign*18)]
        assert len(gable)==4
        assert any(np.isclose(v[t,1],16.02).any() for t in gable)
    assert report['arena']['square_boards']==2
    assert len(report['arena']['banner_moves'])==20
    for old,new in report['arena']['banner_moves']:
        assert new[2] in (-14,-6,2,10,14) and abs(new[0])<11.3
    # Exact non-targeted shared0 bytes guarantee BOT1, new bots, player atlases,
    # meshes, materials, hierarchy, animation and selection mapping are preserved.
    shared0=files['sharedassets0.assets'];before=baseline['sharedassets0.assets'];allowed=set(botreport['changed_object_ids'])
    assert all(o.get_raw_data()==shared0.objects[i].get_raw_data() for i,o in before.objects.items() if i not in allowed)
    assert set(botreport['texture_profiles'].values())==set(PROFILES)
    return dict(passed=True,exact_whitelists=True,colliders_and_physics_unchanged=True,shader_binaries_unchanged=True,
      terrain_heightmap_unchanged=True,palms_static_shader=True,skyline_triangles=1572,skyline_draws_per_scene=1,
      roof_inside_and_outside_faces=True,gables_filled=2,flags_between_columns=True,scoreboard_backings_square=2,
      opaque_mips='RGB24 1024x1024, 11 levels',bot1_and_nonrequested_profiles_exact_bytes=True,
      object_counts=counts,scope='Serialized checks and authored previews. No Quest headset/2-PC playtest performed.')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=R/'versions/cloudcourt-v20-1-antes-v21');p.add_argument('--fixture-dir',type=Path,default=R/'visuals-v21-environment');a=p.parse_args()
    report=json.loads((a.fixture_dir/'environment-report.json').read_text());botreport=json.loads((a.fixture_dir/'bot-appearance-report.json').read_text());botreport['texture_profiles']={int(k):v for k,v in botreport['texture_profiles'].items()}
    names=list(report['changed_objects'])+['sharedassets0.assets'];files={n:UnityPy.load(str(a.fixture_dir/n)).file for n in names};before={n:UnityPy.load(str(a.source_dir/n)).file for n in names}
    result=validate(files,before,report,botreport)
    raw={n:snapshot(f) for n,f in files.items()};build_environment_assets(files);apply_bot_appearance_v21(files['sharedassets0.assets'])
    for n,f in files.items():assert snapshot(f)==raw[n],('not idempotent',n,delta(f,raw[n]))
    result['idempotent']=True;(a.fixture_dir/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
