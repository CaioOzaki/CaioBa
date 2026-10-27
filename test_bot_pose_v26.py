"""Production v26 visual skeleton pose, built only in an isolated native fixture.

Runs v24 recipient/wire/ace regressions plus behind-body, neck limit, hierarchy,
dead Unity object and second-match cache tests. No game DLL/assets are changed.
"""
from pathlib import Path
import ctypes, hashlib, json, os, subprocess, sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
import test_bot_target_v24 as old

POSE_TESTS=r'''
static void setup_pose_v26(){
 celebration_reset_v21();init();random_calls=look_calls=solver_leaks=0;solver_root_expected=(Q4){0,0,0,1};
 PTR(objects[15],0x38)=objects[33];PTR(objects[33],0x68)=objects[34];PTR(objects[34],0x10)=objects[32];
 *(V3*)((char*)objects[34]+0x60)=(V3){0,0,1};ts[32].p=(V3){0,1.6f,0};
 INT(objects[23],0x18)=2;PTR(objects[24],0x20)=objects[16];PTR(objects[24],0x28)=objects[27];
 INT(objects[16],0x28)=INT(objects[27],0x28)=0;INT(objects[16],0x100)=1001;INT(objects[27],0x100)=2002;
 INT(objects[17],0x7c)=0;INT(objects[17],0x9c)=3;INT(objects[17],0x98)=2002;
 ts[16].p=(V3){.01f,1.6f,1};ts[27].p=(V3){0,1.6f,-4};
}
EXPORT int test_pose_v26(){
 int checks=0;
 // Independent peers/formats and reversed rosters all consume the same rank.
 for(int peer=0;peer<4;peer++){
  setup_pose_v26();doubles_enabled=peer<2;quartet_enabled=peer>=2;
  if(peer&1){PTR(objects[24],0x20)=objects[27];PTR(objects[24],0x28)=objects[16];}
  Q4 original={0,.2f,0,.9797959f};ts[39].q=original;solver_root_expected=original;
  ts[13].q=(Q4){0,.70710678f,0,.70710678f};ts[14].q=(Q4){0,.3f,0,.9539392f};
  V3 rootpos=ts[13].p,modelpos=ts[14].p;Q4 gameplay=ts[13].q,model=ts[14].q;
  int wire=0x24020000;celebration_point_wire_v24(objects[17],0,wire);
  for(int frame=0;frame<50;frame++){
   if(frame==25)ts[27].p=(V3){-4,1.6f,-2};
   celebration_bot_v21(objects[13]);
   for(int pass=14;pass<=15;pass++){
    bot_ik_hook(objects[pass],0);
    V3 dir=sub(ts[27].p,ts[13].p);dir.y=0;dir=mul(dir,1/sqroot(dot(dir,dir)));
    if(!nearv(rotate(worldq(39),(V3){0,0,1}),dir))return -1;
    // Torso, idle arm and feet inherit this same visual-root yaw.
    for(int i=40;i<=42;i++)if(!nearv(rotate(worldq(i),(V3){0,0,1}),dir))return -2;
    if(rooted(celebration_target_v24)!=objects[27]||!ts[8].active)return -3;
    V3 headforward=rotate(worldq(32),(V3){0,0,1});
    V3 gaze=sub(celebration_gaze_v24(objects[27]),position(objects[32]));gaze=mul(gaze,1/sqroot(dot(gaze,gaze)));
    if(!nearv(headforward,gaze))return -4;
    if(rotate(worldq(32),(V3){0,1,0}).y<.81914f)return -16;
    if(!nearv(position(objects[8]),position(objects[12]))||!nearv(rotate(worldq(8),(V3){0,0,1}),dir))return -5;
    if(!nearv(ts[13].p,rootpos)||!nearv(ts[14].p,modelpos)||ts[13].q.w!=gameplay.w||ts[14].q.w!=model.w)return -6;
    checks++;
   }
  }
  // No per-frame target RNG; body/arm/head locals restore for next solver.
  if(random_calls||solver_leaks)return -7;
  celebration_reset_v21();if(ts[8].active||ts[12].scale.x!=1||ts[39].q.y!=original.y||ts[39].q.w!=original.w)return -8;
  for(int i=10;i<13;i++)if(ts[i].q.w<.9999f)return -9;
  if(rooted(bot_celebrations_v21[0].bot)||rooted(bot_celebrations_v21[0].rig)||bot_celebrations_v21[0].bound)return -10;
  checks++;
 }
 // Pathological head tracking remains within 35-degree pitch / 60-degree yaw.
 setup_pose_v26();PTR(objects[27],0x80)=objects[44];PTR(objects[44],0x30)=objects[45];
 ts[45].p=(V3){100,100,100};celebration_point_wire_v24(objects[17],0,0x24020000);celebration_bot_v21(objects[13]);bot_ik_hook(objects[15],0);
 V3 f=rotate(worldq(32),(V3){0,0,1});float horizontal=sqroot(f.x*f.x+f.z*f.z);
 if(f.y>horizontal*.70022f||-f.z<horizontal*.49999f||rotate(worldq(32),(V3){0,1,0}).y<.81914f)return -11;checks++;
 // Destroyed skeleton: restore only surviving Unity objects, release binding,
 // then rebind a replacement Root_jnt in the next match even with same bot.
 dead_index=39;bot_ik_hook(objects[15],0);
 if(bot_celebrations_v21[0].bound||rooted(bot_celebrations_v21[0].rig)||ts[8].active||dead_access)return -12;checks++;
 celebration_reset_v21();dead_index=-1;rig_index=43;ts[43].parent=14;ts[43].q=(Q4){0,0,0,1};ts[10].parent=ts[32].parent=43;
 celebration_point_wire_v24(objects[17],0,0x24020000);celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);
 if(rooted(bot_celebrations_v21[0].rig)!=objects[43]||!ts[8].active)return -13;checks++;
 celebration_reset_v21();if(ts[43].q.w<.9999f||ts[12].scale.x!=1)return -14;checks++;
 // A destroyed bot/component must not enter game APIs or the native solver.
 dead_index=13;celebration_bot_v21(objects[13]);dead_index=14;int calls=solver_calls;bot_ik_hook(objects[14],0);
 if(solver_calls!=calls||dead_access)return -15;checks++;
 dead_index=-1;rig_index=39;return checks;
}
'''

