import sys, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/python'))
import UnityPy, pefile, capstone
m=json.loads((ROOT/'analysis/script.json').read_text())['ScriptMethod']
keys=['Collision$$GetContact','Rigidbody$$get_angularVelocity','Rigidbody$$get_isKinematic','Time$$get_deltaTime','PhysicalBodyPart$$GetVelocityAtPoint','Volleyball$$get_radius','Rigidbody$$set_maxAngularVelocity']
for x in m:
    if any(k in x['Name'] for k in keys): print(x)
p=pefile.PE(str(ROOT/'working/GameAssembly.dll'))
names={x['Address']:x['Name'] for x in m}
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
out=[]
for a,n in [(0x31a450,0xa0),(0xeea0e0,0x1a0),(0x77f080,0x2b0)]:
    out.append('\n### '+names.get(a,hex(a)))
    for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
        extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic=='call' and i.op_str.startswith('0x') else ''
        out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(ROOT/'analysis/extra-disassembly.txt').write_text('\n'.join(out))
print('\n'.join(out[:50]))
e=UnityPy.load(str(ROOT/'working/VolleyballFever_Data'))
for o in e.objects:
    if o.type.name=='Mesh' and o.assets_file.name=='resources.assets' and o.path_id==62:
        (ROOT/'analysis/Volleyball.obj').write_text(o.read().export())
    if o.type.name in ['MonoBehaviour','GameObject','Rigidbody','SphereCollider'] and o.assets_file.name=='resources.assets':
        try:
            t=o.read_typetree()
            if o.type.name=='MonoBehaviour' or 'ball' in str(t).lower():
                (ROOT/'analysis'/f'resources-{o.path_id}-{o.type.name}.json').write_text(json.dumps(t,indent=2,default=lambda x:list(x)))
        except Exception: pass
