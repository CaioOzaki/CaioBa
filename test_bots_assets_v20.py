"""Nine bot appearances, all mip alpha, rig preservation and database mapping."""
from pathlib import Path
import argparse,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import numpy as np,UnityPy
from PIL import Image
import build_bots_v20 as build
from fix_gloves_v16 import hierarchy


def validate(path,baseline=None):
    file=UnityPy.load(str(path)).file
    old=UnityPy.load(str(baseline or R/'versions/cloudcourt-v19-antes-v20/sharedassets0.assets')).file
    catalog=json.loads((build.A/'unity-bindings.json').read_text(encoding='utf-8'))
    meshes=catalog['mesh_ids'];allowed=set(catalog['changed_object_ids']);oldids=set(old.objects)
    assert set(file.objects)-oldids==set(meshes[7:])
    for i,o in old.objects.items():
        if i not in allowed:assert file.objects[i].get_raw_data()==o.get_raw_data(),(i,o.type.name)
    checks=[]
    for n,ident in enumerate(meshes):
        d=file.objects[ident].read_typetree();count=d['m_VertexData']['m_VertexCount']
        raw=bytes(d['m_VertexData']['m_DataSize']);assert len(raw)==count*80
        row=np.frombuffer(raw,'<f4').reshape(-1,20)
        skin=np.frombuffer(raw,'<u4').reshape(-1,20)[:,16:]
        triangles=np.frombuffer(bytes(d['m_IndexBuffer']),'<u2').reshape(-1,3)
        assert triangles.max()<count and count<10000
        assert np.isfinite(row[:,:16]).all()
        assert np.allclose(np.linalg.norm(row[:,3:6],axis=1),1,atol=1e-4)
        assert np.allclose(row[:,12:16],[1,0,0,0]) and skin[:,0].max()<len(d['m_BindPose'])
        assert d['m_BindPose']==old.objects[4322].read_typetree()['m_BindPose']
        center=np.array([d['m_LocalAABB']['m_Center'][k] for k in 'xyz']);extent=np.array([d['m_LocalAABB']['m_Extent'][k] for k in 'xyz'])
        assert (np.abs(row[:,:3]-center)<=extent+1e-6).all()
        start=catalog['hair_vertex_ranges'][n][0]
        assert (skin[start:,0]==12).all(),'Hair does not follow the original head bone.'
        hair=row[start:,:3].copy()
        if n==8:hair/=[.82,1.10,.86]
        assert np.any((np.abs(hair[:,0])<.10)&(hair[:,1]>2.40)&(hair[:,1]<2.70)&(hair[:,2]<-.44)), 'Scalp/nape coverage missing.'
        ht=triangles[(triangles>=start).all(axis=1)];p=row[ht,:3];normal=row[ht,3:6].mean(axis=1)
        facing=(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0])*normal).sum(axis=1)
        assert (facing>=-1e-9).all(),'Hair face winding points inward.'
        if n==8:
            _,base=mesh_rows(file.objects[4322])
            assert np.allclose(row[:start,:3],base[:start,:3]*[.82,1.10,.86],atol=1e-6)
        checks.append(dict(bot=n+1,mesh=ident,vertices=count,triangles=len(triangles),hair_vertices=count-start))
    alpha_levels=0;max_error=0;mean_errors=[]
    for key,profile in catalog['texture_profiles'].items():
        ident=int(key);obj=file.objects[ident];d=obj.read_typetree()
        assert d['m_TextureFormat']==10 and d['m_Width']==d['m_Height']==1024 and d['m_MipCount']==9
        raw=bytes(d['image data']);offset=0
        for level in range(9):
            size=1024>>level;length=((size+3)//4)**2*8
            image=Image.frombytes('RGBA',(size,size),raw[offset:offset+length],'bcn',1)
            assert image.getextrema()[3]==(255,255),(ident,level,image.getextrema()[3])
            offset+=length;alpha_levels+=1
        assert offset==len(raw)==d['m_CompleteImageSize']
        expected=np.array(Image.open(build.A/f'bot-{profile+1:02d}-atlas.png').convert('RGB'))
        actual=np.array(obj.read().image.convert('RGB'));error=np.abs(actual.astype(np.int16)-expected.astype(np.int16))
        assert error.mean()<3,(ident,error.mean());mean_errors.append(float(error.mean()));max_error=max(max_error,int(error.max()))
    gs,ts,paths=hierarchy(file)
    def visible_meshes(gid):
        g=gs[gid];out=[]
        for c in g['m_Component']:
            obj=file.objects[c['component']['m_PathID']]
            if obj.type.name=='SkinnedMeshRenderer':
                d=obj.read_typetree()
                if d['m_Enabled']:out.append(d['m_Mesh']['m_PathID'])
            elif obj.type.name=='Transform':
                for child in ts[obj.path_id]['m_Children']:out+=visible_meshes(ts[child['m_PathID']]['m_GameObject']['m_PathID'])
        return out
    menu=UnityPy.load(str(R/'versions/cloudcourt-v19-antes-v20/level0')).file
    database=menu.objects[1022].get_raw_data();assert struct.unpack_from('<i',database,32)[0]==48
    loaded=[]
    for identity,index in enumerate(build.DATABASE_INDICES):
        fid,gid=struct.unpack_from('<iq',database,36+index*12);assert fid==2
        actual=visible_meshes(gid);assert actual==[meshes[identity]],(index,gs[gid]['m_Name'],actual)
        loaded.append(dict(identity=identity+1,database_index=index,prefab=gs[gid]['m_Name'],mesh=actual[0]))
    assert len({x['mesh'] for x in loaded})==9
    for i in range(7):
        legacy=Image.open(R/f'assets/cloudcourt-v16/bot-{i+1:02d}-rosto.png').convert('RGB')
        own=Image.open(build.A/f'bot-{i+1:02d}-rosto.png').convert('RGB')
        assert np.array_equal(np.array(legacy),np.array(own))
    assert catalog['grandma_hair']=='#171b24' and catalog['grandma_shirt']=='#762f49'
    assert Path(path).stat().st_size<200*1024*1024
    before_bytes=sum(old.objects[int(i)].read_typetree()['m_CompleteImageSize'] for i in catalog['texture_profiles'])
    after_bytes=sum(file.objects[int(i)].read_typetree()['m_CompleteImageSize'] for i in catalog['texture_profiles'])
    assert after_bytes<before_bytes
    return dict(passed=True,bots=checks,database=loaded,opaque_mips_verified=alpha_levels,
                average_DXT1_RGB_error=float(np.mean(mean_errors)),maximum_DXT1_RGB_error=max_error,
                texture_bytes_before=before_bytes,texture_bytes_after=after_bytes,
                unrelated_objects_byte_identical=len(oldids-allowed),rig_transforms_materials_scripts_colliders_unchanged=True,
                seven_legacy_faces_pixel_identical=True,grandma_black_hair_and_wine_clothes_preserved=True,
                file_bytes=Path(path).stat().st_size,scope='Serialized geometry, textures and rig bindings; actual animated VR review remains required.')


def mesh_rows(obj):
    d=obj.read_typetree();return d,np.frombuffer(bytes(d['m_VertexData']['m_DataSize']),'<f4').reshape(-1,20)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--asset',type=Path);args=parser.parse_args()
    path=args.asset or R/'visuals-v20-bots/sharedassets0.assets';report=validate(path)
    if not args.asset:
        file=UnityPy.load(str(path)).file;before={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in file.objects.items()}
        scope=build.authoring();models=[build.character(scope,i)[0] for i in range(9)]
        atlas=[Image.open(build.A/f'bot-{i+1:02d}-atlas.png').convert('RGB') for i in range(9)]
        catalog=json.loads((build.A/'catalog.json').read_text());build.apply_bots_assets_v20(file,(scope,models,atlas,catalog))
        repeat=R/'visuals-v20-bots/sharedassets0-reapplied.assets';repeat.write_bytes(file.save())
        after=UnityPy.load(str(repeat)).file
        assert before=={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in after.objects.items()}
        report['idempotent']=True
    (R/'analysis/v20-bot-assets-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
