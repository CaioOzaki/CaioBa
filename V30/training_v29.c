/* Guided offline practice. Every result comes from the actual native ball:
 * landing (serve/spike) or a swept descending target plane (receive/set).
 * No bot, score RPC, synthetic hit or network object is taken over. */
EXPORT int training_drill_v29,training_attempts_v29,training_hits_v29;
EXPORT int training_phase_v29; /* 0 ready, 1 feed/serve, 2 accepted contact, 3 result */
EXPORT int training_difficulty_v29=1;
EXPORT float training_error_v29;
static int training_pending_v29,training_running_v29,training_qualified_v29;
static float training_elapsed_v29,training_cooldown_v29;
static V3 training_target_v29,training_previous_v29;
static int training_previous_valid_v29;
static const char* training_result_v29="Ready";
static const char* training_names_v29[4]={"SERVE","RECEIVE","SET","SPIKE"};
EXPORT float training_radius_v29(void){return training_difficulty_v29==0?1.45f:training_difficulty_v29==2?.75f:1.05f;}
EXPORT V3 training_target_position_v29(void){return training_target_v29;}
static void training_target_next_v29(void){
 float x=(training_attempts_v29%3-1)*2.2f;
 training_target_v29=(V3){x,.025f,6.1f};
 if(training_drill_v29==2)training_target_v29=(V3){0,2.15f,-1.65f};
 if(training_drill_v29==3)training_target_v29=(V3){x,3.1f,-1.25f};
 if(training_drill_v29==4)training_target_v29=(V3){-x,.025f,4.7f};
}
static void training_round_v29(void){
 training_phase_v29=0;training_qualified_v29=0;training_elapsed_v29=0;
 training_previous_valid_v29=0;training_error_v29=-1;training_result_v29="Ready";training_target_next_v29();
}
EXPORT int training_requested_v29(void){return training_pending_v29!=0;}
EXPORT int training_active_v29(void){return training_running_v29&&offline();}
EXPORT int training_request_v29(int drill){
 if(drill<1||drill>4)return 0;
 /* Do not authorize practice from a connected room, even before offlineMode
  * has settled. The root menu routes this only through native Solo Start. */
#ifndef TRAINING_CORE_ONLY_V29
 if(FN(0x61efc0,_Bool(*)(void*))(0)&&!offline())return 0;
#endif
 training_pending_v29=drill;return 1;
}
static void training_finish_v29(int hit,float error,const char* result){
 if(training_phase_v29!=1&&training_phase_v29!=2)return;
 training_attempts_v29++;training_hits_v29+=hit!=0;training_error_v29=error;
 training_phase_v29=3;training_result_v29=result;training_previous_valid_v29=0;
}
/* Plane intersection is swept across consecutive actual ball positions; a
 * fast ball cannot skip the target between Update frames. */
