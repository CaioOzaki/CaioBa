"""Asset isolation/anatomy plus real compiled codec/menu regression tests."""
from pathlib import Path
import ctypes,itertools,json,sys
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import UnityPy,numpy as np
from fix_gloves_v16 import hierarchy
from build_avatar_v21 import build_resources,build_menu
from build_customization_fix_v20 import mip_report
F=R/'visuals-v21-avatar'

def assets():
    before=UnityPy.load(str(R/'versions/cloudcourt-v20-1-antes-v21/resources.assets')).file
    f=UnityPy.load(str(F/'resources.assets')).file
    report=json.loads((F/'avatar-v21-report.json').read_text())['resources.assets']
    allowed=set(report['changed_existing_ids'])
    assert allowed=={629,638,665,666,699,792,797,1308,1312,1317,1321}
    for i,o in before.objects.items():
        if i not in allowed:assert o.get_raw_data()==f.objects[i].get_raw_data(),(i,o.type.name)
        elif o.type.name=='Transform':
            old=o.read_typetree();new=f.objects[i].read_typetree()
            assert {k for k in old if old[k]!=new[k]}=={'m_Children'}
            assert new['m_Children'][:len(old['m_Children'])]==old['m_Children']
        else:assert o.type.name=='MeshRenderer'
    assert all(f.objects[i].get_raw_data()==o.get_raw_data() for i,o in before.objects.items() if o.type.name in ('Texture2D','MonoBehaviour','BoxCollider','SphereCollider','CapsuleCollider','Mesh','Rigidbody'))
    meshes={}
    for record in report['hand_meshes']:
        d=f.objects[record['mesh']].read_typetree();v=np.frombuffer(bytes(d['m_VertexData']['m_DataSize']),dtype='<f4').reshape(-1,12)
        tri=np.frombuffer(bytes(d['m_IndexBuffer']),dtype='<u2').reshape(-1,3)
        assert np.isfinite(v).all() and tri.max()<len(v)
        assert np.allclose(np.linalg.norm(v[:,3:6],axis=1),1,atol=1e-5)
        center=np.array([d['m_LocalAABB']['m_Center'][k] for k in 'xyz']);extent=np.array([d['m_LocalAABB']['m_Extent'][k] for k in 'xyz'])
        assert (np.abs(v[:,:3]-center)<=extent+1e-6).all()
        meshes[record['side'],record['state']]=(v,tri)
    for state in ('Open','Closed'):
        lv,lt=meshes['L',state];rv,rt=meshes['R',state]
        assert np.allclose(lv[:,0],-rv[:,0]) and np.allclose(lv[:,1:3],rv[:,1:3])
        assert np.allclose(lv[:,3],-rv[:,3]) and np.allclose(lv[:,4:6],rv[:,4:6])
        assert np.array_equal(lt[:,[0,2,1]],rt)
        for side in ('L','R'):
            v,_=meshes[side,state];thumb=v[v[:,1]>(.09 if state=='Open' else .075),:3]
            assert len(thumb) and thumb[:,0].mean()*(1 if side=='L' else -1)>0
        if state=='Closed':assert lv[:,1].max()>.09 and lv[:,2].max()>.20
        else:assert lv[:,2].max()>.20
    objects,transforms,paths=hierarchy(f)
    for tid in report['bot_visuals']+report['hand_visuals']:
        go=objects[transforms[tid]['m_GameObject']['m_PathID']]
        assert not go['m_IsActive']
        assert {f.objects[c['component']['m_PathID']].type.name for c in go['m_Component']}=={'Transform','MeshFilter','MeshRenderer'}
    neutral=f.objects[report['texture']].read();assert neutral.m_TextureFormat==12
    assert all(m['alpha_min']==255 for m in mip_report(neutral))
    for ident in (1329,1330):assert all(m['alpha_min']==255 for m in mip_report(f.objects[ident].read()))
    data={i:o.get_raw_data() for i,o in f.objects.items()};build_resources(f)
    again=UnityPy.load(f.save()).file
    assert set(data)==set(again.objects) and all(again.objects[i].get_raw_data()==raw for i,raw in data.items()),'resource builder not idempotent'
    menu=UnityPy.load(str(F/'level0')).file;data={i:o.get_raw_data() for i,o in menu.objects.items()};build_menu(menu);again=UnityPy.load(menu.save()).file
    assert set(data)==set(again.objects) and all(again.objects[i].get_raw_data()==raw for i,raw in data.items()),'menu builder not idempotent'
    return dict(original_physics_scripts_meshes_textures_byte_identical=True,mirrored_meshes=4,new_visual_only_nodes=9,opaque_bc3_preserved=True,idempotent=True)

