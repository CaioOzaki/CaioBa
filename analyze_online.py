exec(open(__file__.replace('analyze_online.py','analyze_2v2.py')).read().split('spans=')[0])
spans=[(0x31a240,0xf0),(0x3197b0,0xc0),(0x315d40,0x6a0),(0x314e70,0x120),(0x2546f8,0x700)]
out=[]
for a,n in spans:
 out.append('\n### '+names.get(a,hex(a)))
 for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
  extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x') else ''
  out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(R/'analysis/online-flow.txt').write_text('\n'.join(out))

