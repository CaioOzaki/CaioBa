"""Compile the production celebration module in an isolated hierarchical fixture.

The solver deliberately points at a different ball after each pass. The native
calibrated-head stub and the arm must then point at the same selected human.
No shipped DLL, asset, or historical test fixture is overwritten.
"""
from pathlib import Path
import ctypes, hashlib, json, os, subprocess, sys
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R),str(R/'tools/python')]
from test_hands_v22 import HARNESS

EXTRA=r'''
static int random_pick,random_calls,look_calls,solver_leaks;
static int touchid(void* p,void* m){return INT(p,0x100);}
static int choose(int lo,int hi,void* m){random_calls++;return random_pick%hi;}
static void lookat(void* bone,V3 direction,float weight,void* m){
 look_calls++;void* head=PTR(bone,0x10);int i=index(head);
 V3 from=rotate(worldq(i),*(V3*)((char*)bone+0x60));
 V3 c={from.y*direction.z-from.z*direction.y,from.z*direction.x-from.x*direction.z,from.x*direction.y-from.y*direction.x};
 Q4 q={c.x,c.y,c.z,1+dot(from,direction)};
 if(q.w<.00001f&&dot(c,c)<.00001f)q=(Q4){0,1,0,0};else q=normalized(q);
 setglobalq(head,product(q,worldq(i)),0);
}
static void fake_solver(void* ik){
 // Identity head points +Z, while the native look solver tracks a ball at -Z.
 // Its incoming pose must have been restored, never the celebration target.
 if(look_calls){V3 forward=rotate(worldq(32),(V3){0,0,1});if(forward.x>.01f||forward.x<-.01f)solver_leaks++;}
 ts[32].q=(Q4){0,1,0,0};
}
'''