EXPORT int training_crossing_v29(V3 a,V3 b,V3 target,float radius,float* error){
 if(!finitev(a)||!finitev(b)||!finitev(target)||!(radius>0)||a.y<target.y||b.y>target.y||b.y>=a.y)return 0;
 float t=(target.y-a.y)/(b.y-a.y),x=a.x+(b.x-a.x)*t-target.x,z=a.z+(b.z-a.z)*t-target.z;
 float distance=sqroot(x*x+z*z);if(error)*error=distance;return distance<=radius?2:1;
}
EXPORT void training_observe_v29(V3 p,V3 velocity){
 if(!training_active_v29()||(training_phase_v29!=1&&training_phase_v29!=2)||!finitev(p)||!finitev(velocity))return;
 if((training_drill_v29==2||training_drill_v29==3)&&training_phase_v29==2&&training_previous_valid_v29){
  float error=0;int cross=training_crossing_v29(training_previous_v29,p,training_target_v29,training_radius_v29(),&error);
  if(cross)training_finish_v29(cross==2&&training_qualified_v29,error,cross==2&&training_qualified_v29?"TARGET HIT":"MISSED TARGET");
 }
 training_previous_v29=p;training_previous_valid_v29=1;
}
EXPORT void training_contact_v29(V3 p,V3 velocity,int hit,int isThrow,int id,int team){
 if(!training_active_v29()||training_phase_v29<1||training_phase_v29>2||!hit||isThrow||id<0||team!=0||!finitev(p)||!finitev(velocity))return;
 training_phase_v29=2;
 /* Receive must rise toward the setter; set must rise above the 2.4m net;
  * spike must be an above-tape contact directed into the opposite court. */
 training_qualified_v29=training_drill_v29==1?velocity.z>0:
   training_drill_v29==2?velocity.y>1&&velocity.z>0:
   training_drill_v29==3?velocity.y>2.5f:
   p.y>=2.4f&&p.z<.8f&&velocity.z>0;
 training_previous_v29=p;training_previous_valid_v29=1;
}
EXPORT void training_landed_at_v29(V3 p){
 if(!training_active_v29()||training_phase_v29<1||training_phase_v29>2||!finitev(p))return;
 float x=p.x-training_target_v29.x,z=p.z-training_target_v29.z,error=sqroot(x*x+z*z);
 int valid=(training_drill_v29==1||training_drill_v29==4)&&training_phase_v29==2&&training_qualified_v29;
 int hit=valid&&error<=training_radius_v29();
 training_finish_v29(hit,error,hit?"TARGET HIT":training_phase_v29==1?"NO CONTACT":"MISSED TARGET");
}
EXPORT V3 training_feed_v29(V3 destination,float seconds,V3 origin){
 if(!finitev(destination)||!finitev(origin)||seconds<.5f||seconds>4)return (V3){0,0,0};
 return (V3){(destination.x-origin.x)/seconds,(destination.y-origin.y)/seconds+4.905f*seconds,(destination.z-origin.z)/seconds};
}
#ifndef TRAINING_CORE_ONLY_V29
static unsigned training_rules_root_v29,training_ball_root_v29,training_hands_v29[2],training_pending_hand_v29;
static unsigned training_target_roots_v29[3];
static unsigned char training_trigger_v29[2];
static int training_ui_dirty_v29=1;
static float training_ui_at_v29;
typedef struct {unsigned text;float size,min,max,alpha;int automatic;} TrainingTmpV29;
static TrainingTmpV29 training_tmp_v29[3];
static unsigned training_canvas_v29;
static float training_canvas_alpha_v29;
static void training_tmp_restore_v29(void){
 for(int i=0;i<3;i++){
  TrainingTmpV29* s=&training_tmp_v29[i];void* t=rooted(s->text);
  if(alive(t)){
   FN(0x23f480,void(*)(void*,_Bool,void*))(t,0,0);
   FN(0x23f980,void(*)(void*,float,void*))(t,s->min,0);FN(0x23f930,void(*)(void*,float,void*))(t,s->max,0);
   FN(0x23f9d0,void(*)(void*,float,void*))(t,s->size,0);FN(0x23f480,void(*)(void*,_Bool,void*))(t,s->automatic,0);
   FN(0x23f2a0,void(*)(void*,float,void*))(t,s->alpha,0);
  }root_set(&s->text,0);
 }
 void* group=rooted(training_canvas_v29);if(alive(group))FN(0xeccee0,void(*)(void*,float,void*))(group,training_canvas_alpha_v29,0);root_set(&training_canvas_v29,0);
}
static void training_tmp_style_v29(void* rules){
 for(int i=0;i<3;i++){
  TrainingTmpV29* s=&training_tmp_v29[i];void* t=PTR(rules,0x28+i*8);if(!alive(t))continue;
  if(rooted(s->text)!=t){
   root_set(&s->text,t);s->size=FN(0x23e820,float(*)(void*,void*))(t,0);s->min=FN(0x23e810,float(*)(void*,void*))(t,0);s->max=FN(0x23e800,float(*)(void*,void*))(t,0);
   s->alpha=FN(0x23e4a0,float(*)(void*,void*))(t,0);s->automatic=FN(0x23e600,_Bool(*)(void*,void*))(t,0);
   /* Native scoreboard TMP rects are 611x50 / 389x50 / 389x50.
    * Fit long practice hints and two-line results only for this session. */
   FN(0x23f980,void(*)(void*,float,void*))(t,i==2?12:14,0);FN(0x23f930,void(*)(void*,float,void*))(t,i==1?20:i==2?14:18,0);
   FN(0x23f480,void(*)(void*,_Bool,void*))(t,1,0);
  }
  FN(0x23f2a0,void(*)(void*,float,void*))(t,1,0);
 }
 if(!alive(rooted(training_canvas_v29))){
  void* score=PTR(rules,0x30);void* parent=score?FN(0xb739d0,void*(*)(void*,void*))(transform(score),0):0;
  void* group=parent?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(parent),str("CanvasGroup"),0):0;
  if(alive(group)){root_set(&training_canvas_v29,group);training_canvas_alpha_v29=FN(0xecce20,float(*)(void*,void*))(group,0);}
 }
 void* group=rooted(training_canvas_v29);if(alive(group))FN(0xeccee0,void(*)(void*,float,void*))(group,1,0);
}
static void training_text_v29(void* text,const char* value){if(alive(text))FN(0x2405f0,void(*)(void*,void*,void*))(text,str(value),0);}
static void training_show_targets_v29(int show){
 const char* names[3]={"GroundTarget","AirTarget","Origin"};
 void* t=0;
 if(show){
  void* go=FN(0x94f3d0,void*(*)(void*,void*))(str("CC_TrainingTargets"),0);
  /* Find returns GameObject, not Component. Its get_transform is a
   * different IL2CPP method; Component.get_transform dereferences wrong data. */
  t=go?FN(0x94fb00,void*(*)(void*,void*))(go,0):0;
 }
 for(int i=0;i<3;i++){
  void* child=rooted(training_target_roots_v29[i]);
  if(!alive(child)&&t){child=find_child(t,names[i]);root_set(&training_target_roots_v29[i],child);}
  if(!alive(child))continue;
  int use=i==2||((training_drill_v29==1||training_drill_v29==4)?i==0:i==1);
  FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(child),show&&use,0);
  if(i<2){position_set(child,training_target_v29);float radius=training_radius_v29();FN(0xb75560,SetVec)(child,(V3){radius,1,radius},0);}
  else position_set(child,(V3){training_drill_v29==3?training_target_v29.x:0,.025f,training_drill_v29==1?-7.6f:training_drill_v29==4?-1.7f:-5.2f});
 }
}
static void training_detach_v29(void* ball){
 if(!alive(ball))return;void* hand=PTR(ball,0xd8);
 if(alive(hand)&&PTR(hand,0x30)==ball)managed_field(hand,0x30,0);
 FN(0xb755b0,void(*)(void*,void*,void*))(transform(ball),0,0);
 BYTE(ball,0xd0)=0;managed_field(ball,0xd8,0);
}
EXPORT void training_reset_v29(void){
 training_tmp_restore_v29();
 training_show_targets_v29(0);
 void* ball=rooted(training_ball_root_v29);if(alive(ball)&&offline()){
  training_detach_v29(ball);FN(0x77ea70,void(*)(void*,void*))(ball,0);serve_visible(ball,0);position_set(transform(ball),(V3){0,-100,0});
 }
 training_running_v29=training_pending_v29=0;training_phase_v29=0;training_cooldown_v29=0;
 root_set(&training_rules_root_v29,0);root_set(&training_ball_root_v29,0);root_set(&training_pending_hand_v29,0);
 for(int i=0;i<2;i++){root_set(&training_hands_v29[i],0);training_trigger_v29[i]=1;}
 for(int i=0;i<3;i++)root_set(&training_target_roots_v29[i],0);
}
EXPORT void training_begin_v29(void* rules){
 int request=training_pending_v29;training_reset_v29();
 if(!request||!offline()||!rules)return;
 training_drill_v29=request;training_running_v29=1;training_attempts_v29=training_hits_v29=0;
 root_set(&training_rules_root_v29,rules);training_round_v29();training_ui_at_v29=0;training_ui_dirty_v29=1;
}
static void* training_get_ball_v29(void){
 void* ball=rooted(training_ball_root_v29);if(alive(ball))return ball;
 ball=v19_ball();
 if(!alive(ball)){
  Q4 rotation={0,0,0,1};void* go=FN(0x60fb50,void*(*)(void*,V3,Q4,unsigned char,void*,void*))(str("Volleyball"),(V3){0,-100,0},rotation,0,0,0);
  ball=go?FN(0x94f410,void*(*)(void*,void*,void*))(go,str("Volleyball"),0):0;
 }
 if(!alive(ball))return 0;root_set(&training_ball_root_v29,ball);return ball;
}
static int training_start_attempt_v29(void* hand){
 if(!training_active_v29()||training_cooldown_v29>0)return 0;
 void* ball=training_get_ball_v29();if(!ball)return 0;
 training_detach_v29(ball);FN(0x77ea70,void(*)(void*,void*))(ball,0);
 BYTE(ball,0x88)=1;BYTE(ball,0x89)=1;INT(ball,0xc0)=3;
 training_round_v29();training_phase_v29=1;training_result_v29="IN FLIGHT";training_cooldown_v29=.35f;training_ui_dirty_v29=1;
 void* rules=rooted(training_rules_root_v29);
 if(rules){BYTE(rules,0x78)=1;BYTE(rules,0x79)=0;BYTE(rules,0x7a)=0;INT(rules,0x7c)=0;INT(rules,0x98)=-1;INT(rules,0x9c)=training_drill_v29==3?1:training_drill_v29==4?2:0;}
 serve_visible(ball,1);training_show_targets_v29(1);
 if(training_drill_v29==1){if(!hand_ball_place_v26(ball,hand))return 0;root_set(&training_pending_hand_v29,hand);return 1;}
 void* player=rooted(local_player_root);V3 pp=player?player_court_position(player):(V3){0,0,-5.2f};
 if(!finitev(pp))pp=(V3){0,0,-5.2f};
 if(pp.x< -3)pp.x=-3;if(pp.x>3)pp.x=3;
 float variation=(training_attempts_v29%3-1)*(training_difficulty_v29==2?.6f:training_difficulty_v29==0?0:.3f);
 V3 origin,destination;float seconds;
 if(training_drill_v29==2){origin=(V3){variation,3.5f,5.5f};destination=(V3){pp.x+variation,1.1f,pp.z};seconds=1.8f;}
 else if(training_drill_v29==3){origin=(V3){pp.x-1.4f,2.7f,pp.z+1.5f};destination=(V3){pp.x+variation,1.85f,pp.z};seconds=1.25f;}
 else {origin=(V3){pp.x-1.2f,3.0f,pp.z+.8f};destination=(V3){pp.x+variation,3.0f,pp.z+.15f};seconds=1.5f;}
 V3 velocity=training_feed_v29(destination,seconds,origin);
 /* Native offline InvokeRpc_ChangeMotion unfreezes both rigidbodies and
  * updates the prediction/collision state. Feed is not credited as a hit. */
 FN(0x77e5c0,void(*)(void*,V3,V3,_Bool,_Bool,int,int,int,void*))(ball,origin,velocity,0,0,-1,1,3,0);
 return 1;
}
EXPORT void training_hand_update_v29(void* hand){
 if(!training_active_v29()||!hand)return;
 void* player=rooted(local_player_root),*body=player?PTR(player,0x80):0;
 if(!body||!FN(12008720,_Bool(*)(void*,void*,void*))(transform(hand),transform(body),0))return;
 int i=BYTE(hand,0x24)?1:0;
 if(rooted(training_hands_v29[i])!=hand){root_set(&training_hands_v29[i],hand);training_trigger_v29[i]=1;}
 int down=spawn_trigger_v24(hand);
 if(down&&!training_trigger_v29[i]&&!ui_pointer_over_button_v19())training_start_attempt_v29(hand);
 training_trigger_v29[i]=(unsigned char)down;
}
EXPORT void* training_hand_ball_v29(void* hand){
 if(!training_active_v29()||rooted(training_pending_hand_v29)!=hand)return 0;
 root_set(&training_pending_hand_v29,0);return rooted(training_ball_root_v29);
}
EXPORT void training_motion_v29(void* ball,V3 p,V3 velocity,int hit,int isThrow,int id,int team){
 if(training_active_v29()&&ball==rooted(training_ball_root_v29))training_contact_v29(p,velocity,hit,isThrow,id,team);
}
EXPORT int training_ball_ground_v29(void* ball){
 if(!training_active_v29())return 0;
 if(ball==rooted(training_ball_root_v29))training_landed_at_v29(position(transform(ball)));
 return 1;
}
static char* training_num_v29(char* out,int value){char b[12];int n=0;do{b[n++]=(char)('0'+value%10);value/=10;}while(value&&n<11);while(n)*out++=b[--n];return out;}
static void training_hud_v29(void* rules){
 char text[160],*p=text;const char* s=training_names_v29[training_drill_v29-1];while(*s)*p++=*s++;
 s=" PRACTICE  |  ";while(*s)*p++=*s++;p=training_num_v29(p,training_hits_v29);*p++='/';p=training_num_v29(p,training_attempts_v29);
 s=" TARGETS\n";while(*s)*p++=*s++;s=training_result_v29;while(*s)*p++=*s++;
 if(training_error_v29>=0&&training_phase_v29==3){s="  |  ERROR ";while(*s)*p++=*s++;int dec=(int)(training_error_v29*10+.5f);p=training_num_v29(p,dec/10);*p++='.';*p++=(char)('0'+dec%10);*p++='m';}*p=0;
 training_tmp_style_v29(rules);
 training_text_v29(PTR(rules,0x30),text);training_text_v29(PTR(rules,0x38),"TRIGGER: REPEAT  |  MENU: CHANGE DRILL / EXIT");
 const char* hint=training_drill_v29==1?"Stand on the blue ring. Trigger: ball to palm. Toss, then serve into the gold ring.":training_drill_v29==2?"Stand behind the blue ring. Trigger: incoming feed. Forearm pass up through the gold ring.":training_drill_v29==3?"Move to the blue ring. Trigger: soft feed. Set upward through the gold ring; use both grips for set pose.":"Move near the blue ring. Trigger: high set. Contact above the tape and spike into the gold ring.";
 training_text_v29(PTR(rules,0x28),hint);
}
EXPORT void training_tick_v29(void){
 if(!training_running_v29)return;
 void* rules=rooted(training_rules_root_v29);
 if(!offline()||!alive(rules)||rooted(rules_root)!=rules){training_reset_v29();return;}
 float dt=FN(0xb72960,float(*)(void*))(0);if(!(dt>=0&&dt<=.25f))dt=0;
 if(training_cooldown_v29>0)training_cooldown_v29-=dt;
 BYTE(rules,0x78)=1;BYTE(rules,0x79)=0;BYTE(rules,0x7a)=0;
 void* ball=rooted(training_ball_root_v29);
 if(alive(ball)&&training_phase_v29>0&&training_phase_v29<3){
  training_elapsed_v29+=dt;V3 p=position(transform(ball)),v=*(V3*)((char*)ball+0x8c);
  training_observe_v29(p,v);
  if(training_elapsed_v29>12||!finitev(p)||p.y<-.5f||p.x< -18||p.x>18||p.z< -24||p.z>24)training_finish_v29(0,0,"TRY AGAIN");
 }
 float now=FN(0xb72b40,float(*)(void*))(0);
 if(training_ui_dirty_v29||now>=training_ui_at_v29){training_hud_v29(rules);training_show_targets_v29(1);training_ui_at_v29=now+.2f;training_ui_dirty_v29=0;}
}
EXPORT int training_button_v29(void* button){
 if(named(button,"CC_TrainEasy")){training_difficulty_v29=0;training_ui_dirty_v29=1;return 1;}
 if(named(button,"CC_TrainStandard")){training_difficulty_v29=1;training_ui_dirty_v29=1;return 1;}
 if(named(button,"CC_TrainChallenge")){training_difficulty_v29=2;training_ui_dirty_v29=1;return 1;}
 if(named(button,"CC_TrainRepeat")){if(training_active_v29()&&training_drill_v29!=1)training_start_attempt_v29(0);return 1;}
 return 0;
}
#endif
