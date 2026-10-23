"""Raise all court net variants by 40 cm, including their colliders."""
import pathlib,sys,json
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
OUT=R/'visuals-v14';BASE=R/'versions/v13-antes-personagens'
report={}
for name in ['resources.assets','level0','level1','level2','level3']:
    f=UnityPy.load(str(OUT/name if name=='resources.assets' else BASE/name)).file
    gos={o.path_id:o.read_typetree() for o in f.objects.values() if o.type.name=='GameObject'}
    ts={o.path_id:o.read_typetree() for o in f.objects.values() if o.type.name=='Transform'}
    changed=[]
    for id,t in ts.items():
        go=gos[t['m_GameObject']['m_PathID']];n=go['m_Name'];parent=ts.get(t['m_Father']['m_PathID'])
        pn=gos[parent['m_GameObject']['m_PathID']]['m_Name'] if parent else ''
        p=t['m_LocalPosition'];s=t['m_LocalScale']
        if n=='Net':p['y']+=.4
        elif n.startswith('NetPole'):s['y']*=1.2
        elif pn=='Net':continue
        elif n in ['Net frame visual','Net frame collider','Net net','Net net small']:p['y']+=.4
        elif n in ['Net frame','Net invisible collider']:p['y']+=.2;s['y']+=.4
        else:continue
        f.objects[id].save_typetree(t);changed.append(id)
    if name=='level3':
        # Undo baked static batching for moving net details; use prefab-local meshes.
        meshes={'pCylinder15':63,'pCylinder16':65,'NetFrame':64}
        for go in gos.values():
            if go['m_Name'] not in meshes:continue
            for c in go['m_Component']:
                o=f.objects[c['component']['m_PathID']];d=o.read_typetree()
                if o.type.name=='MeshFilter':d['m_Mesh']={'m_FileID':3,'m_PathID':meshes[go['m_Name']]}
                elif o.type.name=='MeshRenderer':
                    d['m_StaticBatchInfo']={'firstSubMesh':0,'subMeshCount':0};d['m_StaticBatchRoot']={'m_FileID':0,'m_PathID':0}
                    d['m_LightmapIndex']=65535
                else:continue
                o.save_typetree(d)
    if name=='level0':
        for id,g in gos.items():
            if g['m_Name']=='Daily Challenge':g['m_IsActive']=False;f.objects[id].save_typetree(g)
    (OUT/name).write_bytes(f.save());report[name]=changed
(OUT/'net-height.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