TESTS=r'''
static int nearv(V3 a,V3 b){return dot(sub(a,b),sub(a,b))<.00002f;}
static int verify_target(void* expected){
 if(rooted(celebration_target_v24)!=expected)return 0;
 V3 delta=sub(celebration_gaze_v24(expected),position(objects[32]));delta=mul(delta,1/sqroot(dot(delta,delta)));
 if(!nearv(rotate(worldq(32),(V3){0,0,1}),delta))return 0;
 V3 dir=sub(position(expected),position(objects[13]));dir.y=0;dir=mul(dir,1/sqroot(dot(dir,dir)));
 if(!nearv(bot_celebrations_v21[0].toward,dir))return 0;
 V3 wrist=position(objects[12]),thumb=position(objects[8]);return nearv(wrist,thumb)&&ts[8].active;
}
EXPORT int test_target_v24(){
 init();int checks=0;
 // A real LookAtIK/IKSolverLookAt/LookAtBone graph, separate from arm refs.
 PTR(objects[15],0x38)=objects[33];PTR(objects[33],0x68)=objects[34];PTR(objects[34],0x10)=objects[32];
 *(V3*)((char*)objects[34]+0x60)=(V3){0,0,1};ts[32].p=(V3){0,1.6f,0};
 int who[4]={16,27,35,36};int ids[4]={1001,2002,50003,700004};
 for(int i=0;i<4;i++){INT(objects[who[i]],0x28)=0;INT(objects[who[i]],0x100)=ids[i];PTR(objects[24],0x20+i*8)=objects[who[i]];ts[who[i]].p=(V3){(i&1)?-2.f:2.f,1.6f,(float)i+1};}
 INT(objects[23],0x18)=4;INT(objects[17],0x7c)=0;INT(objects[17],0x9c)=3;INT(objects[17],0x98)=700004;
 PTR(objects[36],0x80)=objects[37];PTR(objects[37],0x30)=objects[38];ts[38].p=(V3){2,2.05f,4};
 int wire=celebration_wire_v24(objects[17],0);if(wire!=0x24040000||random_calls)return -1;
 celebration_point_wire_v24(objects[17],0,wire);celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);
 if(!verify_target(objects[36]))return -2;checks++;
 // The second native pass actively aims at the ball; recipient must win again.
 bot_ik_hook(objects[15],0);if(!verify_target(objects[36])||look_calls!=2||solver_leaks)return -3;checks++;
 // Movement changes both rays, but a closer other human never changes identity.
 ts[36].p=(V3){4,1.8f,-3};ts[38].p=(V3){4,.8f,-3};ts[16].p=(V3){.1f,1.6f,0};
 int f=finds,a=activewrites;
 for(int i=0;i<100;i++){celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);bot_ik_hook(objects[15],0);if(!verify_target(objects[36]))return -4;checks++;}
 if(random_calls||finds!=f||activewrites!=a||solver_leaks)return -5;
 // Another peer can have reversed insertion order. Rank still resolves the
 // full Photon touch id, including ids larger than 16 bits.
 for(int i=0;i<4;i++)PTR(objects[24],0x20+i*8)=objects[who[3-i]];
 celebration_point_wire_v24(objects[17],0,wire);celebration_bot_v21(objects[13]);bot_ik_hook(objects[15],0);
 if(!verify_target(objects[36]))return -6;checks++;
 // Bot point: pick random human once on authority, freeze it for all frames.
 INT(objects[17],0x98)=-13;random_pick=2;wire=celebration_wire_v24(objects[17],0);
 if(wire!=0x24030000||random_calls!=1)return -7;
 celebration_point_wire_v24(objects[17],0,wire);celebration_bot_v21(objects[13]);bot_ik_hook(objects[15],0);
 if(!verify_target(objects[35]))return -8;checks++;
 for(int i=0;i<20;i++){celebration_bot_v21(objects[13]);bot_ik_hook(objects[15],0);if(!verify_target(objects[35]))return -9;checks++;}
 if(random_calls!=1)return -10;
 // Opposing final human touch must not credit an earlier winner/receiver.
 INT(objects[17],0x7c)=1;INT(objects[17],0x98)=700004;random_pick=1;
 wire=celebration_wire_v24(objects[17],0);if(wire!=0x24020000||random_calls!=2)return -11;checks++;
 celebration_point_wire_v24(objects[17],0,wire);celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);if(!verify_target(objects[27]))return -12;
 // A disconnected player may remain a live Unity object; roster membership
 // must still reject it and select one stable eligible teammate.
 for(int i=0;i<3;i++)PTR(objects[24],0x20+i*8)=objects[who[i==0?0:i+1]];INT(objects[23],0x18)=3;
 celebration_bot_v21(objects[13]);bot_ik_hook(objects[15],0);if(!verify_target(objects[16])||random_calls!=2)return -13;checks++;
 // Team switches and invalid/absent humans cannot leave the head/arm posed.
 INT(objects[16],0x28)=1;celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);if(!verify_target(objects[35]))return -14;checks++;
 celebration_reset_v21();if(ts[8].active||ts[12].scale.x!=1||ts[32].q.y<.9999f)return -15;
 for(int i=10;i<13;i++)if(ts[i].q.w<.9999f)return -16;checks++;
 INT(objects[35],0x28)=1;INT(objects[36],0x28)=1;wire=celebration_wire_v24(objects[17],0);
 if(wire!=0x24000000||random_calls!=2)return -17;
 celebration_point_wire_v24(objects[17],0,wire);celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);if(ts[8].active)return -18;checks++;
 if(solver_leaks)return -19;
 return checks;
}
'''

