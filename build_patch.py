"""Build a version-isolated experimental native patch in the working copy.
Never writes into the Steam installation. Keeps original binary as backup.
"""
import sys,pathlib,struct,json,hashlib,ctypes,math
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import pefile,capstone
align=lambda n,a:(n+a-1)//a*a
target=R/'working/GameAssembly.dll'
backup=R/'backup/GameAssembly.dll'
backup.parent.mkdir(exist_ok=True)
if not backup.exists():backup.write_bytes(target.read_bytes())
original=backup.read_bytes(); p=pefile.PE(data=original)
q=pefile.PE(str(R/'tools/spin-native.dll'))
assert p.OPTIONAL_HEADER.SizeOfImage==0x1950000
assert p.FILE_HEADER.Machine==0x8664
assert not getattr(q,'DIRECTORY_ENTRY_IMPORT',[])
delta=p.OPTIONAL_HEADER.SizeOfImage-0x1000
assert delta==0x194f000
image=bytearray(q.get_memory_mapped_image())
exports={x.name.decode():x.address for x in q.DIRECTORY_ENTRY_EXPORT.symbols}
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64);md.detail=True
patches=[]
entries=[('collision',0xeeb3b0),('random',0x77f430),('late',0x77ec30),
 ('solo_awake',0xef3ff0),('solo_entry',0xef73c0),('main_menu',0xef6fb0),('solo_day',0xef4260),('solo_night',0xef42a0),
 ('solo_back',0xef41c0),('solo_start',0xef4520),('game_go',0x253660),('spawn_bot',0x254e00),
 ('add_player',0x30cfb0),('bot_body',0x271460),('pass_target',0x270d00),
 ('tracked_touch',0x253d30),('bot_hit',0x26fbb0),('serve_routine',0x25ab20),('bot_assess',0x26f190),('player_jump',0x329df0),('team_update',0x30d0d0),('local_serve',0x259160),('hand_find',0x312c50)]
entries += [('online_entry',0xef7230),('network_version',0x31a240),('clear_teams',0x2529c0),('online_setup',0x254a00),('choose_team',0x31b1b0),('online_awake',0x3846d0),('client_motion',0x77de30),('client_end',0x252c10)]
entries += [('avatar_update',0xeefbc0),('bot_jump',0x270020)]
if 'probe_start_hook' in exports:entries += [('probe_start',0xef74f0),('probe_solo',0xef4620)]
for name,rva in entries:
    n=0
    for i in md.disasm(p.get_data(rva,32),rva):
        assert not i.group(capstone.CS_GRP_JUMP) and not i.group(capstone.CS_GRP_CALL)
        assert not any(op.type==capstone.x86.X86_OP_MEM and op.mem.base==capstone.x86.X86_REG_RIP for op in i.operands)
        n+=i.size
        if n>=5:break
    t=exports[name+'_trampoline']; hook=exports[name+'_hook']+delta
    assert n+5<=32
    image[t:t+n]=p.get_data(rva,n)
    image[t+n:t+n+5]=b'\xe9'+struct.pack('<i',rva+n-(t+delta+n+5))
    patches.append(dict(name=name,rva=rva,length=n,original=p.get_data(rva,n).hex(),hook=hook,trampoline=t+delta))
# ASLR: rebase helper absolute pointers, then merge its relocation entries.
extra_reloc=[]
for block in getattr(q,'DIRECTORY_ENTRY_BASERELOC',[]):
    entries=[]
    for e in block.entries:
        if e.type==0:continue
        assert e.type==10
        struct.pack_into('<Q',image,e.rva,struct.unpack_from('<Q',image,e.rva)[0]+delta)
        extra_reloc.append((e.rva+delta,e.type))
# Unwind metadata for new native frames is added to the original exception table.
exc=p.OPTIONAL_HEADER.DATA_DIRECTORY[3]
exceptions=[struct.unpack_from('<III',p.get_data(exc.VirtualAddress,exc.Size),i) for i in range(0,exc.Size,12)]
qe=q.OPTIONAL_HEADER.DATA_DIRECTORY[3]
for i in range(0,qe.Size,12):
    a,b,u=struct.unpack_from('<III',q.get_data(qe.VirtualAddress,qe.Size),i)
    flags=image[u]>>3
    assert flags&4==0, 'Chained unwind requires explicit relocation'
    exceptions.append((a+delta,b+delta,u+delta))
exceptions.sort()
exception_bytes=b''.join(struct.pack('<III',*e) for e in exceptions)
rel=p.OPTIONAL_HEADER.DATA_DIRECTORY[5]
reloc_bytes=bytearray(p.get_data(rel.VirtualAddress,rel.Size))
for page in sorted(set(rva&~4095 for rva,typ in extra_reloc)):
    entries=[(typ<<12)|(rva&4095) for rva,typ in extra_reloc if rva&~4095==page]
    if len(entries)%2:entries.append(0)
    reloc_bytes+=struct.pack('<II',page,8+2*len(entries))+struct.pack('<'+'H'*len(entries),*entries)
