"""Production v26 C and original Hand.Update; deterministic engine stubs."""
from pathlib import Path
import sys,os,json,subprocess,struct
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import pefile
import test_lobby_v21 as old
from unicorn.x86_const import *
def take(file,start,end):
 s=(R/file).read_text();return s[s.index(start):s.index(end,s.index(start))]
placement=take('formation_serve.c','static int hand_ball_place_v26','static void hand_serve_reset')
visible=take('formation_serve.c','static void serve_visible','/* Both serve')
clamp=take('identity_v16.c','static V3 clamp_player_position_v26','\ntypedef struct {unsigned player;int skin;}')
reset=take('online_2v2.c','static void online_session_reset_v26','static int network_physics')
handreset=take('formation_serve.c','static void hand_serve_reset(void){','/* Replace just')
roster=take('bots_v20.c','static unsigned bot_roster_rules_v20;','EXPORT void bots_spawn_begin_v20')
pending=take('identity_v16.c','typedef struct {unsigned player;int team;} PendingTeam;','static void finish_team_changes')
HARNESS=old.HARNESS.replace('#include "../lobby_v18.c"',r'''
static int spawn_trigger_v24(void* h){return FN(0x3130b0,_Bool(*)(void*,void*))(h,0);}
static int offline(void){return 0;}
static unsigned waiting_ball_root,attack_receiver[2],wing_turn[2],rules_root,local_player_root,jumping_player_root;
static int doubles_enabled,quartet_enabled,doubles_spawned,doubles_team_counts[2];
static int net_first_touch,net_serve_team,net_touch_team,net_touch_count,net_rally_active,net_last_id_v28,accepted_position_valid_v28,accepted_block_v28;
static int reception_pending,reception_context,serve_flight_team,serve_fault,deferred_serve_point,player_airborne;
static int pending_valid;static void* pending_ball;static void* spinning_ball;static float pending_time;
typedef struct {unsigned controller;unsigned char held;} Trigger;
static Trigger spawn_triggers_v25[2];
static void customization_reset_v28(void){} /* Cosmetics tested independently. */
static void ball_style_reset_v26(void){} /* Ball material lifecycle has its own integrated tests. */
static void lobby_session_reset_v26(void);
static void online_session_reset_v26(void);
static int lobby_active(void);
TRAMP(void,clamp_player,(void* p,void* m))
''' + visible+placement+handreset+roster+clamp+pending+reset+r'''
#include "../lobby_v18.c"
EXPORT void session_reset(void){online_session_reset_v26();}
EXPORT void dirty(void* rules,void* ball,void* hand){
 root_set(&waiting_ball_root,ball);root_set(&bot_roster_rules_v20,rules);bot_roster_mask_v20=255;bot_spawn_context_v20=1;
 for(int i=0;i<2;i++){root_set(&attack_receiver[i],player);wing_turn[i]=1;}root_set(&rules_root,rules);root_set(&local_player_root,player);root_set(&jumping_player_root,player);
 root_set(&pending_teams[0].player,player);pending_teams[0].team=1;
 for(int i=0;i<2;i++){root_set(&spawn_triggers_v25[i].controller,hand);spawn_triggers_v25[i].held=1;}
 doubles_enabled=quartet_enabled=doubles_spawned=doubles_team_counts[0]=doubles_team_counts[1]=1;
 net_first_touch=net_touch_count=net_rally_active=reception_pending=reception_context=serve_fault=player_airborne=pending_valid=1;
 net_last_id_v28=42;accepted_position_valid_v28=accepted_block_v28=1;
 net_serve_team=net_touch_team=serve_flight_team=deferred_serve_point=0;pending_ball=spinning_ball=ball;pending_time=1;
}
EXPORT int clean(void){
 return !waiting_ball_root&&!attack_receiver[0]&&!attack_receiver[1]&&!wing_turn[0]&&!wing_turn[1]&&!bot_roster_rules_v20&&!bot_roster_mask_v20&&!bot_spawn_context_v20&&!rules_root&&!local_player_root&&!jumping_player_root&&!pending_teams[0].player&&pending_teams[0].team==-1&&
 !spawn_triggers_v25[0].controller&&!spawn_triggers_v25[1].controller&&!spawn_triggers_v25[0].held&&!spawn_triggers_v25[1].held&&
 !doubles_enabled&&!quartet_enabled&&!doubles_spawned&&!doubles_team_counts[0]&&!doubles_team_counts[1]&&
 !accepted_position_valid_v28&&!accepted_block_v28&&net_last_id_v28==-1&&!net_first_touch&&!net_touch_count&&!net_rally_active&&net_serve_team==-1&&net_touch_team==-1&&serve_flight_team==-1&&deferred_serve_point==-1&&
 !reception_pending&&!reception_context&&!serve_fault&&!player_airborne&&!pending_valid&&!pending_ball&&!spinning_ball&&!pending_time;
}
EXPORT void roomscale(void* body){clamp_local_player_v26(body);}
EXPORT void format(int f){doubles_enabled=f==2;quartet_enabled=f==4;}
EXPORT void move(void* t,V3 p,void* m){lobby_move_position_hook(t,p,m);}
''')
def compile_harness():
 c=R/'tools/o26.c';dll=c.with_suffix('.dll');c.write_text(HARNESS)
 env=dict(os.environ,ZIG_LOCAL_CACHE_DIR=str(R/'tools/zo26'),ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zo26'))
 r=subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(c),'-o',str(dll),'-Wl,--entry=DllMain'],env=env,capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr
 return pefile.PE(str(dll))