def prepare():
 old.EXTRA=old.EXTRA.replace('static int random_pick,random_calls,look_calls,solver_leaks;','static int random_pick,random_calls,look_calls,solver_leaks;static Q4 solver_root_expected={0,0,0,1};')
 old.EXTRA=old.EXTRA.replace('if(look_calls){V3 forward=rotate(worldq(32),(V3){0,0,1});if(forward.x>.01f||forward.x<-.01f)solver_leaks++;}', 'if(look_calls){Q4 q=ts[rig_index].q;if(q.y!=solver_root_expected.y||q.w!=solver_root_expected.w)solver_leaks++;}')
 old.HARNESS=old.HARNESS.replace('if(eq(s,"CC_WinThumb"))','if(eq(s,"Root_jnt"))return ts[rig_index].id;if(eq(s,"CC_WinThumb"))')
 old.HARNESS=old.HARNESS.replace('static int alive(void* p){return p!=0;}','static int dead_index=-1,dead_access,rig_index=39;\nstatic int alive(void* p){return p!=0&&(dead_index<0||p!=objects[dead_index]);}')
 # find_child appears after alive, so rig_index is already declared there.
 old.HARNESS=old.HARNESS.replace('ts[16].p=(V3){2,1,0};','ts[39].parent=14;ts[10].parent=39;ts[32].parent=39;for(int i=40;i<=42;i++)ts[i].parent=39;\n ts[16].p=(V3){2,1,0};')
 old.HARNESS=old.HARNESS.replace('static void setlocalq(void* o,Q4 q,void* m){','static void setlocalq(void* o,Q4 q,void* m){if(index(o)==dead_index){dead_access++;return;}')
 # Report stale API access without dereferencing any dead fixture object.
 old.HARNESS=old.HARNESS.replace('static void setglobalq(void* o,Q4 q,void* m){','static void setglobalq(void* o,Q4 q,void* m){if(index(o)==dead_index){dead_access++;return;}')
 # Legacy v24 fixture checks its saved native head before each solver. Its
 # identity root baseline is restored, so head tracking cannot leak backward.
 source=old.prepare();h=source.read_text().replace('ts[64].parent=39;','ts[32].parent=39;').replace('ts[16].p=(V3){.1f,1.6f,0};','ts[16].p=(V3){.1f,1.6f,3};').replace('look_calls!=2','look_calls!=4').replace('EXPORT int DllMain(',POSE_TESTS+'\nEXPORT int DllMain(')
 folder=R/'tools/v26-bot-pose';folder.mkdir(exist_ok=True)
 p=folder/'pose.c';p.write_text(h);return p

def run():
 source=prepare();dll=source.with_suffix('.dll');cache=str(source.parent/'cache')
 env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=cache,ZIG_LOCAL_CACHE_DIR=cache)
 p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(dll),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
 assert p.returncode==0,(p.returncode,p.stdout+p.stderr)
 lib=ctypes.CDLL(str(dll));results={}
 for name,expected in [('test_target_v24',129),('test_wire_v24',60),('test_ace_v24',9),('test_pose_v26',409)]:
  got=getattr(lib,name)();assert got==expected,(name,got,expected);results[name]=got
 result=dict(passed=True,native_checks=results,production_sha256=hashlib.sha256((R/'hand_visuals_v21.c').read_bytes()).hexdigest(),
  cases=['recipient behind bot turns complete decorative skeleton','head/torso/idle arm/legs/thumb agree after both hostile IK passes','moving teammate keeps stable recipient','4 independent peer/format fixtures and reversed roster order','no bot gameplay/model transform movement or rotation','head limited to 60 degree yaw and 35 degree pitch','whistle restores original skeleton root/arm/head locals and hand scale','reset releases cached roots','destroyed rig releases binding without dead-object API calls','second match with same bot binds replacement skeleton','destroyed bot/IK component ignored'],
  scope='Production C compiled in isolated hierarchical Unity/FinalIK fixtures; no shipped DLL/assets written, no live VR claim')
 (R/'analysis/v26-bot-pose-native-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()


