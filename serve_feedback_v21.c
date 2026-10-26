/* Own synthesized referee whistle; generated once, reused at each serve.
 * No downloaded sample or third-party recording is redistributed. */
static unsigned serve_whistle_source_v21,serve_whistle_clip_v21;
static int serve_feedback_pending_v21=1;
static void serve_feedback_arm_v21(void){serve_feedback_pending_v21=1;}
static void play_serve_whistle_v21(void* ball){
 if(!alive(rooted(serve_whistle_source_v21))){
  void* domain=FN(0x14a920,void*(*)(void))();
  void* assembly=domain?FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.AudioModule"):0;
  void* image=assembly?FN(0x14a530,void*(*)(void*))(assembly):0;
  void* klass=image?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","AudioSource"):0;
  if(!klass||!ball)return;
  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
  void* source=type?FN(0x94f240,void*(*)(void*,void*,void*))(gameobject(ball),type,0):0;
  if(!source)return;
  FN(0xebc590,void(*)(void*,float,void*))(source,0,0);
  FN(0xebc760,void(*)(void*,float,void*))(source,.32f,0);
  FN(0xebc370,void(*)(void*,_Bool,void*))(source,0,0);
  FN(0xebc500,void(*)(void*,_Bool,void*))(source,0,0);
  FN(0xebc460,void(*)(void*,_Bool,void*))(source,0,0);
  root_set(&serve_whistle_source_v21,source);
 }
 if(!alive(rooted(serve_whistle_clip_v21))){
  enum {count=6174};
  void* clip=FN(0xeba090,void*(*)(void*,int,int,int,_Bool,void*))(str("Cloudcourt_Original_Serve_Whistle"),count,1,22050,0,0);
  if(!clip)return;
  void* corlib=FN(0x14acb0,void*(*)(void))();
  void* single=corlib?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(corlib,"System","Single"):0;
  void* samples=single?FN(0x14a4f0,void*(*)(void*,U64))(single,count):0;
  if(!samples)return;
  float a=0,b=0;
  for(int i=0;i<count;i++){
   float t=i/(float)count,e=1;
   if(i<220)e=i/220.f;else if(i>count-1102)e=(count-i)/1102.f;
   a+=(2700.f+120.f*t)/22050.f;b+=(3160.f-60.f*t)/22050.f;
   if(a>=1)a-=1;if(b>=1)b-=1;
   float x=a<.5f?4*a-1:3-4*a,y=b<.5f?4*b-1:3-4*b;
   FLT(samples,0x20+i*4)=(x*.65f+y*.35f)*e*.68f;
  }
  if(!FN(0xeba5f0,_Bool(*)(void*,void*,int,void*))(clip,samples,0,0))return;
  root_set(&serve_whistle_clip_v21,clip);
 }
 void* source=rooted(serve_whistle_source_v21);
 FN(0xebc2d0,void(*)(void*,void*,void*))(source,rooted(serve_whistle_clip_v21),0);
 FN(0xebbe30,void(*)(void*,void*))(source,0);
}
static void serve_feedback_spawn_v21(void* ball){
 if(!serve_feedback_pending_v21||!ball||lobby_is_ball(ball))return;
 serve_feedback_pending_v21=0;landing_clear_v20();celebration_reset_v21();play_serve_whistle_v21(ball);
}
static void serve_feedback_motion_v21(void* ball,V3 p,V3 v,int hit,int touch,int team,int context){
 /* Exact existing bot serve placement: no touch, stationary, context 3.
  * Human waiting balls remain hidden until the local trigger event below. */
 if(!hit&&touch==-1&&team==-1&&context==3&&dot(v,v)<.00001f&&p.y>0&&p.y<10&&p.z>-15&&p.z<15)
  serve_feedback_spawn_v21(ball);
}
static void serve_feedback_human_v21(void* ball){
 int pending=serve_feedback_pending_v21;
 serve_feedback_spawn_v21(ball);
 if(pending&&!serve_feedback_pending_v21&&network_physics()){
  void* player=online_local_player();if(player)send_mod_choice(player,0x5c220000);
 }
}
static void serve_feedback_remote_v21(void* player){
 void* rules=rooted(rules_root);if(!rules||!player||!network_physics()||lobby_active())return;
 int team=INT(player,0x28);
 /* The current server is selected by the existing original rules lookup. */
 /* currentTeam (rules+0x7c) is host-only between rallies and may be stale
  * here. Validate the synchronized serving player instead. */
 if(team<0||team>1||FN(0x253580,void*(*)(void*,int,void*))(rules,team,0)!=player)return;
 void* k=PTR((void*)base(),0x15426f0),*s=k?PTR(k,0xb8):0;
 serve_feedback_spawn_v21(s?PTR(s,0):0);
}
