"""Independent exact-union/typed-reference audit of the reloaded v22 candidate."""
from pathlib import Path
import hashlib,json,sys,struct
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy,numpy as np
from build_scene_v20 import _vertices,_world,_apply
from fix_gloves_v16 import hierarchy
from build_environment_v22 import scoreboard_bounds
from test_integration_v21 import pointers
BASE=R/'versions/cloudcourt-v21-antes-v22';CAND=R/'visuals-v22-integrated'
NAMES=['level0','level1','level2','level3','level4','resources.assets']+[f'sharedassets{i}.assets' for i in range(5)]
BOT_MESHES={4323,4324,4327,4328}
BOT_RENDERERS={3530,3531,3532,3535,3541,3544,3547,3551,3555,3559,3561,3564,4201,4205,4214,4217,4218,4220,4221,4222,4224,4230,4234,4237,4242,4245,4248}
VISUAL_TRANSFORMS={1356,1360,1364,1368,1372}
HAND_FILTERS={1341,1345,1349,1353,1357,1361,1365,1369,1373}
EXISTING={'level0':{1143,1146,1232,1236,1243,1248,1253,1257,1264,1268,1275},
          'level3':{357,360},'resources.assets':{7,8}|VISUAL_TRANSFORMS|HAND_FILTERS,
          'sharedassets0.assets':BOT_MESHES|BOT_RENDERERS,'sharedassets1.assets':{68},'sharedassets3.assets':{3}}
ADDED={'resources.assets':{1375,1376,1377,1378},'sharedassets1.assets':{71,72},'level1':{284,285,286,287},'level2':{322,323,324,325}}
H=lambda b:hashlib.sha256(b).hexdigest()

