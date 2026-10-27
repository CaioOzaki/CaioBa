/* Shared practice balls in the online room, before match creation only.
 * Photon assigns each spawned object to the client who pulled the trigger.
 * One ball per client is recalled by either local trigger, including transfer
 * from an already holding hand. Remote balls remain independently simulated.
 */
TRAMP(void,lobby_enter,(void* page,void* arg,void* m))
TRAMP(void,lobby_start,(void* page,void* m))
TRAMP(void,lobby_ball_awake,(void* ball,void* m))
TRAMP(void,lobby_hand_update,(void* hand,void* m))
TRAMP(void,lobby_update,(void* page,void* m))
static unsigned lobby_page,lobby_balls[32];
static unsigned lobby_local_ball,lobby_hands[2];
static unsigned lobby_pending_hand,lobby_pending_ball;
static unsigned char lobby_trigger_down[2];
static float lobby_spin_time[32];
static int lobby_transitioning,lobby_menu_down;
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
static void lobby_cleanup(void){
 for(int i=0;i<32;i++)lobby_remove_ball(&lobby_balls[i]);root_set(&lobby_local_ball,0);
 root_set(&lobby_pending_hand,0);root_set(&lobby_pending_ball,0);
 for(int i=0;i<2;i++){root_set(&lobby_hands[i],0);lobby_trigger_down[i]=0;}lobby_menu_down=0;
}
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
static void lobby_detach(void* ball){
 void* previous=PTR(ball,0xd8);
 if(alive(previous)&&PTR(previous,0x30)==ball)managed_field(previous,0x30,0);
 /* Do not call EndInteraction: that would throw and broadcast a hit. */
 FN(0xb755b0,void(*)(void*,void*,void*))(transform(ball),0,0);
 BYTE(ball,0xd0)=0;managed_field(ball,0xd8,0);
 V3 zero={0,0,0};void* rb=PTR(ball,0x98);void* local=PTR(ball,0x30);
 if(rb){FN(0xec60d0,SetVec)(rb,zero,0);FN(0xec5cd0,SetVec)(rb,zero,0);}
 if(local&&local!=rb){FN(0xec60d0,SetVec)(local,zero,0);FN(0xec5cd0,SetVec)(local,zero,0);}
 for(int i=0;i<32;i++)if(rooted(lobby_balls[i])==ball)lobby_spin_time[i]=0;
}
static void* lobby_recall_ball(void* hand){
 if(!hand)return 0;
 void* center=PTR(hand,0x18);if(!center)return 0;V3 p=position(center);if(!finitev(p))return 0;
 void* ball=rooted(lobby_local_ball);
 if(!alive(ball)||!lobby_owned(ball)){
  root_set(&lobby_local_ball,0);ball=0;
  /* Recover a locally owned cached ball after reactivation, never a peer's. */
  for(int i=0;i<32;i++){void* candidate=rooted(lobby_balls[i]);if(alive(candidate)&&lobby_owned(candidate)){ball=candidate;break;}}
  if(!ball){
   float now=FN(0xb72b40,float(*)(void*))(0);if(now<lobby_spawn_at)return 0;
   Q4 q={0,0,0,1};void* go=FN(0x60fb50,void*(*)(void*,V3,Q4,unsigned char,void*,void*))(str("Volleyball"),p,q,0,0,0);
   if(!go)return 0;
   ball=FN(0x94f410,void*(*)(void*,void*,void*))(go,str("Volleyball"),0);
   if(!ball||!lobby_is_ball(ball))return 0;
   lobby_spawn_at=now+.25f;
  }
  root_set(&lobby_local_ball,ball);
 }
 lobby_detach(ball);
 /* Original Hand.Update owns attachment, release and throwing velocity. */
 position_set(transform(ball),p);return ball;
}
static void* lobby_hand_ball(void* hand){
 /* Only a fresh press can attach. A trigger still held in the old hand must
  * not pull the transferred ball back on the next native Update. */
 if(rooted(lobby_pending_hand)!=hand)return 0;
 void* ball=rooted(lobby_pending_ball);root_set(&lobby_pending_hand,0);root_set(&lobby_pending_ball,0);
 return ball;
}
static int lobby_local_hand(void* hand){
 void* player=online_local_player();void* body=player?PTR(player,0x80):0;
 void* ht=hand?transform(hand):0;void* bt=body?transform(body):0;
 return ht&&bt&&FN(12008720,_Bool(*)(void*,void*,void*))(ht,bt,0);
}
EXPORT void lobby_hand_update_hook(void* hand,void* m){
 if(lobby_active()&&lobby_local_hand(hand)){
  int i=BYTE(hand,0x24)?1:0;
  if(rooted(lobby_hands[i])!=hand){root_set(&lobby_hands[i],hand);lobby_trigger_down[i]=0;}
  int down=spawn_trigger_v24(hand);
  if(down&&!lobby_trigger_down[i]&&!ui_pointer_over_button_v19()){
   void* held=PTR(hand,0x30);
   /* Match objects and another client's ball must never be stolen. */
   if(!held||(lobby_is_ball(held)&&lobby_owned(held))){
    void* ball=lobby_recall_ball(hand);
    if(ball){root_set(&lobby_pending_hand,hand);root_set(&lobby_pending_ball,ball);}
   }
  }
  lobby_trigger_down[i]=(unsigned char)down;
 }
 lobby_hand_update_trampoline(hand,m);
 if(rooted(lobby_pending_hand)==hand){root_set(&lobby_pending_hand,0);root_set(&lobby_pending_ball,0);}
}
EXPORT void lobby_selector_hide_v21(void){
 void* page=rooted(lobby_page);void* menu=page?PTR(page,0x68):0;
 if(lobby_active()&&alive(menu))FN(0x318350,void(*)(void*,void*))(menu,0);
}
EXPORT void lobby_selector_show_v21(void){
 void* page=rooted(lobby_page);void* menu=page?PTR(page,0x68):0;
 if(lobby_active()&&alive(menu))FN(0x3183d0,void(*)(void*,void*))(menu,0);
}
EXPORT void lobby_update_hook(void* page,void* m){
 lobby_update_trampoline(page,m);
 if(!lobby_active())return;
 /* Native input helper reads global controllers and no InGame fields. */
 int down=FN(0x314470,_Bool(*)(void*,void*))(0,0);
 if(down&&!lobby_menu_down)lobby_selector_show_v21();lobby_menu_down=down;
}
EXPORT _Bool lobby_jump_area_hook(void* area,void* other,void* m){
 return lobby_active()?1:FN(0xa0c080,_Bool(*)(void*,void*,void*))(area,other,m);
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
