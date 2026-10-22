exec(open(__file__.replace('analyze_reception.py','analyze_2v2.py')).read().split('spans=')[0])
spans=[(0x329df0,0x1c0),(0x329500,0x230),(0x32a6b0,0x210),(0x270020,0x30),(0x26f190,0x460)]
out=[]
for a,n in spans:
 out.append('\n### '+names.get(a,hex(a)))
 for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
  extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x') else ''
  out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(R/'analysis/jump-states.txt').write_text('\n'.join(out))
