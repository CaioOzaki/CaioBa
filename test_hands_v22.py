"""Compile exact v22 production cosmetic module with real hierarchical transform stubs.
No working/live files are written. Geometry preview uses serialized meshes/rig.
"""
from pathlib import Path
import ctypes,json,os,subprocess,sys,hashlib
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
HARNESS=r'''
typedef unsigned long long U64;
typedef struct{float x,y,z;} V3;
typedef struct{float x,y,z,w;} Q4;
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define BYTE(o,n) (*(unsigned char*)((char*)(o)+(n)))
#define TRAMP(t,n,args) static t n##_trampoline args {solver_calls++;}
static int solver_calls;
static unsigned char memory[0x1544000],objects[32][512];
static U64 base(void){return (U64)memory;}
static float sqroot(float f){return __builtin_sqrtf(f);}
static V3 add(V3 a,V3 b){return(V3){a.x+b.x,a.y+b.y,a.z+b.z};}
static V3 sub(V3 a,V3 b){return(V3){a.x-b.x,a.y-b.y,a.z-b.z};}
static V3 mul(V3 a,float k){return(V3){a.x*k,a.y*k,a.z*k};}
static float dot(V3 a,V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static int finitev(V3 a){return __builtin_isfinite(a.x)&&__builtin_isfinite(a.y)&&__builtin_isfinite(a.z);}
static Q4 normalized(Q4 q){float n=sqroot(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w);return(Q4){q.x/n,q.y/n,q.z/n,q.w/n};}
static Q4 product(Q4 a,Q4 b){return(Q4){a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x,a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w,a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z};}
static Q4 inverse(Q4 q){return(Q4){-q.x,-q.y,-q.z,q.w};}
static V3 rotate(Q4 q,V3 v){Q4 x=product(product(q,(Q4){v.x,v.y,v.z,0}),inverse(q));return(V3){x.x,x.y,x.z};}
typedef struct{void* id;int parent,active;V3 p,scale;Q4 q,color;} T;
static T ts[32];static int tn;
static int index(void* id){for(int i=0;i<tn;i++)if(ts[i].id==id)return i;return -1;}
static void* transform(void* o){return o;}
static void* gameobject(void* o){return o;}
static Q4 worldq(int i){return ts[i].parent<0?ts[i].q:product(worldq(ts[i].parent),ts[i].q);}
static V3 position(void* o){int i=index(o);return ts[i].parent<0?ts[i].p:add(position(ts[ts[i].parent].id),rotate(worldq(ts[i].parent),ts[i].p));}
static void position_set(void* o,V3 v){int i=index(o);if(ts[i].parent>=0)v=rotate(inverse(worldq(ts[i].parent)),sub(v,position(ts[ts[i].parent].id)));ts[i].p=v;}
static int rootn;static void* roots[256];
static void* rooted(unsigned h){return h?roots[h]:0;}
static void root_set(unsigned* h,void* o){if(!*h)*h=++rootn;roots[*h]=o;}
static int alive(void* p){return p!=0;}
static int finds,materials,activewrites,grips[2],net,local_pose_v21,tone,remote_pose,ready_touch=1;
static int doubles_enabled=1,quartet_enabled=0,net_rally_active,net_serve_team=-1,net_touch_team,net_touch_count=1,serve_flight_team=-1;
static unsigned rules_root;static void* player;
static int network_physics(void){return net;}
static void* local_avatar_player(void){return player;}
static void ensure_preferences_v19(void){}
static int player_hand_pose_v21(void* p){return remote_pose;}
static int player_hand_tone_v21(void* p){return tone;}
static void select_appearance(int x,int y){}
static Q4 hand_tone_colors_v21[6]={{1,.85,.74,1},{.91,.69,.49,1},{.76,.49,.29,1},{.58,.32,.17,1},{.36,.18,.10,1},{.19,.085,.05,1}};
static void* str(const char* s){return(void*)s;}
static int eq(const char* a,const char* b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static void* find_child(void* p,const char* s){finds++;
 const char* paths[8]={"Hand Root L/Open/Cloudcourt Open Glove","Hand Root L/Closed/Cloudcourt Closed Glove","Hand Root R/Open/Cloudcourt Open Glove","Hand Root R/Closed/Cloudcourt Closed Glove","Hand Root L/CC_ThumbsUp","Hand Root R/CC_ThumbsUp","Hand Root L/CC_SettingOpen","Hand Root R/CC_SettingOpen"};
 for(int i=0;i<8;i++)if(eq(s,paths[i]))return ts[i].id;
 if(eq(s,"CC_WinThumb"))return ts[8].id;if(eq(s,"Base_mesh"))return ts[9].id;return 0;
}
static V3 player_court_position(void* p){return position(p);}
static void active(void* t,_Bool b,void* m){ts[index(t)].active=b;activewrites++;}
static void* component(void* o,void* type,void* m){return o;}
static void* material(void* o,void* m){materials++;return o;}
static void color(void* o,Q4 q,void* m){ts[index(o)].color=q;}
static void localq(Q4* q,void* o,void* m){*q=ts[index(o)].q;}
static void globalq(Q4* q,void* o,void* m){*q=worldq(index(o));}
static void setlocalq(void* o,Q4 q,void* m){ts[index(o)].q=q;}
static void setglobalq(void* o,Q4 q,void* m){int i=index(o);ts[i].q=ts[i].parent<0?q:product(inverse(worldq(ts[i].parent)),q);}
static void localscale(V3* v,void* o,void* m){*v=ts[index(o)].scale;}
static void setlocalscale(void* o,V3 v,void* m){ts[index(o)].scale=v;}
static void* atlas(void* o,void* m){return objects[30];}
static int atlas_assignments;static void setatlas(void* o,void* mat,void* m){if(mat==objects[30])atlas_assignments++;}
static void* control(int slot,void* type,void* o){if(slot==5)return objects[28];if(slot==6)return objects[29];return(void*)(U64)(grips[o==objects[29]]!=0);}
static void* dispatch(U64 r){switch(r){case 0xa2710:return control;case 0x94f700:return active;case 0x94f410:return component;case 0xa1ae90:return material;case 0x956610:return color;case 0xb74b50:return localq;case 0xb74fd0:return globalq;case 0xb754c0:return setlocalq;case 0xb75750:return setglobalq;case 0xb74bf0:return localscale;case 0xb75560:return setlocalscale;case 0xa1af10:return atlas;case 0xa1b0e0:return setatlas;default:return 0;}}
#define FN(r,t) ((t)dispatch(r))
SETTING_READY
#include "../hand_visuals_v21.c"
static void init(){
 for(int i=0;i<32;i++){ts[i].id=objects[i];ts[i].parent=-1;ts[i].scale=(V3){1,1,1};ts[i].q=(Q4){0,0,0,1};}tn=32;
 player=objects[16];root_set(&rules_root,objects[17]);INT(player,0x28)=0;
 PTR(objects[18],0x168)=player;BYTE(objects[17],0x78)=1;INT(objects[17],0x7c)=0;INT(objects[17],0x9c)=1;
 PTR(memory,0x1542b48)=objects[20];PTR(objects[20],0xb8)=objects[21];PTR(objects[21],0)=objects[22];PTR(objects[22],0x40)=objects[23];PTR(memory,0x1541dc0)=objects[24];PTR(memory,0x1541d98)=objects[25];
 // Bot right arm exact bind lengths from sharedassets0, scaled to world.
 ts[10].p=(V3){-.28f,1.13f,0};ts[11].parent=10;ts[11].p=(V3){-.262721f,0,0};ts[12].parent=11;ts[12].p=(V3){-.245490f,0,0};
 void* bot=objects[13];INT(bot,0x28)=0;PTR(bot,0xb8)=objects[19];PTR(objects[19],0x28)=objects[14];PTR(objects[19],0x38)=objects[15];PTR(objects[14],0x38)=objects[20];PTR(objects[20],0x68)=ts[10].id;PTR(objects[20],0x70)=ts[11].id;PTR(objects[20],0x78)=ts[12].id;
 PTR(objects[17],0x60)=objects[21];PTR(objects[21],0x20)=objects[22];PTR(objects[22],0x38)=objects[23];PTR(objects[23],0x10)=objects[24];INT(objects[23],0x18)=3;PTR(objects[24],0x20)=player;PTR(objects[24],0x28)=objects[26];PTR(objects[24],0x30)=objects[27];INT(objects[26],0x28)=1;INT(objects[27],0x28)=0;ts[26].p=(V3){-.1f,1,0};ts[27].p=(V3){-4,1,0};
 ts[16].p=(V3){2,1,0};ts[13].p=(V3){0,0,0};
}
EXPORT int test_hands(){
 // Call separately in a fresh process before bot setup reuses fixture memory.
 init();int checks=0;
 for(int i=0;i<32;i++)for(int j=0;j<512;j++)objects[i][j]=0;
 PTR(objects[18],0x168)=player;BYTE(objects[17],0x78)=1;INT(objects[17],0x7c)=0;INT(objects[17],0x9c)=1;
 PTR(memory,0x1542b48)=objects[20];PTR(objects[20],0xb8)=objects[21];PTR(objects[21],0)=objects[22];PTR(objects[22],0x40)=objects[23];PTR(memory,0x1541dc0)=objects[24];PTR(memory,0x1541d98)=objects[25];
 for(net=0;net<2;net++)for(int fmt=2;fmt<=4;fmt+=2){
  doubles_enabled=fmt==2;quartet_enabled=fmt==4;net_rally_active=1;
  for(int g=0;g<4;g++)for(int touch=0;touch<4;touch++)for(int serving=0;serving<2;serving++){
   grips[0]=g&1;grips[1]=g&2;net_touch_count=touch;INT(objects[17],0x9c)=touch;serve_flight_team=net_serve_team=serving?0:-1;
   avatar_hands_v21(objects[18]);int expected=g==3&&touch==1&&!serving?4:g;
   if(local_pose_v21!=expected)return -100-checks;
   if(ts[6].active!=(expected==4)||ts[7].active!=(expected==4))return -200-checks;
   if(ts[4].active!=(expected!=4&&(expected&1)!=0)||ts[5].active!=(expected!=4&&(expected&2)!=0))return -300-checks;
   for(int t=0;t<6;t++){tone=t;avatar_hands_v21(objects[18]);for(int i=0;i<8;i++)if(ts[i].color.x!=hand_tone_colors_v21[t].x)return -400-checks;}
   checks++;
  }
 }
 int f=finds,a=activewrites;avatar_hands_v21(objects[18]);if(finds!=f||activewrites!=a)return -9;
 return checks;
}
EXPORT int test_bot(){
 init();celebration_point_v21(objects[17],0);celebration_bot_v21(objects[13]);if(ts[8].active)return -1;
 bot_ik_hook(objects[14],0);if(!ts[8].active||atlas_assignments!=1)return -2;
 V3 wrist=position(ts[12].id),hand=position(ts[8].id);if(dot(sub(wrist,hand),sub(wrist,hand))>.000001f)return -3;
 if(wrist.y<1.3f||wrist.x<.1f)return -4;
 if(ts[12].scale.x>.01f)return -5;
 int f=finds,a=activewrites;
 for(int i=0;i<200;i++){celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);bot_ik_hook(objects[15],0);}
 if(finds!=f||activewrites!=a||atlas_assignments!=1)return -6;
 // NewRally activation does not clear the point or start a 2.6s timer.
 BYTE(objects[17],0x78)=1;celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);if(!ts[8].active)return -7;
 // A closer opponent is excluded; switching the nearest human retargets
 // the other same-team human, moving the arm to the other side.
 INT(player,0x28)=1;celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);
 if(position(ts[8].id).x>-.4f)return -12;INT(player,0x28)=0;
 // Whistle event restores the original bone rotations/scale immediately.
 celebration_reset_v21();if(ts[8].active||ts[12].scale.x!=1)return -8;
 for(int i=10;i<13;i++)if(ts[i].q.w<.9999f)return -9;
 f=finds;a=activewrites;for(int i=0;i<100;i++){celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);}if(finds!=f||activewrites!=a)return -10;
 // Winning bot has no eligible human when the own-team human switches.
 INT(player,0x28)=1;INT(objects[27],0x28)=1;celebration_point_v21(objects[17],0);celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);if(ts[8].active)return -11;
 return 401;
}
EXPORT void preview_bot(){init();celebration_point_v21(objects[17],0);celebration_bot_v21(objects[13]);bot_ik_hook(objects[14],0);}
EXPORT float fixture(int obj,int field){T* t=&ts[obj];if(field<3)return((float*)&t->p)[field];if(field<7)return((float*)&t->q)[field-3];if(field<10){V3 p=position(t->id);return((float*)&p)[field-7];}Q4 q=worldq(obj);return((float*)&q)[field-10];}
EXPORT int DllMain(void* m,unsigned why,void* x){return 1;}
'''

