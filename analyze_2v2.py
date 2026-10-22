import pathlib,sys,json
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import pefile,capstone
p=pefile.PE(str(R/'backup/GameAssembly.dll'));methods=json.loads((R/'analysis/script.json').read_text())['ScriptMethod'];names={m['Address']:m['Name'] for m in methods}
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64)
spans=[(0xef3ff0,0x6d0),(0x2540f0,0x910),(0x253660,0x350),(0x26fbb0,0x470),(0x270d00,0x2d0)]
out=[]
for a,n in spans:
    out.append('\n### '+names.get(a,hex(a)))
    for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
        extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x') else ''
        out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(R/'analysis/2v2-disassembly.txt').write_text('\n'.join(out))
for e in p.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.name and e.name.decode() in ['il2cpp_string_new','il2cpp_array_new','il2cpp_gchandle_new','il2cpp_gchandle_get_target']:print(e.name,hex(e.address))
for x in methods:
    if any(k in x['Name'] for k in ['Settings$$get_movementSpeed','Text$$set_text','Selectable$$set_interactable','PageController$$','Team$$']):
        print(hex(x['Address']),x['Name'],x['Signature'])