# Four sections keep code executable/read-only and state non-executable.
text=next(s for s in q.sections if s.Name.startswith(b'.text'))
ro=next(s for s in q.sections if s.Name.startswith(b'.rdata'))
data=next(s for s in q.sections if s.Name.startswith(b'.data'))
pdata=next(s for s in q.sections if s.Name.startswith(b'.pdata'))
meta_start=pdata.VirtualAddress
meta_end=align(q.OPTIONAL_HEADER.SizeOfImage,4096)
meta=bytearray(image[meta_start:meta_end]);meta.extend(b'\0'*(align(len(meta),16)-len(meta)))
exception_rva=meta_start+delta+len(meta);meta+=exception_bytes
meta.extend(b'\0'*(align(len(meta),4)-len(meta)))
reloc_rva=meta_start+delta+len(meta);meta+=reloc_bytes
sections=[(b'.vfcode',0x1000,bytes(image[0x1000:ro.VirtualAddress]),0x60000020),
          (b'.vfread',ro.VirtualAddress,bytes(image[ro.VirtualAddress:data.VirtualAddress]),0x40000040),
          (b'.vfstate',data.VirtualAddress,bytes(image[data.VirtualAddress:meta_start]),0xc0000040),
          (b'.vfmeta',meta_start,bytes(meta),0x40000040)]
result=bytearray(original)
header=p.sections[-1].get_file_offset()+40
assert header+40*len(sections)<=p.OPTIONAL_HEADER.SizeOfHeaders
for idx,(name,start,content,flags) in enumerate(sections):
    raw=align(len(result),p.OPTIONAL_HEADER.FileAlignment)
    result.extend(b'\0'*(raw-len(result)))
    result.extend(content); rawsize=align(len(content),p.OPTIONAL_HEADER.FileAlignment)
    result.extend(b'\0'*(rawsize-len(content)))
    struct.pack_into('<8sIIIIIIHHI',result,header+40*idx,name,len(content),start+delta,rawsize,raw,0,0,0,0,flags)
    final_end=start+delta+len(content)
for item in patches:
    offset=p.get_offset_from_rva(item['rva'])
    result[offset:offset+item['length']]=b'\xe9'+struct.pack('<i',item['hook']-item['rva']-5)+b'\x90'*(item['length']-5)
callsite=0xeed250
callbytes=p.get_data(callsite,5)
assert callbytes==b'\xe8'+struct.pack('<i',0x77e5c0-callsite-5)
motion_hook=exports['motion_hook']+delta
result[p.get_offset_from_rva(callsite):p.get_offset_from_rva(callsite)+5]=b'\xe8'+struct.pack('<i',motion_hook-callsite-5)
patches.append(dict(name='accepted_local_hit',rva=callsite,length=5,original=callbytes.hex(),hook=motion_hook,kind='call'))
for name,site,original_target,hookname in [
 ('score_reason',0x2584e1,0x14ba70,'score_box_hook'),
 ('four_touches',0x253de8,0x2533a0,'four_point_hook'),
 ('double_touch',0x253e10,0x2533a0,'double_point_hook'),
 ('grounded_point',0x252606,0x2533a0,'ground_point_hook'),
 ('front_row_setup',0x254181,0xef32b0,'front_row_hook'),
 ('front_row_rotation',0x2526d2,0xef32b0,'front_row_hook'),
 ('player_speed',0x31bf73,0xef33b0,'player_speed_hook'),
 ('reception_assist',0xeecdbb,0xa12690,'reception_assist_hook'),
 ('connect_fixed_region',0x319759,0x60acf0,'connect_settings_hook'),
 ('connect_auto_region',0x31979c,0x60abf0,'connect_default_hook'),
 ('bot_serve_position',0x25ad60,0xb74de0,'bot_serve_position_hook'),('hand_serve_position',0x259664,0xb756b0,'hand_serve_position_hook')]:
    before=p.get_data(site,5)
    assert before==b'\xe8'+struct.pack('<i',original_target-site-5)
    hook=exports[hookname]+delta;offset=p.get_offset_from_rva(site)
    result[offset:offset+5]=b'\xe8'+struct.pack('<i',hook-site-5)
    patches.append(dict(name=name,rva=site,length=5,original=before.hex(),hook=hook,kind='call'))
site=0x253060
before=b'\x33\xd2\xe9'+struct.pack('<i',0x253e30-site-7)
assert p.get_data(site,7)==before
hook=exports['net_new_rally_hook']+delta;offset=p.get_offset_from_rva(site)
result[offset:offset+7]=b'\xe9'+struct.pack('<i',hook-site-5)+b'\x90\x90'
patches.append(dict(name='net_new_rally',rva=site,length=7,original=before.hex(),hook=hook))
struct.pack_into('<H',result,p.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),p.FILE_HEADER.NumberOfSections+4)
struct.pack_into('<I',result,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(final_end,4096))
struct.pack_into('<II',result,exc.get_file_offset(),exception_rva,len(exception_bytes))
struct.pack_into('<II',result,rel.get_file_offset(),reloc_rva,len(reloc_bytes))
struct.pack_into('<I',result,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),0)
target.write_bytes(result)
check=pefile.PE(data=result)
assert check.OPTIONAL_HEADER.DATA_DIRECTORY[3].Size==len(exception_bytes)
assert len(check.DIRECTORY_ENTRY_EXCEPTION)==len(exceptions)
for item in patches:
    assert check.get_data(item['rva'],1)==(b'\xe8' if item.get('kind')=='call' else b'\xe9')
    assert check.get_section_by_rva(item['hook']).Characteristics&0x20000000
for section in check.sections:
    assert not (section.Name.startswith(b'.vf') and section.Characteristics&0x20000000 and section.Characteristics&0x80000000)
manifest={'original_sha256':hashlib.sha256(original).hexdigest(),'modified_sha256':hashlib.sha256(result).hexdigest(),'patches':patches,'exports':{k:v+delta for k,v in exports.items()},'extra_aslr_relocations':extra_reloc,'new_exception_entries':qe.Size//12,'offline_only':False,'network_version':'CaioBa-2v2-v15 / CaioBa-4v4-v15','status':'v15 checkpoint; VR and live two-PC validation pending'}
(R/'analysis/native-patch-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))

