from pathlib import Path
import hashlib,json,shutil,sys,struct
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import pefile
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'analysis/native-patch-manifest.json').read_text(encoding='utf8'));native=H(R/'working/GameAssembly.dll');assert native==m['modified_sha256']
reports={}
for name in ['v30-rules-integrated-tests.json','v30-ball-spawn-integrated-tests.json']:
 d=json.loads((R/'analysis'/name).read_text(encoding='utf8'));assert d['passed'] and d['sha256']==native,name;reports[name]=dict(passed=True,sha256=d['sha256'])
p=pefile.PE(str(R/'working/GameAssembly.dll'));ex=m['exports']
for row in m['patches']:
 if row.get('kind')=='branch_neutralized':assert p.get_data(row['rva'],row['length'])==b'\x90'*row['length'];continue
 inst=p.get_data(row['rva'],5);assert inst[0]==(0xe8 if row.get('kind')=='call' else 0xe9)
 assert row['rva']+5+struct.unpack('<i',inst[1:5])[0]==row['hook'],row['name']
for addr in (0xeed321,0xeed386):
 row=next(x for x in m['patches'] if x['rva']==addr);assert row['hook']==ex['hit_haptic_dispatch_v29']
assert any(x['name']=='bot_character_v29' and x['rva']==0x270380 for x in m['patches'])
assert not any(x.startswith('probe') or x.startswith('customization_stats') for x in ex)
assert not getattr(p,'DIRECTORY_ENTRY_IMPORT',None) or len(p.DIRECTORY_ENTRY_IMPORT)==len(pefile.PE(str(R/'backup/GameAssembly.dll')).DIRECTORY_ENTRY_IMPORT)
for sec in p.sections:
 if sec.Name.startswith(b'.vf'):assert not(sec.Characteristics&0x20000000 and sec.Characteristics&0x80000000)
# Record reviewed integration ordering at shared native entry points.
contracts={}
def contract(file,words):
 s=(R/file).read_text(encoding='utf-8-sig');positions=[s.index(w) for w in words];assert positions==sorted(positions),(file,words);contracts[file]=words
contract('spin_mod.c',['set_begin(body,part);','hit_feedback_begin_v29(body,part,ball,collision);','collision_trampoline(body,part,ball,collision,method);','hit_feedback_end_v29();','set_end();'])
contract('hand_visuals_v21.c',['bots_ik_before_v29(ik);','if(s)celebration_restore_v22(s);','bot_ik_trampoline(ik,m);','if(s)celebration_pose_v22(s);','bots_ik_after_v29(ik);'])
contract('online_2v2.c',['stats_motion_v29(ball,pos,velocity,hit,touch,team);','client_motion_trampoline(ball,pos,velocity,hit,touch,team,context,m);'])
contract('mode_2v2.c',['if(training_requested_v29())training_begin_v29(o);','stats_prepare_v29(o);','game_go_trampoline(o,m);'])
contract('identity_v16.c',['in_game_active_trampoline(page,arg,m);','FN(0x314870,void(*)(void*,void*))(page,0);'])
source_hashes={p.name:H(p) for p in R.glob('*.c') if p.name in ['spin_mod.c','mode_2v2.c','training_v29.c','bots_refine_v29.c','hit_feedback_v29.c','stats_v29.c','rewards_v29.c','refinement_v29.c','identity_v16.c','customization_v28.c','match_settings_v30.c','settings_audio_v28.c','online_2v2.c']}
r=dict(passed=True,sha256=native,patch_count=len(m['patches']),hookcontracts=contracts,source_sha256=source_hashes,regressions=reports,exact_haptic_call_sites=True,native_bot_character_hook=True,no_debug_exports=True,writable_executable_sections=False,headset_tested=False,two_PC_tested=False)
(R/'analysis/v30-native-integration.json').write_text(json.dumps(r,indent=2),encoding='utf8')
a=json.loads((R/'analysis/v30-composed-assets.json').read_text(encoding='utf8'))
for row in a['files']:
 name=row['path'];candidate=R/'visuals-v30'/name;assert H(candidate)==row['sha256']
 if name!='GameAssembly.dll':shutil.copyfile(candidate,R/'working/VolleyballFever_Data'/name)
assert H(R/'working/GameAssembly.dll')==native
print(json.dumps(dict(passed=True,native=native,patches=len(m['patches']),assets_copied=16)))
