/* Landing-only feedback. Reuse the existing reliable EndRally RPC: bit6 marks
 * a floor point, bit7 means out; the Vector3 becomes its actual contact point.
 * Score team/reason retain their v19 bits. No collider, rules or new RPC added. */
TRAMP(void,landing_collision,(void* ball,void* collision,void* m))
static void* landing_contact_ball_v20;
static V3 landing_contact_v20,landing_pending_v20;
static int landing_contact_valid_v20,landing_pending_valid_v20,landing_pending_out_v20;
static unsigned landing_marks_v20[2];

EXPORT void landing_collision_hook(void* ball,void* collision,void* m){
 landing_contact_ball_v20=ball;landing_contact_valid_v20=0;
 if(ball&&collision&&!lobby_is_ball(ball)){
  int count=INT(collision,0x38);void* contacts=PTR(collision,0x40);
  if(!contacts)contacts=PTR(collision,0x48);
  if(contacts&&count>0&&count<=64&&*(U64*)((char*)contacts+0x18)>0){
   V3 point=*(V3*)((char*)contacts+0x20),normal=*(V3*)((char*)contacts+0x2c);
   if(finitev(point)&&finitev(normal)&&normal.y>.5f){landing_contact_v20=point;landing_contact_valid_v20=1;}
  }
 }
 landing_collision_trampoline(ball,collision,m);
 landing_contact_ball_v20=0;landing_contact_valid_v20=0;
}
static void landing_prepare_v20(void* ball,V3 center){
 landing_pending_valid_v20=0;
 if(!ball||!finitev(center)||lobby_is_ball(ball))return;
 /* Match the original BallGrounded strict court bounds, including its exact
  * boundary behavior, rather than changing which team receives the point. */
 landing_pending_out_v20=!(center.x> -4.5f&&center.x<4.5f&&center.z> -9.f&&center.z<9.f);
 if(ball==landing_contact_ball_v20&&landing_contact_valid_v20)landing_pending_v20=landing_contact_v20;
 else{
  float r=FN(0x77fe10,float(*)(void*,void*))(ball,0);
  if(!(r>.02f&&r<.5f))r=.11f;
  landing_pending_v20=center;landing_pending_v20.y-=r;
 }
 landing_pending_valid_v20=finitev(landing_pending_v20);
}
static int landing_wire_flags_v20(void){return landing_pending_valid_v20?0x40|(landing_pending_out_v20?0x80:0):0;}
EXPORT void* landing_position_box_hook(void* klass,void* value){
 V3 point=*(V3*)value;
 if(landing_pending_valid_v20){point=landing_pending_v20;landing_pending_valid_v20=0;}
 return FN(0x14ba70,void*(*)(void*,void*))(klass,&point);
}
static void landing_find_marks_v20(void){
 if(alive(rooted(landing_marks_v20[0]))&&alive(rooted(landing_marks_v20[1])))return;
 void* go=FN(0x94f3d0,void*(*)(void*,void*))(str("CC_LandingMarks"),0);
 void* root=go?FN(0x94fb00,void*(*)(void*,void*))(go,0):0;
 for(int i=0;i<2;i++)root_set(&landing_marks_v20[i],find_child(root,i?"Out":"In"));
}
static void landing_clear_v20(void){
 landing_pending_valid_v20=0;
 for(int i=0;i<2;i++){void* t=rooted(landing_marks_v20[i]);if(alive(t))FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),0,0);}
}
static void landing_show_v20(V3 point,int outside){
 if(!finitev(point))return;
 landing_find_marks_v20();
 for(int i=0;i<2;i++){
  void* t=rooted(landing_marks_v20[i]);if(!alive(t))continue;
  if(i==outside){point.y+=.014f;position_set(t,point);}
  FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),i==outside,0);
 }
}