WIRE_STUBS=r'''
static int point_reason,wire_landing_flags,boxed,received_team,received_reason,received_marker,finished;
static int net_first_touch,net_touch_team,net_touch_count;
static int offline(void){return !net;}
static int landing_wire_flags_v20(void){return wire_landing_flags;}
static void* box(void* klass,void* value){boxed=*(int*)value;return &boxed;}
static void client_end_trampoline(void* rules,int team,V3 pos,void* m){received_team=team;}
static void landing_show_v20(V3 pos,int outside){received_marker=outside?2:1;}
static void point_message(void* rules,int team,int reason){received_reason=reason;}
static void finish_team_changes(void){finished++;}
'''
WIRE_TESTS=r'''
EXPORT int test_wire_v24(){
 init();int checks=0,team=0;INT(objects[23],0x18)=2;PTR(objects[24],0x20)=objects[16];PTR(objects[24],0x28)=objects[27];
 INT(objects[16],0x28)=INT(objects[27],0x28)=0;INT(objects[16],0x100)=1001;INT(objects[27],0x100)=2002;
 INT(objects[17],0x7c)=0;INT(objects[17],0x98)=2002;INT(objects[17],0x9c)=3;
 for(net=0;net<2;net++)for(int reason=1;reason<=7;reason++)for(int flags=0;flags<4;flags++){
  point_reason=reason;wire_landing_flags=(flags&1?0x40:0)|(flags&2?0x80:0);
  score_box_hook(0,&team);if((boxed&0xffff)!=(0x4300|(reason<<1)|wire_landing_flags)||((unsigned)boxed&0xff000000u)!=0x24000000u)return -1;
  received_reason=received_marker=0;client_end_hook(objects[17],boxed,(V3){1,0,2},0);
  if(received_team!=0||received_reason!=reason||rooted(celebration_target_v24)!=objects[27])return -2;
  int marker=(flags&1)&&(reason==3||reason==4||reason==6)?(flags&2?2:1):0;if(received_marker!=marker)return -3;checks++;
 }
 // Legacy online peers don't have authoritative rules touch attribution and
 // must not perform their own RNG or guess a last hitter from stale fields.
 net=1;int before=random_calls;client_end_hook(objects[17],0x4306,(V3){0,0,0},0);
 if(rooted(celebration_target_v24)!=objects[16]||random_calls!=before)return -4;checks++;
 // A bad rank falls back safely without changing valid low bits.
 client_end_hook(objects[17],0x24074306,(V3){0,0,0},0);if(rooted(celebration_target_v24)!=objects[16]||received_team!=0)return -5;checks++;
 // Magic without the recognized low header must never enable a celebration.
 client_end_hook(objects[17],0x24020000,(V3){0,0,0},0);if(celebration_team_v21!=-1||rooted(celebration_target_v24))return -6;checks++;
 client_end_hook(objects[17],0x24024301,(V3){0,0,0},0);if(received_team!=1||rooted(celebration_target_v24))return -7;checks++;
 celebration_reset_v21();return checks;
}
EXPORT int test_ace_v24(){
 init();int checks=0;INT(objects[23],0x18)=2;PTR(objects[24],0x20)=objects[16];PTR(objects[24],0x28)=objects[27];
 INT(objects[16],0x28)=INT(objects[27],0x28)=0;INT(objects[16],0x100)=1001;INT(objects[27],0x100)=2002;
 BYTE(objects[17],0x78)=0;BYTE(objects[17],0x79)=BYTE(objects[17],0x94)=1;INT(objects[17],0x7c)=0;INT(objects[17],0x98)=-1;INT(objects[17],0x9c)=0;
 int before=random_calls;celebration_serve_touch_v24(objects[17],2002,0);
 int wire=celebration_wire_v24(objects[17],0);if(wire!=0x24020000||random_calls!=before)return -1;checks++;
 if(INT(objects[17],0x98)!=-1||INT(objects[17],0x9c)!=0||BYTE(objects[17],0x78))return -2;checks++;
 // Starting the new rally clears an earlier ace before any new serve/fault.
 celebration_serve_clear_v24();random_pick=0;wire=celebration_wire_v24(objects[17],0);if(wire!=0x24010000||random_calls!=before+1)return -3;checks++;
 // Only the authoritative current human server and controlled pending serve
 // can fill this display cache. A bot id, wrong team, or playing rally cannot.
 celebration_serve_touch_v24(objects[17],-13,0);celebration_serve_touch_v24(objects[17],2002,1);
 if(rooted(celebration_serve_rules_v24))return -4;checks++;
 BYTE(objects[17],0x78)=1;celebration_serve_touch_v24(objects[17],2002,0);if(rooted(celebration_serve_rules_v24))return -5;checks++;
 BYTE(objects[17],0x78)=0;BYTE(objects[17],0x94)=0;celebration_serve_touch_v24(objects[17],2002,0);if(rooted(celebration_serve_rules_v24))return -6;checks++;
 BYTE(objects[17],0x94)=1;celebration_serve_touch_v24(objects[17],2002,0);INT(objects[17],0x7c)=1;
 wire=celebration_wire_v24(objects[17],0);if(wire!=0x24010000)return -7;checks++;
 // A later accepted touch always supersedes the special count-zero ace path.
 INT(objects[17],0x7c)=0;INT(objects[17],0x98)=1001;INT(objects[17],0x9c)=1;wire=celebration_wire_v24(objects[17],0);if(wire!=0x24010000)return -8;checks++;
 celebration_reset_v21();if(rooted(celebration_serve_rules_v24))return -9;checks++;
 return checks;
}
'''

