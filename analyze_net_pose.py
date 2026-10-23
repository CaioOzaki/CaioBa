exec(open(__file__.replace('analyze_net_pose.py','analyze_2v2.py')).read().split('spans=')[0])
spans=[(0xeea620,0x400),(0x253060,0x10),(0x252c10,0x1f0),(0x3154d0,0x240)]
out=[]
for a,n in spans:
 out.append('\n### '+names.get(a,hex(a)))
 for i in md.disasm(p.get_data(a,n),p.OPTIONAL_HEADER.ImageBase+a):
  extra=names.get(int(i.op_str,16)-p.OPTIONAL_HEADER.ImageBase,'') if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x') else ''
  out.append(f'{i.address-p.OPTIONAL_HEADER.ImageBase:x}: {i.mnemonic} {i.op_str} ; {extra}')
(R/'analysis/net-pose-flow.txt').write_text('\n'.join(out))