class Engine(old.Engine):
 def __init__(self,b,q):
  self.freezes=[];self.kinematic={};self.renderer_enabled={};self.net_go=0;self.net_renderer=0;self.finds=0
  super().__init__(b,q)
  self.ek=self.alloc();self.es=self.alloc();self.ptr(b+0x15422a0,self.ek);self.ptr(self.ek+0xb8,self.es)
  self.transforms[self.player]=self.alloc();self.pos[self.transforms[self.player]]=(0,0,-4)
  self.torso=self.alloc();self.ptr(self.body+0x38,self.torso);self.pos[self.torso]=(0,1.3,-4)
  self.ptr(self.player+0x20,self.alloc())
 def hook(self,u,at,size,user):
  r=at-self.b;a,b,c=[u.reg_read(x) for x in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8)]
  if r==0x77ea70:
   self.freezes.append(a);self.kinematic[self.q(a+0x98)]=True;self.ret()
  elif r==0x77fe10:self.ret(f=.105)
  elif r==0xa1b2f0:self.renderer_enabled[a]=bool(b);self.ret()
  elif r==0x94f3d0:self.finds+=1;self.ret(self.net_go)
  elif r==0x94f410 and a==self.net_go and a:self.ret(self.net_renderer)
  elif at==self.ex.get('clamp_player_trampoline'):self.ret()
  elif at==old.STOP-0x100:
   self.kinematic[self.q(a+0x98)]=False;super().hook(u,at,size,user)
  else:super().hook(u,at,size,user)
 def scene(self,ready=True):
  self.environment=self.alloc();self.ptr(self.es,self.environment)
  self.net_go=self.alloc() if ready else 0;self.net_renderer=self.alloc() if ready else 0
 def leave_menu(self):self.active=False;self.call('session_reset')