def main():
    report=json.loads((CAND/'build-report.json').read_text());files={};old={}
    for n in NAMES:
        p=BASE/n
        if not p.exists():p=R/'working/VolleyballFever_Data'/n
        old[n]=UnityPy.load(str(p)).file;files[n]=UnityPy.load(str(CAND/n if (CAND/n).exists() else p)).file
    live=Path(json.loads((R/'installation-status.json').read_text())['installed'])/'VolleyballFever_Data'
    def resolve(n,ref,baseline=False):
        owners=old if baseline else files
        target=n
        if ref['m_FileID']:
            assert 1<=ref['m_FileID']<=len(owners[n].externals)
            target=Path(owners[n].externals[ref['m_FileID']-1].path.replace('\\','/')).name
        if target not in owners:
            candidates=[BASE/target,R/'working/VolleyballFever_Data'/target,live/'Resources'/target]
            p=next((p for p in candidates if p.exists()),None);assert p is not None,('missing external file',n,target)
            owners[target]=UnityPy.load(str(p)).file
        obj=owners[target].objects.get(ref['m_PathID']);assert obj is not None,('missing PPtr',n,target,ref)
        return target,obj
    colliders=0;collision_meshes=0;introduced_refs=0;mesh_checks=[];rows={}
    for n in NAMES:
        b=old[n];f=files[n];assert set(b.objects)<=set(f.objects)
        changed={i for i,o in b.objects.items() if o.get_raw_data()!=f.objects[i].get_raw_data()};added=set(f.objects)-set(b.objects)
        assert changed==EXISTING.get(n,set()),('unauthorized changed union',n,changed^EXISTING.get(n,set()))
        assert added==ADDED.get(n,set()),('unauthorized added union',n,added^ADDED.get(n,set()))
        if n in report['files']:
            row=report['files'][n];assert set(row['changed'])==changed and set(row['added'])==added
            assert H((CAND/n).read_bytes())==row['sha256'] and H((BASE/n).read_bytes())==row['source_sha256']
        for i,o in b.objects.items():
            target=f.objects[i];typ=o.type.name
            if 'Collider' in typ or typ in ('Rigidbody','PhysicMaterial','Terrain','TerrainData','Shader','Animator','Animation','AnimationClip','Avatar'):
                assert o.get_raw_data()==target.get_raw_data(),('physics/rig asset altered',n,i,typ)
            if 'Collider' in typ:colliders+=1
            if typ=='MeshCollider':
                ref=o.read_typetree()['m_Mesh']
                if ref['m_PathID']:
                    owner,mesh=resolve(n,ref);_,prior=resolve(n,ref,True)
                    assert mesh.get_raw_data()==prior.get_raw_data(),('collider-referenced mesh altered',n,i,owner,mesh.path_id);collision_meshes+=1
            if typ=='Transform':
                d=target.read_typetree();p=o.read_typetree()
                if n=='resources.assets' and i in VISUAL_TRANSFORMS:
                    assert d['m_Father']==p['m_Father'] and d['m_LocalRotation']==p['m_LocalRotation']
                    assert d['m_LocalPosition']==dict(x=0.,y=0.,z=0.) and all(abs(d['m_LocalScale'][k]-1.3)<1e-6 for k in 'xyz')
                else:assert d==p,('original rig/tracking transform altered',n,i)
            if n=='sharedassets0.assets' and i in BOT_RENDERERS:
                a=o.read_typetree();d=target.read_typetree();assert {k for k in a if a[k]!=d[k]}=={'m_AABB'},('bot renderer beyond visual bound',i)
            if n=='resources.assets' and i in HAND_FILTERS:
                a=o.read_typetree();d=target.read_typetree();assert {k for k in a if a[k]!=d[k]}=={'m_Mesh'}
        for i in changed|added:
            obj=f.objects[i];assert obj.type.name not in ('Rigidbody','Animator','AnimationClip'),('unexpected physics edit',n,i)
            if obj.type.name=='MonoBehaviour':
                assert n=='level0' and i in changed
                raw=obj.get_raw_data();prior=b.objects[i].get_raw_data()
                assert len(raw)==len(prior)==96 and raw[:60]+raw[68:]==prior[:60]+prior[68:],('UI change beyond CurvedUI dimensions',n,i)
                refs=[('/m_GameObject',dict(m_FileID=struct.unpack_from('<i',raw,0)[0],m_PathID=struct.unpack_from('<q',raw,4)[0])),('/m_Script',dict(m_FileID=struct.unpack_from('<i',raw,16)[0],m_PathID=struct.unpack_from('<q',raw,20)[0]))]
            else:refs=list(pointers(obj.read_typetree()))
            for field,ref in refs:
                if not ref['m_PathID']:continue
                resolve(n,ref);introduced_refs+=1
            if obj.type.name=='Mesh':
                d=obj.read_typetree();v=_vertices(obj);assert np.isfinite(v).all()
                a=d['m_LocalAABB'];c=np.array([a['m_Center'][k] for k in 'xyz']);e=np.array([a['m_Extent'][k] for k in 'xyz']);assert np.all(v.min(0)>=c-e-1e-4) and np.all(v.max(0)<=c+e+1e-4),(n,i,'invalid mesh AABB')
                mesh_checks.append(dict(file=n,id=i,vertices=len(v),bounds_min=v.min(0).tolist(),bounds_max=v.max(0).tolist()))
        rows[n]=dict(changed=sorted(changed),added=sorted(added))
    # Candidate must retain exactly the isolated validated environment edits.
    for n,ids in report['environment']['changed_objects'].items():
        isolated=UnityPy.load(str(R/'visuals-v22-environment'/n)).file
        for i in ids:assert files[n].objects[i].get_raw_data()==isolated.objects[i].get_raw_data(),('environment conflict',n,i)
    assert (CAND/'sharedassets0.assets').read_bytes()==(R/'visuals-v22-bots/sharedassets0.assets').read_bytes(),'Bot candidate differs from independently validated historical restore'
    # Every renderer resolves to proper types after all helpers compose.
    render_refs=0
    for n in NAMES:
        for i,o in files[n].objects.items():
            if o.type.name not in ('MeshFilter','MeshRenderer','SkinnedMeshRenderer'):continue
            d=o.read_typetree()
            for key,typ in [('m_Mesh','Mesh')]:
                if key in d and d[key]['m_PathID']:assert resolve(n,d[key])[1].type.name==typ,(n,i,key)
            for ref in d.get('m_Materials',[]):
                if ref['m_PathID']:assert resolve(n,ref)[1].type.name=='Material',(n,i,'material')
            render_refs+=1
    dry=files['sharedassets1.assets'].objects[72].read_typetree();shader=resolve('sharedassets1.assets',dry['m_Shader'])[1]
    assert shader.type.name=='Shader' and shader.read_typetree()['m_ParsedForm']['m_Name']=='Standard'
    assert resolve('sharedassets1.assets',dict(dry['m_SavedProperties']['m_TexEnvs'])['_MainTex']['m_Texture'])[1].type.name=='Texture2D'
    # Both board sides use the same correctly oriented backing behind live UI.
    scene=files['level3'];gs,ts,ps=hierarchy(scene);v=_vertices(scene.objects[357]);lo,hi=scoreboard_bounds();boardrows=[]
    for side in (0,1):
        tr=ps[f'CloudBoard{side}'];world=_world(ts,tr);sign=1 if side==0 else -1
        panel=v[v[:,2]*sign>0];local=_apply(np.linalg.inv(world),panel)
        assert np.all(local[:,2]>0),'Backing must be behind forward-facing score UI on both sides'
        assert np.allclose(panel[:,0].max()-panel[:,0].min(),hi[0]-lo[0],atol=1e-5)
        assert np.allclose(panel[:,1].max()-panel[:,1].min(),hi[1]-lo[1],atol=1e-5)
        boardrows.append(dict(side=side,world_z=float(world[2,3]),backing_ui_local_z_min=float(local[:,2].min()),size_m=(hi-lo).tolist()))
    # Existing fitted board UI fields and original player fists/materials/textures are exact.
    for i in [270,275,278,280,282,284,286,288,290,292,306,311,314,316,318,320,322,324,326,328]:assert scene.objects[i].get_raw_data()==old['level3'].objects[i].get_raw_data()
    result=dict(passed=True,candidate=str(CAND),exact_authorized_unions=True,files=rows,
        unchanged_colliders=colliders,unchanged_collider_referenced_meshes=collision_meshes,
        original_physics_terrain_tracking_rig_animation_exact=True,intended_historical_bot_meshes=sorted(BOT_MESHES),
        bot_candidate_exact_validated_historical_fixture=True,all_introduced_pptrs_resolve=True,introduced_pptrs_checked=introduced_refs,
        typed_renderer_references_checked=render_refs,dry_surface_shader_actual_name='Standard',
        modified_mesh_aabbs=mesh_checks,scoreboard_both_sides=boardrows,environment_composition_exact=True,
        cross_module_conflicts=[],scope='Reloaded candidate asset audit. No live changes, Unity/VR render or multiplayer claim.')
    (R/'analysis/v22-integration-assets.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['files','modified_mesh_aabbs']},indent=2))
if __name__=='__main__':main()