def native():
    d=ctypes.CDLL(str(F/'avatar-tests.dll'));pack=d.appearance_pack_pose_v21;pack.argtypes=[ctypes.c_int]*5
    dec=d.appearance_decode_v21;dec.argtypes=[ctypes.c_int]+[ctypes.POINTER(ctypes.c_int)]*4
    cases=0
    for team,style,change,tone,pose in itertools.product(range(2),range(81),range(2),range(6),range(5)):
        encoded=pack(team,style,change,tone,pose);outputs=[ctypes.c_int() for _ in range(4)]
        assert dec(encoded,*[ctypes.byref(x) for x in outputs])==1
        assert [x.value for x in outputs]==[team,style,change,tone]
        assert d.appearance_pose_v21(encoded)==pose;cases+=1
    for bad in (0x5c210000|(9<<1),0x5c210000|(9<<5),0x5c210000|(6<<10),0x5c210000|(5<<13)):
        outputs=[ctypes.c_int(123) for _ in range(4)];assert dec(bad,*[ctypes.byref(x) for x in outputs])==-1
        assert all(x.value==123 for x in outputs)
    outputs=[ctypes.c_int() for _ in range(4)]
    for old in (0x5600,0x5c190000,0x5c200000,-1):assert dec(old,*[ctypes.byref(x) for x in outputs])==0
    for l,r,ready,side in itertools.product(range(2),repeat=4):assert d.hand_pose_v21(l,r,ready,side)==((1 if ready and l and r else 2) if (r if side else l) else 0)
    d.test_press.argtypes=[ctypes.c_char_p];d.test_uv.argtypes=[ctypes.c_int,ctypes.c_int];d.test_uv.restype=ctypes.c_float
    for face,outfit,tone in itertools.product(range(9),range(9),range(6)):
        d.test_reset(face,outfit,tone);assert d.test_press(b'CC_CustomizeOpen')==1 and d.test_visible()
        assert d.test_style()==face+9*outfit and d.test_tone()==tone
        for name,newface,newoutfit in [(b'CC_FaceNext',(face+1)%9,outfit),(b'CC_OutfitPrev',(face+1)%9,(outfit+8)%9)]:
            assert d.test_press(name)==1
            for side,index in enumerate((newface,newoutfit)):
                expected=(index%3/3,(2-index//3)/3,1/3 if side==0 else 1/6,1/3 if side==0 else 1/6)
                assert all(abs(d.test_uv(side,k)-v)<1e-6 for k,v in enumerate(expected))
                assert d.test_dirty(side)==d.test_verts(side) and d.test_dirty(side)>=2
        assert d.test_press(b'CC_HandToneNext')==1 and d.test_tone()==(tone+1)%6
        assert d.test_sends()==3
        d.test_press(b'CC_CustomizeBack');assert not d.test_visible()
    c=d.celebration_allowed_v21;c.argtypes=[ctypes.c_int]*4+[ctypes.c_float]*2
    for winner,bot,human,rally in itertools.product((-1,0,1,2),repeat=4):
        for now in (9.,10.,11.):assert bool(c(winner,bot,human,rally,now,10.))==(winner in (0,1) and bot==winner and human==winner and not rally and now<10)
    return dict(packet_roundtrips=cases,hand_pose_cases=16,menu_initial_combinations=486,preview_cache_invalidation_called_every_refresh=True,celebration_predicate_cases=768)

if __name__=='__main__':
    result=dict(passed=True,assets=assets(),native=native(),scope='Compiled production codec/menu with Unity stubs and serialized asset checks. No Quest or two-PC claim.')
    (R/'analysis/v21-avatar-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
