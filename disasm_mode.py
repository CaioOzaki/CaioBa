exec(open(__file__.replace('disasm_mode.py','analyze_2v2.py')).read().split('spans=')[0])
spans=[(0x252840,0x180),(0xef6fb0,0x50),(0x271be0,0x580),(0x254e00,0x460),(0xef4320,0x40)]
out=[]
for a,n in spans:
 out.append('\n### '+names.get(a,hex(a)))
 for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
  extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x') else ''
  out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(R/'analysis/mode-callers.txt').write_text('\n'.join(out))
for e in p.DIRECTORY_ENTRY_EXPORT.symbols:
 if e.name and e.name.decode() in ['il2cpp_gchandle_free','il2cpp_gc_wbarrier_set_field']:print(e.name,hex(e.address))
for x in methods:
 if any(k in x['Name'] for k in ['BotArea$$','Component$$get_gameObject','SettingsChanged','GetMovement','get_CompletedTask','Bot$$HitBall']):print(hex(x['Address']),x['Name'],x['Signature'])