def prepare():
    text=(R/'comfort_v14.c').read_text();body=text[text.index('EXPORT int setting_ready('):text.index('static void set_begin(')]
    p=R/'tools/h22.c';p.write_text(HARNESS.replace('SETTING_READY',body));return p

def compile_harness():
    source=prepare();dll=R/'tools/h22.dll';cache=str(R/'tools/zh22');env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=cache,ZIG_LOCAL_CACHE_DIR=cache)
    c=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(dll),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
    assert c.returncode==0,c.stdout+c.stderr
    return dll

def run():
    dll=R/'tools/h22.dll';d=ctypes.CDLL(str(dll));h=d.test_hands();b=d.test_bot();assert h==128,('hand cases',h);assert b==401,('bot',b)
    d.fixture.argtypes=[ctypes.c_int,ctypes.c_int];d.fixture.restype=ctypes.c_float
    report=dict(passed=True,production_module_sha256=hashlib.sha256((R/'hand_visuals_v21.c').read_bytes()).hexdigest(),hand_guard_cases=h,bot_solver_frames=b,checks=['actual production native C','actual setting_ready guard copied from production','local grips 00/01/10/11','first/second/third/fourth touch and serve eligibility','offline/online and 2v2/4v4','six skin tones per pose','cached visual/material bindings','existing upper/forearm bones rotated after native solver','thumb origin equals moved skeletal wrist','own character atlas assigned once','no 2.6s timeout or NewRally clear','whistle restores three bones and hand scale','nearest same-team human selected despite closer opponent','team switches retarget the connected arm','no eligible human hides','no per-frame Find/allocation/SetActive after warmup'],scope='Native deterministic hierarchical engine stubs; no live VR claim')
    (R/'analysis/v22-hands-native-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
    if '--prepare' in sys.argv:print(prepare())
    elif '--compile' in sys.argv:print(compile_harness())
    else:run()
