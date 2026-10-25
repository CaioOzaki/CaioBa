/* Shared practice balls in the online room, before match creation only.
 * Photon assigns each spawned object to the client who pulled the trigger.
 * Four live balls per client are recycled, avoiding unbounded VR physics load.
 */
TRAMP(void,lobby_enter,(void* page,void* arg,void* m))
TRAMP(void,lobby_start,(void* page,void* m))
TRAMP(void,lobby_ball_awake,(void* ball,void* m))
static unsigned lobby_page,lobby_balls[32];
static float lobby_spin_time[32];
static int lobby_transitioning,lobby_cursor;
static float lobby_spawn_at;
static int lobby_active(void){
 if(!network_physics()||lobby_transitioning)return 0;
 void* page=rooted(lobby_page);
 return page&&alive(page)&&FN(0x9478e0,_Bool(*)(void*,void*))(page,0)&&FN(0x61efc0,_Bool(*)(void*))(0);
}
static int lobby_is_ball(void* ball){
 if(!ball)return 0;
 for(int i=0;i<32;i++)if(rooted(lobby_balls[i])==ball)return 1;
 return 0;
}
static float lobby_step_time(void* ball,float dt){
 for(int i=0;i<32;i++)if(rooted(lobby_balls[i])==ball){
  lobby_spin_time[i]+=dt;if(lobby_spin_time[i]+.000001f<physics_interval)return 0;
  float step=lobby_spin_time[i];lobby_spin_time[i]=0;return step;
 }
 return 0;
}
static int lobby_owned(void* ball){void* view=ball?PTR(ball,0xc8):0;return view&&FN(0xe6e000,_Bool(*)(void*,void*))(view,0);}
static void lobby_adopt_ball(void* ball){
 if(!ball)return;
 void* klass=*(void**)(base()+0x15426f0);void* statics=klass?PTR(klass,0xb8):0;
 if(statics&&PTR(statics,0)==ball)PTR(statics,0)=0;
 if(lobby_is_ball(ball))return;
 BYTE(ball,0x88)=1;BYTE(ball,0x89)=1;INT(ball,0xc0)=3;
 for(int i=0;i<32;i++)if(!alive(rooted(lobby_balls[i]))){root_set(&lobby_balls[i],ball);lobby_spin_time[i]=0;return;}
 BYTE(ball,0x88)=0;BYTE(ball,0x89)=0;
}
static void lobby_remove_ball(unsigned* root){
 for(int i=0;i<32;i++)if(root==&lobby_balls[i])lobby_spin_time[i]=0;
 void* ball=rooted(*root);
 if(alive(ball)){
  void* hand=PTR(ball,0xd8);if(alive(hand)&&PTR(hand,0x30)==ball)managed_field(hand,0x30,0);
  BYTE(ball,0x88)=0;BYTE(ball,0x89)=0;BYTE(ball,0xd0)=0;managed_field(ball,0xd8,0);
  void* go=gameobject(ball);FN(0x94f700,void(*)(void*,_Bool,void*))(go,0,0);
  if(lobby_owned(ball)&&FN(0x61efc0,_Bool(*)(void*))(0))FN(0x60cb40,void(*)(void*,void*))(go,0);
 }
 root_set(root,0);
}
static void lobby_cleanup(void){for(int i=0;i<32;i++)lobby_remove_ball(&lobby_balls[i]);lobby_cursor=0;}
EXPORT void lobby_enter_hook(void* page,void* arg,void* m){
 lobby_transitioning=1;lobby_cleanup();root_set(&lobby_page,page);lobby_spawn_at=0;
 lobby_enter_trampoline(page,arg,m);lobby_transitioning=0;
}
EXPORT void lobby_start_hook(void* page,void* m){
 lobby_transitioning=1;lobby_cleanup();lobby_start_trampoline(page,m);
}
EXPORT void lobby_ball_awake_hook(void* ball,void* m){
 int practice=lobby_active();void* klass=*(void**)(base()+0x15426f0);void* statics=klass?PTR(klass,0xb8):0;
 void* previous=statics?PTR(statics,0):0;
 lobby_ball_awake_trampoline(ball,m);
 if(!practice)return;
 /* Practice must never replace the singleton used by match rules/cameras. */
 if(statics)PTR(statics,0)=previous;
 lobby_adopt_ball(ball);
}
static void* lobby_hand_ball(void* hand){
 if(!hand||PTR(hand,0x30))return 0;
 void* center=PTR(hand,0x18);if(!center)return 0;V3 p=position(center);if(!finitev(p))return 0;
 float now=FN(0xb72b40,float(*)(void*))(0);if(now<lobby_spawn_at)return 0;
 int count=0,oldest=-1;
 for(int j=0;j<32;j++){
  int i=(lobby_cursor+j)%32;void* ball=rooted(lobby_balls[i]);
  if(alive(ball)&&lobby_owned(ball)){count++;if(!BYTE(ball,0xd0)&&oldest<0)oldest=i;}
 }
 if(count>=4){if(oldest<0)return 0;lobby_remove_ball(&lobby_balls[oldest]);lobby_cursor=(oldest+1)%32;}
 Q4 q={0,0,0,1};void* go=FN(0x60fb50,void*(*)(void*,V3,Q4,unsigned char,void*,void*))(str("Volleyball"),p,q,0,0,0);
 if(!go)return 0;
 void* ball=FN(0x94f410,void*(*)(void*,void*,void*))(go,str("Volleyball"),0);
 if(!ball||!lobby_is_ball(ball))return 0;
 lobby_spawn_at=now+.25f;
 /* Original Hand.Update owns attachment, release and throwing velocity. */
 position_set(transform(ball),p);return ball;
}
EXPORT _Bool lobby_move_enabled_hook(void* m){return lobby_active()?1:FN(0xef3370,_Bool(*)(void*))(m);}
EXPORT float lobby_move_clamp_hook(float value,float low,float high,void* m){
 return lobby_active()?value:FN(0x956d70,float(*)(float,float,float,void*))(value,low,high,m);
}
EXPORT void lobby_move_position_hook(void* t,V3 p,void* m){
 if(lobby_active()){
  if(p.x< -10)p.x=-10;if(p.x>10)p.x=10;if(p.z< -15)p.z=-15;if(p.z>15)p.z=15;
 }
 FN(0xb756b0,SetVec)(t,p,m);
}