def prepare():
    h=HARNESS.replace('objects[32][512]','objects[64][512]').replace('ts[32]','ts[64]')
    h=h.replace('i<32','i<64').replace('tn=32','tn=64')
    h=h.replace('#define EXPORT', '#define FLT(o,n) (*(float*)((char*)(o)+(n)))\nstatic void fake_solver(void* ik);\n#define EXPORT',1)
    h=h.replace('solver_calls++;}', 'solver_calls++;fake_solver(ik);}')
    h=h.replace('static void* dispatch(U64 r)',EXTRA+'\nstatic void* dispatch(U64 r)')
    h=h.replace('switch(r){','switch(r){case 0x30cb70:return touchid;case 0xa14da0:return choose;case 0xafe880:return lookat;',1)
    h=h.replace('static void* dispatch(U64 r)',WIRE_STUBS+'\nstatic void* dispatch(U64 r)')
    h=h.replace('switch(r){','switch(r){case 0x14ba70:return box;',1)
    body=(R/'comfort_v14.c').read_text();body=body[body.index('EXPORT int setting_ready('):body.index('static void set_begin(')]
    h=h.replace('SETTING_READY',body).replace('#include "../hand_visuals_v21.c"','#include "../../hand_visuals_v21.c"')
    score=(R/'celebration_v15.c').read_text();score=score[score.index('EXPORT void* score_box_hook('):score.index('static void point_message(')]
    end=(R/'online_2v2.c').read_text();end=end[end.index('EXPORT void client_end_hook('):]
    h=h.replace('EXPORT void preview_bot()',score+'\n'+end+'\n'+TESTS+'\n'+WIRE_TESTS+'\nEXPORT void preview_bot()')
    folder=R/'tools/v24-bot-target';folder.mkdir(exist_ok=True);p=folder/'target.c';p.write_text(h);return p

def run():
    source=prepare();dll=source.with_suffix('.dll');cache=str(source.parent/'cache')
    env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=cache,ZIG_LOCAL_CACHE_DIR=cache)
    p=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(dll),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
    assert p.returncode==0,(p.returncode,p.stdout+p.stderr)
    lib=ctypes.CDLL(str(dll));checks=lib.test_target_v24();assert checks==129,checks
    wire_checks=lib.test_wire_v24();assert wire_checks==60,wire_checks
    ace_checks=lib.test_ace_v24();assert ace_checks==9,ace_checks
    result=dict(passed=True,checks=checks,wire_checks=wire_checks,ace_checks=ace_checks,native_fixture=str(dll),production_sha256=hashlib.sha256((R/'hand_visuals_v21.c').read_bytes()).hexdigest(),
      cases=['winner actual human last touch takes precedence over distance/receiver','opponent final touch and bot point choose human randomly once','stable full-width Photon touchId ordering across reversed peer rosters','head aims at recipient after arm IK and hostile native ball-look pass','moving recipient updates head and hand to same human without retargeting','disconnected live objects rejected by roster membership','team-switch fallback stable and same-team only','no-human hides','reset restores all four bones and hand scale','cached frame loop does not call Random/Find/SetActive'],
      scope='Compiled production celebration C; deterministic calibrated LookAt and hierarchical transform stubs, not live headset/multiplayer validation')
    (R/'analysis/v24-bot-target-native-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
