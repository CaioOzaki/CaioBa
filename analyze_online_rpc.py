exec(open(__file__.replace('analyze_online_rpc.py','analyze_2v2.py')).read().split('spans=')[0])
spans=[(0x31b1b0,0x250),(0x2529c0,0x250),(0x252f10,0x160),(0x252910,0xb0)]
out=[]
for a,n in spans:
 out.append('\n### '+names.get(a,hex(a)))
 for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
  extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x') else ''
  out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(R/'analysis/online-rpc-flow.txt').write_text('\n'.join(out))

