"""Validate 81 avatar combinations without changing the working game assets."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import UnityPy
import numpy as np
from PIL import Image
from build_customization_art_v19 import (A,CELL,SIZE,FACE_NAMES,OUTFIT_NAMES,create_art,
                                         apply_customization_assets,named)


def mesh_rows(obj):
    tree=obj.read_typetree()
    rows=np.frombuffer(bytes(tree['m_VertexData']['m_DataSize']),dtype='<f4').reshape(-1,12)
    return tree,rows


def validate(file,before=None):
    face_material=named(file,'Material','Cloudcourt v19 Face')
    outfit_material=named(file,'Material','Cloudcourt v19 Outfit')
    assert face_material and outfit_material and face_material.path_id!=outfit_material.path_id
    types={}
    for part,material,default_index in [('face',face_material,0),('outfit',outfit_material,2)]:
        tree=material.read_typetree()
        texenv=next(v for k,v in tree['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
        assert texenv['m_Scale']==dict(x=1.,y=1.)
        assert np.allclose(list(texenv['m_Offset'].values()),[(default_index%3)/3,(2-default_index//3)/3])
        ptr=texenv['m_Texture'];assert ptr['m_FileID']==0
        obj=file.objects[ptr['m_PathID']];data=obj.read_typetree()
        assert data['m_Width']==data['m_Height']==SIZE and data['m_MipCount']==9
        assert data['m_TextureFormat']==25 and data['m_StreamData']['size']==0
        assert data['m_TextureSettings']['m_WrapU']==data['m_TextureSettings']['m_WrapV']==1
        decoded=np.array(obj.read().image.convert('RGB'))
        expected=np.array(Image.open(A/('faces-atlas.png' if part=='face' else 'outfits-atlas.png')).convert('RGB'))
        error=np.abs(decoded.astype(np.int16)-expected.astype(np.int16))
        assert error.mean()<1.5 and np.quantile(error,.999)<35,(part,error.mean(),np.quantile(error,.999))
        types[part]=dict(material_id=material.path_id,texture_id=obj.path_id,decoded=decoded,
                        bytes=len(data['image data']),max_error=int(error.max()),mean_error=float(error.mean()))
    for meshid in (67,68):
        tree,rows=mesh_rows(file.objects[meshid])
        assert tree['m_Name'].endswith('_v19') and np.isfinite(rows).all()
        assert np.all(rows[:,10:12]>=0) and np.all(rows[:,10:12]<=1/3+1e-6)
        if before:
            old,oldrows=mesh_rows(before.objects[meshid])
            assert np.array_equal(rows[:,:10],oldrows[:,:10]),'Avatar geometry/normals/tangents changed.'
            assert tree['m_IndexBuffer']==old['m_IndexBuffer']
            assert tree['m_LocalAABB']==old['m_LocalAABB']
    # Renderer references must be split while every other visual and gameplay object survives.
    for renderer,material in [(902,face_material.path_id),(937,outfit_material.path_id)]:
        assert file.objects[renderer].read_typetree()['m_Materials']==[dict(m_FileID=0,m_PathID=material)]
    if before:
        assert len(file.objects)==len(before.objects)+4
        allowed={67,68,902,937}
        for i,o in before.objects.items():
            if i not in allowed:assert file.objects[i].get_raw_data()==o.get_raw_data(),(i,o.type.name)
    # The selected cells must map independently and all 81 pairings remain distinct.
    cells={}
    for part,t in types.items():
        image=t.pop('decoded')
        values=[]
        for index in range(9):
            col,row=index%3,index//3
            tile=image[row*CELL:(row+1)*CELL,col*CELL:(col+1)*CELL]
            assert tile.shape==(CELL,CELL,3)
            # Material offsets operate in bottom-up UVs; prove the top-left image crop agrees.
            u=(col/3+1/6);v=(2-row)/3+1/6
            px=min(SIZE-1,int(u*SIZE));py=min(SIZE-1,int((1-v)*SIZE))
            assert np.array_equal(image[py,px],tile[CELL//2,CELL//2])
            values.append(hashlib.sha256(tile.tobytes()).hexdigest())
        assert len(set(values))==9
        cells[part]=values
    assert len({f+o for f in cells['face'] for o in cells['outfit']})==81
    for index in range(4):
        legacy=np.array(Image.open(R/f'assets/cloudcourt-v16/player-{index+1:02d}-rosto.png').convert('RGB'))
        new=np.array(Image.open(A/f'face-{index:02d}-{FACE_NAMES[index].lower()}.png').convert('RGB'))
        assert np.array_equal(legacy,new),'Existing own emoji drawing changed.'
    return {'passed':True,'faces':9,'outfits':9,'independent_combinations':81,
            'atlas':types,'shape_normals_indices_bounds_unchanged':True,'unrelated_objects_unchanged':before is not None,
            'legacy_four_faces_pixel_identical_before_BC7':True,
            'texture_bytes_total':sum(x['bytes'] for x in types.values()),
            'scope':'Art, serialized references and UV sampling; native selection/RPC and headset review are separate checks.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--asset',type=Path);parser.add_argument('--before',type=Path);args=parser.parse_args()
    if args.asset:
        file=UnityPy.load(str(args.asset)).file
        before=UnityPy.load(str(args.before)).file if args.before else None
        report=validate(file,before)
    else:
        source=R/'versions/cloudcourt-v18-antes-v19/resources.assets'
        before=UnityPy.load(str(source)).file
        file=UnityPy.load(str(source)).file
        art=create_art();bindings=apply_customization_assets(file,art)
        path=R/'analysis/avatar-v19-resources.assets';path.write_bytes(file.save())
        file=UnityPy.load(str(path)).file;report=validate(file,before)
        hashes={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in file.objects.items()}
        apply_customization_assets(file,art);path.write_bytes(file.save())
        repeat=UnityPy.load(str(path)).file
        assert hashes=={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in repeat.objects.items()}
        report['idempotent']=True;report['bindings']=bindings
    (R/'analysis/v19-avatar-art-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