def run():
 q=compile_harness();cases=[]
 for base in (0x180000000,0x190000000):
  for fmt in (2,4):
   for host in (False,True):
    e=Engine(base,q);left=e.hand(0);right=e.hand(1);remote=e.hand(0,False)
    old_balls=[];old_nets=[]
    for session in (1,2):
     e.active=True;e.call('lobby_enter_hook',e.page);e.scene(False)
     e.call('lobby_update_hook',e.page);before=e.finds
     e.net_go=e.alloc();e.net_renderer=e.alloc();e.time+=.3;e.call('lobby_update_hook',e.page)
     assert e.renderer_enabled[e.net_renderer];net=e.net_renderer;old_nets.append(net)
     for _ in range(20):e.call('lobby_update_hook',e.page)
     assert e.finds==before+1,'ready environment must not search each frame'
     # Same live page, asynchronous scene replacement while old net remains alive.
     previous_net=net;e.scene();e.time+=.3;e.call('lobby_update_hook',e.page)
     net=e.net_renderer;old_nets.append(net)
     assert not e.renderer_enabled[previous_net] and e.renderer_enabled[net]
     stable=e.finds
     for _ in range(10):e.call('lobby_update_hook',e.page)
     assert e.finds==stable
     e.update(remote,True);count=len(e.spawned);e.update(left,False);e.update(left,True)
     ball=e.q(left+0x30);old_balls.append(ball);assert ball and len(e.spawned)==count+1
     assert e.kinematic[e.q(ball+0x98)] and e.q(ball+0xd8)==left
     assert abs(e.pos[e.transforms[ball]][1]-1.53)<1e-5
     e.update(right,True);assert e.q(right+0x30)==ball and not e.q(left+0x30)
     frozen=len(e.freezes)
     for _ in range(12):e.update(left,True);e.update(right,True)
     assert len(e.freezes)==frozen and e.q(right+0x30)==ball
     e.update(right,False);assert not e.kinematic[e.q(ball+0x98)] and not e.q(right+0x30)
     e.call('lobby_start_hook',e.page);assert not e.renderer_enabled[net]
     e.active=False;e.call('format',fmt if host else 0)
     for team in (0,1):
      e.u.mem_write(e.player+0x28,struct.pack('<i',team));t=e.transforms[e.player]
      for desired_z,offset in [(1.,.3),(-1.,-.3),(0.,.45),(0.,-.45)]:
       e.pos[t]=(0,0,0);e.pos[e.torso]=(0,1.3,offset);v=e.alloc();e.vec(v,(0,0,desired_z));e.call('move',t,v)
       actual=e.pos[t][2]+offset
       assert actual<=-.18+1e-6 if team==0 else actual>=.18-1e-6
     # Solver-follow torso crossing is clamped even without locomotion input.
     for team in (0,1):
      e.u.mem_write(e.player+0x28,struct.pack('<i',team));t=e.transforms[e.player]
      e.pos[t]=(0,0,0);offset=.3 if team==0 else -.3;e.pos[e.torso]=(0,1.3,offset)
      e.call('roomscale',e.body);actual=e.pos[t][2]+offset
      assert actual<=-.18+1e-6 if team==0 else actual>=.18-1e-6
      saved=e.pos[t];e.call('roomscale',e.alloc());assert e.pos[t]==saved
     e.call('dirty',e.alloc(),ball,left);e.leave_menu();assert e.call('clean')==1
     assert not e.call('lobby_move_enabled_hook')
     # A persistent player/old nonnull area must not move the menu outside
     # Photon room membership, even while network namespace stays ready.
     e.room=False;e.call('format',0);t=e.transforms[e.player]
     e.pos[t]=(0,0,0);e.pos[e.torso]=(0,1.3,-.3)
     e.call('roomscale',e.body);assert e.pos[t]==(0,0,0)
     v=e.alloc();e.vec(v,(0,0,-1));e.call('move',t,v);assert e.pos[t]==(0.,0.,-1.)
     e.room=True
    assert old_balls[0]!=old_balls[1] and all(b in e.destroyed for b in old_balls)
    assert old_nets[0]!=old_nets[1] and all(not e.renderer_enabled[n] for n in old_nets)
    cases.append(dict(base=hex(base),format=fmt,host=host,sessions=2))
 report=dict(passed=True,cases=cases,actual_production_c=True,checks=['native Hand.Update attachment/release','frozen spawn and recall via original serve RPC','palm radius separation','no repeated freeze on held trigger','remote hand rejected','scene identity plus late renderer readiness','no warm frame Find','lobby cleanup hides existing net','actual movement setter symmetric for cold client and host','room-scale torso boundary without stick and remote body rejection','persistent player with stale nonnull area outside room does not clamp menu motion','actual session reset clears stale rules/waiting/roster/teams/controller/spin/rally state','second session same persistent page/hands uses fresh ball/net'],scope='Native isolated module and original game Hand.Update with deterministic engine/network stubs; no live Unity physics, Quest or two-PC claim.')
 (R/'analysis/v26-online-state-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':run()
