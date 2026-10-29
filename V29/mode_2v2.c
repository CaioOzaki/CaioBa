/* Solo doubles for the exact Steam build recorded in the patch manifest.
 * Uses existing Unity buttons, task handlers, spawning and rally rules.
 * No persistent settings are changed. No per-frame allocations or searches.
 */
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define FLT(o,n) (*(float*)((char*)(o)+(n)))
#define BYTE(o,n) (*((unsigned char*)(o)+(n)))
#define TRAMP(ret,name,args) EXPORT __attribute__((naked)) ret name##_trampoline args {__asm__(".rept 32; int3; .endr");}
TRAMP(void,solo_awake,(void* o,void* m))
TRAMP(void*,solo_entry,(void* o,void* m))
TRAMP(void*,online_entry,(void* o,void* m))
TRAMP(void,main_menu,(void* o,void* argument,void* m))
TRAMP(void*,solo_day,(void* o,void* m))
TRAMP(void*,solo_night,(void* o,void* m))
TRAMP(void*,solo_bomb_v28,(void* o,void* m))
TRAMP(void*,solo_back,(void* o,void* m))
TRAMP(void*,solo_start,(void* o,void* env,_Bool bomb,void* m))
TRAMP(void,game_go,(void* o,void* m))
TRAMP(void,spawn_bot,(void* o,void* prefab,int team,int slot,float yaw,void* m))
TRAMP(void,add_player,(void* o,void* player,int slot,void* m))
TRAMP(void,bot_body,(void* o,void* m))
TRAMP(void*,pass_target,(void* o,void* m))
TRAMP(void,tracked_touch,(void* rules,int player,int team,void* m))
TRAMP(void,bot_hit,(void* bot,void* ball,void* m))
TRAMP(_Bool,serve_routine,(void* routine,void* m))
TRAMP(void,bot_assess,(void* bot,void* m))
TRAMP(_Bool,player_jump,(void* routine,void* m))
EXPORT float bot_serve_spawn_delay=3.0f;
EXPORT int doubles_enabled=0;
EXPORT int quartet_enabled=0;
static unsigned local_player_root;
static int member_role(void* member);
static int quartet_setup(void* bot);
static void* quartet_pass(void* bot,void* target,void* m);
static void hand_serve_reset(void);
static void online_session_reset_v26(void);
static void ball_style_reset_v26(void);
static void clamp_local_player_v26(void* body);
EXPORT int solo_stage=0; /* 0 format selector, 4 original courts, 2 doubles courts */
EXPORT int doubles_requested=0;
EXPORT float doubles_speed=1.40f;
EXPORT float doubles_player_speed=1.60f;
EXPORT float doubles_ally_speed=1.60f;
EXPORT float doubles_serve_height_extra=2.0f;
EXPORT float doubles_set_extra=1.65f;
EXPORT int doubles_spawned=0;
EXPORT int doubles_team_counts[2]={0,0};
EXPORT U64 doubles_high_sets=0;
static unsigned page_root,day_text_root,night_text_root;
static unsigned rules_root;
EXPORT int online_version_ready=0;
EXPORT int online_format=2;
EXPORT int online_bomb_v28=0;
static int net_last_id_v28=-1;
static int net_first_touch=0,net_serve_team=-1;
static int net_touch_team=-1,net_touch_count=0,net_rally_active=0;
EXPORT int online_selector=0;
static unsigned online_start_root;
static int online_mode(void){return online_version_ready&&online_format==2&&!offline();}
static void* online_local_player(void);
static int online_reception(void* player);
static int network_physics(void);
static int chosen_skin(void* player);
static void cloudcourt_avatar_tick(void* body);
static int preferred_style(void);
static int settings_button_v28(void* button);
static void settings_close_v28(void);
static float audio_gain_v28(int category);
static void customization_reset_v28(void);
static void customization_preferences_v28(void);
static void customization_mirror_refresh_v28(void* panel);
static int customization_button_v28(void* button);
static int appearance_receive_v28(void* player,int value);
static int appearance_pack_v28(void);
static int player_cosmetic_v28(void* player,int arms);
EXPORT void avatar_cosmetics_v28(void* body);

static void ensure_preferences_v19(void);
static int customization_button_v19(void* button);
static void customization_close_v19(void);
static void graphics_start_v24(void);
static int graphics_button_v24(void* button);
static void graphics_close_v24(void);
static void map_label_v19(void);
static int ui_input_v19(int value);
static int ui_button_valid_v19(void* button);
static void ui_click_v19(void* button);
static int ui_pointer_over_button_v19(void);
static void landing_prepare_v20(void* ball,V3 center);
static int landing_wire_flags_v20(void);
static void landing_clear_v20(void);
static void landing_show_v20(V3 point,int outside);
static int v19_word(void* text,const char* word);
EXPORT void score_outline_tmp_force_v21(void* text);
EXPORT void avatar_hands_v21(void* body);
EXPORT void avatar_sleeves_v24(void* body);
EXPORT void celebration_point_v21(void* rules,int team);
EXPORT int celebration_wire_v24(void* rules,int team);
EXPORT void celebration_point_wire_v24(void* rules,int team,int wire);
static void celebration_serve_touch_v24(void* rules,int player,int team);
EXPORT void celebration_reset_v21(void);
EXPORT void celebration_bot_v21(void* bot);
static void serve_feedback_arm_v21(void);
static void serve_feedback_motion_v21(void* ball,V3 p,V3 v,int hit,int touch,int team,int context);
static void serve_feedback_human_v21(void* ball);
static void serve_feedback_remote_v21(void* player);
static void send_mod_choice(void* player,int value);
EXPORT void lobby_selector_hide_v21(void);
EXPORT void lobby_selector_show_v21(void);
EXPORT void bots_roster_reset_v20(void* rules);
EXPORT void bots_spawn_begin_v20(void* rules,int team,int slot);
EXPORT void bots_spawn_end_v20(void);
static void finish_team_changes(void);
static int bot_has_human_mate(void* bot);
static int player_is_airborne(void* player);
static unsigned jumping_player_root;
static int player_airborne;
static V3 jump_takeoff;
EXPORT int serve_flight_team=-1;
static int serve_fault;
static int deferred_serve_point=-1;
static int point_reason=0;
static void point_message(void* rules,int team,int reason);
static void* transform(void* o);
static V3 position(void* t);
static V3 player_court_position(void* player){
 void* body=PTR(player,0x80);
 void* torso=body?PTR(body,0x38):0;
 return position(torso?torso:transform(player));
}
EXPORT int reception_pending=0;
static int reception_context;
static void* rooted(unsigned h){return h?FN(0x14ac80,void*(*)(unsigned))(h):0;}
static void root_set(unsigned* h,void* obj){
 if(*h)FN(0x14ac70,void(*)(unsigned))(*h);
 *h=obj?FN(0x14ac90,unsigned(*)(void*,_Bool))(obj,0):0;
}
static void managed_field(void* obj,int offset,void* value){
 FN(0x14ac30,void(*)(void*,void**,void*))(obj,(void**)((char*)obj+offset),value);
}
/* v29 modules are composed after common helpers; shared entry hooks use these contracts. */
EXPORT int training_requested_v29(void);
EXPORT int training_active_v29(void);
EXPORT int training_request_v29(int);
EXPORT void training_begin_v29(void*);
EXPORT void training_reset_v29(void);
EXPORT void training_hand_update_v29(void*);
EXPORT void* training_hand_ball_v29(void*);
EXPORT void training_motion_v29(void*,V3,V3,int,int,int,int);
EXPORT int training_ball_ground_v29(void*);
EXPORT void training_tick_v29(void);
EXPORT int training_button_v29(void*);
static int refinement_button_v29(void*);
static void refinement_close_v29(void);
static void refinement_tick_v29(void);
static void refinement_menu_v29(void);
EXPORT void bots_team_v29(void*);
EXPORT void bots_assess_v29(void*);
EXPORT void bots_before_body_v29(void*);
EXPORT void bots_visual_v29(void*);
EXPORT void bots_point_v29(void*,int);
EXPORT void bots_reset_v29(void);
EXPORT void bots_rally_reset_v29(void);
EXPORT void bots_ik_before_v29(void*);
EXPORT void bots_ik_after_v29(void*);
EXPORT void stats_prepare_v29(void*);
EXPORT void stats_motion_v29(void*,V3,V3,int,int,int);
EXPORT void stats_point_v29(void*,int,int);
EXPORT void stats_tick_v29(void);
EXPORT void stats_session_reset_v29(void);
EXPORT void stats_open_v29(void*);
EXPORT void stats_menu_v29(void*);
EXPORT void rewards_load_v29(void);
EXPORT void rewards_progress_v29(int,int);
EXPORT void rewards_body_v29(void*,void*,int);
EXPORT void rewards_mirror_v29(void*);
EXPORT int rewards_button_v29(void*);
EXPORT void rewards_refresh_v29(void*);
EXPORT void rewards_tick_v29(void);
EXPORT void rewards_reset_v29(void);
EXPORT int rewards_packet_v29(void);
EXPORT int rewards_receive_v29(void*,int);
#include "rules_bomb_v28.c"
/* Yield AFTER any rotation has completed and BEFORE the serve placement.
 * State 1 proceeds directly only when the serving team has not changed;
 * state 2 resumes after the existing rotation pause. Private states 101/102
 * restore their original continuation after one Unity WaitForSeconds.
 * This host-side coroutine also serves standard 4v4; no doubles gate. */
EXPORT _Bool serve_routine_hook(void* routine,void* m){
 if(training_active_v29())return 0;
 int state=INT(routine,0x10);
 if(state==0){point_reason=0;serve_flight_team=-1;serve_fault=0;deferred_serve_point=-1;}
 if(state==101||state==102){INT(routine,0x10)=state-100;return serve_routine_trampoline(routine,m);}
 void* rules=PTR(routine,0x20);int team=INT(routine,0x28);
 if(rules&&!BYTE(rules,0x68)&&(state==2||(state==1&&team==INT(rules,0x90)))){
  void* player=FN(0x253580,void*(*)(void*,int,void*))(rules,team,0);
  if(!player){
   /* Initialized by the original durationServe wait before either state. */
   void* klass=*(void**)(base()+0x1514f48);
   if(klass){
    void* wait=FN(0x1c22e0,void*(*)(void*))(klass);
    FN(0xb7b820,void(*)(void*,float,void*))(wait,bot_serve_spawn_delay,0);
    managed_field(routine,0x18,wait);INT(routine,0x10)=state+100;return 1;
   }
  }
 }
 _Bool result=serve_routine_trampoline(routine,m);
 /* Human serve contact occurs while ballInPlay is still false. State 3
  * resumes after ownership is returned and enables rally scoring. */
 if(state==3&&rules&&deferred_serve_point>=0&&BYTE(rules,0x78)){
  int winner=deferred_serve_point;deferred_serve_point=-1;
  FN(0x2533a0,void(*)(void*,int,void*))(rules,winner,0);
 }
 return result;
}
/* A serve is an accepted touch made while serveInProgress is set. Tracking
 * accepted touches avoids consuming assistance on a rejected collision.
 * The first contact by either receiver consumes it, including the ally bot. */
EXPORT void tracked_touch_hook(void* rules,int player,int team,void* m){
 if(training_active_v29())return;
 if(rules&&(BYTE(rules,0x78)||(BYTE(rules,0x79)&&BYTE(rules,0x94)))&&!BYTE(rules,0x68)&&team>=0&&team<2){
  int serving=BYTE(rules,0x79),isbot=0;void* member=0;
  if(serving&&BYTE(rules,0x78)){serve_fault=0;serve_flight_team=-1;}
  if(serve_fault)return;
  void* teams=PTR(rules,0x60);void* side=teams?PTR(teams,0x20+team*8):0;
  if(side&&(serving||serve_flight_team==1-team)){
   for(int kind=0;kind<2&&!member;kind++){
    void* list=PTR(side,kind?0x30:0x38);void* items=list?PTR(list,0x10):0;
    int count=list?INT(list,0x18):0;
    if(items&&count>=0&&count<=4)for(int i=0;i<count;i++){
     void* candidate=PTR(items,0x20+i*8);
     if(candidate&&FN(0x30cb70,int(*)(void*,void*))(candidate,0)==player){member=candidate;isbot=kind;break;}
    }
   }
  }
  /* A serve cannot be recovered by a second contact from its own team,
   * even if it rebounds off the net. A net graze that crosses is legal. */
  int fault=!serving&&serve_flight_team==team;
  if(member&&serving&&!isbot){
   /* Judge the avatar's ground origin, not the hand or ball over the line.
    * A jump serve uses the origin at takeoff. */
   V3 p=player_airborne&&rooted(jumping_player_root)==member?jump_takeoff:player_court_position(member);
   fault=team==0?p.z>=-9.0f:p.z<=9.0f;
  }else if(member&&serve_flight_team==1-team){
   fault=v28_block(rules,player,team);
  }
  if(fault){
   point_reason=serving?5:serve_flight_team==team?6:7;
   serve_fault=1;serve_flight_team=-1;reception_pending=0;
   if(BYTE(rules,0x78))FN(0x2533a0,void(*)(void*,int,void*))(rules,1-team,0);
   else deferred_serve_point=1-team;
   return;
  }
  /* Native PlayerTouchedBall ignores the accepted human serve until its
   * coroutine enables ballInPlay. Preserve display-only ace attribution. */
  if(serving&&member&&!isbot&&!BYTE(rules,0x78))celebration_serve_touch_v24(rules,player,team);
  serve_flight_team=serving?team:-1;
 }
 if(doubles_enabled&&rules&&BYTE(rules,0x78)){
  reception_pending=BYTE(rules,0x79)&&team==1;
 }
 /* Apply the exception only to a first opponent interception, never a serve
  * or a teammate's set. Keep native Bomb fuse/explosion decisions intact. */
 int block=rules&&!BYTE(rules,0x68)&&BYTE(rules,0x78)&&!BYTE(rules,0x79)&&serve_flight_team<0&&
           team>=0&&team<2&&INT(rules,0x7c)==1-team&&(accepted_block_v28||v28_block(rules,player,team));
 tracked_touch_trampoline(rules,player,team,m);
 if(block&&BYTE(rules,0x78)&&INT(rules,0x7c)==team&&INT(rules,0x98)==player){
  INT(rules,0x9c)=v28_indoor()?0:1;INT(rules,0x98)=-1;
 }
}
/* The parent jump routine enters cooldown state 3 after landing. The
 * player's jumping bool stays set during cooldown, so it is not suitable
 * for deciding a receiving fault. States 1/2 await the actual jump. */
EXPORT _Bool player_jump_hook(void* routine,void* m){
 int state=INT(routine,0x10);void* player=PTR(routine,0x20);
 if(state==0&&player){root_set(&jumping_player_root,player);jump_takeoff=player_court_position(player);player_airborne=1;}
 if(state==1||state==2)player_airborne=0;
 _Bool result=player_jump_trampoline(routine,m);
 if(INT(routine,0x10)==3||!result)player_airborne=0;
 return result;
}
static int receiving_serve(void* bot){
 void* rules=rooted(rules_root);
 if(!rules||!bot||!BYTE(rules,0x78)||BYTE(rules,0x68))return 0;
 int team=INT(bot,0x28);
 return BYTE(rules,0x79)?INT(rules,0x7c)==1-team:serve_flight_team==1-team;
}
EXPORT void bot_assess_hook(void* bot,void* m){
 int receiving=receiving_serve(bot);unsigned char allow=BYTE(bot,0x38);
 void* rules=rooted(rules_root);
 int no_block=0; /* Teammate bots may make legitimate net blocks. */
 if(receiving||no_block)BYTE(bot,0x38)=0;
 bot_assess_trampoline(bot,m);BYTE(bot,0x38)=allow;
 /* Update inlines the jump decision: only the High tactic initiates it. */
 if((receiving||no_block)&&INT(bot,0xa4)==1)INT(bot,0xa4)=2;
 if(rules&&BYTE(rules,0x78)&&!BYTE(rules,0x79)&&!BYTE(rules,0x68)&&serve_flight_team==INT(bot,0x28))INT(bot,0xa4)=0;
 bots_assess_v29(bot);
}
static void reception_begin(void* body){
 reception_context=0;
 if((!doubles_enabled&&!quartet_enabled)||!body)return;
 void* player=PTR(body,0x168);if(!player)return;
 if(network_physics()){
  reception_context=online_reception(player);
  return;
 }
 void* rules=rooted(rules_root);
 if(rules&&offline()&&player==rooted(local_player_root)&&BYTE(rules,0x78)&&!BYTE(rules,0x79))
  reception_context=INT(rules,0x7c)!=INT(player,0x28)||INT(rules,0x9c)==0;
}
static void reception_end(void){reception_context=0;}
/* Replaces only the inlined PlayerPrefs read in the player's hit routine.
 * The settings menu and saved preference are untouched. */
EXPORT int reception_assist_hook(void* key,int fallback,void* m){
 if(doubles_enabled||quartet_enabled)return reception_context;
 return FN(0xa12690,int(*)(void*,int,void*))(key,fallback,m);
}
static int ally_setup(void* bot){
 if(!doubles_enabled||!bot||!bot_has_human_mate(bot))return 0;
 void* rules=rooted(rules_root);
 if(!rules||BYTE(rules,0x68)||!BYTE(rules,0x78)||BYTE(rules,0x79))return 0;
 int used=INT(rules,0x7c)==INT(bot,0x28)?INT(rules,0x9c):0;
 return used>=0&&used<2;
}
EXPORT void bot_hit_hook(void* bot,void* ball,void* m){
 void* serving_rules=rooted(rules_root);
 if(serving_rules&&BYTE(serving_rules,0x79)&&!BYTE(serving_rules,0x68)){
  float apex=FLT(bot,0x44),smack=FLT(bot,0x48);
  FLT(bot,0x44)=apex+.65f;FLT(bot,0x48)=smack+.65f;
  bot_hit_trampoline(bot,ball,m);FLT(bot,0x44)=apex;FLT(bot,0x48)=smack;return;
 }
 if(!ally_setup(bot)&&!quartet_setup(bot)){
  float apex=FLT(bot,0x44),smack=FLT(bot,0x48);
  int attack=serving_rules&&(doubles_enabled||quartet_enabled)&&BYTE(serving_rules,0x78)&&!BYTE(serving_rules,0x79)&&INT(serving_rules,0x7c)==INT(bot,0x28)&&INT(serving_rules,0x9c)>=2;
  if(attack){FLT(bot,0x44)=apex+.6f;FLT(bot,0x48)=smack+.75f;}
  bot_hit_trampoline(bot,ball,m);FLT(bot,0x44)=apex;FLT(bot,0x48)=smack;return;
 }
 int tactic=INT(bot,0xa4);float chance=FLT(bot,0x4c),failure=FLT(bot,0x50);
 /* The original pass branch requires tactic 2, >=2 remaining touches and a
  * successful probability check. Keep its own throw solver and hit rules. */
 INT(bot,0xa4)=2;FLT(bot,0x4c)=1.1f;FLT(bot,0x50)=0;
 bot_hit_trampoline(bot,ball,m);
 INT(bot,0xa4)=tactic;FLT(bot,0x4c)=chance;FLT(bot,0x50)=failure;
}
static void* text_component(void* page,int offset){
 void* saved=PTR(page,0x50);PTR(page,0x50)=PTR(page,offset);
 void* result=FN(0xef46a0,void*(*)(void*,void*))(page,0);
 PTR(page,0x50)=saved;return result;
}
static void set_text(void* text,void* value){if(text)FN(0xe84d60,void(*)(void*,void*,void*))(text,value,0);}
static void label(void* text,const char* value){if(text)set_text(text,FN(0x14b790,void*(*)(const char*))(value));}
static void* read_text(void* text){
 void* klass=PTR(text,0);
 return ((void*(*)(void*,void*))PTR(klass,0x5b0))(text,PTR(klass,0x5b8));
}
static void show_button(void* page,int offset,int show){
 void* button=PTR(page,offset);if(!button)return;
 void* go=FN(0x94b570,void*(*)(void*,void*))(button,0);
 if(go)FN(0x94f700,void(*)(void*,_Bool,void*))(go,show!=0,0);
}
static void layout(void* page){
 if(!page)return;
 int extras=solo_stage==3;
 show_button(page,0x40,1);show_button(page,0x48,solo_stage==0||extras);
 show_button(page,0x50,solo_stage==2||solo_stage==4||(solo_stage==0&&!online_selector));show_button(page,0x58,solo_stage==0);
 if(extras){
  label(text_component(page,0x40),"Bomb 4v4");label(text_component(page,0x48),"Bomb 2v2");
  label(PTR(page,0x38),online_selector?"Online - Extras":"Solo - Extras");
 }else if(solo_stage==0){
  label(text_component(page,0x40),"4v4");label(text_component(page,0x48),"2v2");
  label(text_component(page,0x58),"Extras");label(text_component(page,0x50),"Training");
  label(PTR(page,0x38),online_selector?"Online - Game mode":"Solo - Game mode");
 }else{
  label(text_component(page,0x40),"Beach");label(text_component(page,0x50),"Indoor");
  label(text_component(page,0x58),"Extras");
  label(PTR(page,0x38),solo_stage==2?"Solo 2v2":"Solo 4v4");
 }
}
static void choose(void* page,int stage){solo_stage=stage;layout(page);FN(0xee3400,void(*)(void*,void*))(page,0);}
static void* completed(void){return FN(0x402600,void*(*)(void*))(0);}
EXPORT void solo_awake_hook(void* o,void* m){
 solo_awake_trampoline(o,m);
 root_set(&page_root,o);root_set(&day_text_root,read_text(text_component(o,0x40)));
 root_set(&night_text_root,read_text(text_component(o,0x48)));
 solo_stage=0;layout(o);
}
EXPORT void* solo_entry_hook(void* o,void* m){
 training_reset_v29();stats_session_reset_v29();bots_reset_v29();refinement_close_v29();
 online_selector=0;online_bomb_v28=0;
 solo_stage=0;doubles_requested=0;layout(rooted(page_root));
 return solo_entry_trampoline(o,m);
}
EXPORT void* online_entry_hook(void* o,void* m){
 training_reset_v29();stats_session_reset_v29();bots_reset_v29();refinement_close_v29();
 root_set(&online_start_root,o);online_selector=1;solo_stage=0;online_bomb_v28=0;
 doubles_requested=0;layout(rooted(page_root));
 return solo_entry_trampoline(o,m);
}
static void* select_online(int format,void* m){
 online_format=format;online_version_ready=0;online_selector=0;
 return online_entry_trampoline(rooted(online_start_root),m);
}
EXPORT void main_menu_hook(void* o,void* argument,void* m){
 if(offline()||!FN(0x61efc0,_Bool(*)(void*))(0)){rewards_reset_v29();customization_reset_v28();}
 /* Entering another game from the main menu must not inherit doubles. Keep
  * the current match's speed if the user merely opens and closes the menu. */
 customization_close_v19();graphics_close_v24();landing_clear_v20();celebration_reset_v21();
 /* StartPage can also be opened over a live match. Reset the old online
  * epoch only after leaving its room; lobby entry handles same-room replay. */
 if(!offline()&&!FN(0x61efc0,_Bool(*)(void*))(0))online_session_reset_v26();
 doubles_requested=0;main_menu_trampoline(o,argument,m);show_button(o,0x30,0);
 graphics_start_v24();refinement_menu_v29();
}
EXPORT void* solo_day_hook(void* o,void* m){
 if(solo_stage==3){if(online_selector){online_bomb_v28=1;return select_online(4,m);}solo_stage=4;return solo_bomb_v28_trampoline(o,m);}
 if(online_selector){online_bomb_v28=0;return select_online(4,m);}
 if(solo_stage==0){choose(o,4);return completed();}
 return solo_day_trampoline(o,m);
}
EXPORT void* solo_night_hook(void* o,void* m){
 if(solo_stage==3){if(online_selector){online_bomb_v28=1;return select_online(2,m);}solo_stage=2;return solo_bomb_v28_trampoline(o,m);}
 if(online_selector){online_bomb_v28=0;return select_online(2,m);}
 if(solo_stage==0){choose(o,2);return completed();}
 return completed(); /* Night is retired; this button only selects 2v2 now. */
}
EXPORT void* solo_bomb_v28_hook(void* o,void* m){choose(o,3);return completed();}
EXPORT void* solo_back_hook(void* o,void* m){
 if(solo_stage==3){choose(o,0);return completed();}
 if(online_selector){online_selector=0;return solo_back_trampoline(o,m);}
 if(solo_stage){doubles_requested=0;choose(o,0);return completed();}
 doubles_requested=0;return solo_back_trampoline(o,m);
}
EXPORT void* solo_start_hook(void* o,void* env,_Bool bomb,void* m){
 doubles_requested=solo_stage==2;
 return solo_start_trampoline(o,env,bomb,m);
}

/* Keep two opposite lateral positions, including the serving position.
 * Their area.next links become a two-position cycle, so every serve remains
 * assigned to an actual member. Save original geometry for a later 4v4 game.
 */
typedef struct {void* area;void* next;V3 size,position,default_position;unsigned char back;} AreaSave;
typedef struct {unsigned root;int saved,modified,slots[2];AreaSave areas[4];} TeamSave;
static TeamSave team_saves[2];
static void* transform(void* o){return FN(0x94b620,void*(*)(void*,void*))(o,0);}
static V3 position(void* t){return FN(0xb74de0,GetVec)(t,0);}
static void position_set(void* t,V3 p){FN(0xb756b0,SetVec)(t,p,0);}
static void configure_team(void* team,int index,int enable){
 TeamSave* s=&team_saves[index];
 if(rooted(s->root)!=team){root_set(&s->root,team);s->saved=0;s->modified=0;}
 if(!team)return;
 if(!s->saved){
  void* list=PTR(team,0x18);if(!list||INT(list,0x18)!=4)return;
  void* array=PTR(list,0x10);if(!array)return;
  for(int i=0;i<4;i++){if(!PTR(array,0x20+i*8))return;}
  s->slots[0]=0;
  for(int i=0;i<4;i++){
   AreaSave* a=&s->areas[i];a->area=PTR(array,0x20+i*8);
   a->next=PTR(a->area,0x28);a->size=*(V3*)((char*)a->area+0x18);
   a->position=position(transform(a->area));
   a->default_position=position(PTR(a->area,0x30));a->back=BYTE(a->area,0x39);
   if(BYTE(a->area,0x38))s->slots[0]=i;
  }
  s->slots[1]=(s->slots[0]+2)%4;s->saved=1;
 }
 if(s->modified){
  for(int i=0;i<4;i++){
   AreaSave* a=&s->areas[i];managed_field(a->area,0x28,a->next);
   *(V3*)((char*)a->area+0x18)=a->size;BYTE(a->area,0x39)=a->back;
   position_set(transform(a->area),a->position);position_set(PTR(a->area,0x30),a->default_position);
  }
  s->modified=0;
 }
 if(!enable)return;
 if(enable==4){
  float sign=index?1.0f:-1.0f;
  void* rules=rooted(rules_root);int bomb=rules&&BYTE(rules,0x68);
  for(int i=0;i<4;i++){
   AreaSave* a=&s->areas[i];int role=(i-s->slots[0]+4)%4;
   V3 pos=a->position,def=a->default_position,sz=a->size;
   pos.x=role==1?-3.0f:role==3?3.0f:0.0f;
   pos.z=sign*(role==0?7.0f:role==2?1.5f:4.0f);
   def.x=pos.x;def.z=pos.z;
   sz.x=role==0?9.0f:3.0f;sz.z=role==0?4.0f:role==2?3.0f:8.0f;
   if(bomb){pos.x*=.4f;pos.z*=.5f;def.x=pos.x;def.z=pos.z;sz.x*=.44444445f;sz.z*=.5f;}
   *(V3*)((char*)a->area+0x18)=sz;BYTE(a->area,0x39)=role==0;
   position_set(transform(a->area),pos);position_set(PTR(a->area,0x30),def);
  }
  s->modified=1;return;
 }
 float z=0;for(int i=0;i<4;i++)z+=s->areas[i].position.z*0.25f;
 for(int i=0;i<2;i++){
  AreaSave* a=&s->areas[s->slots[i]];AreaSave* other=&s->areas[s->slots[1-i]];
  managed_field(a->area,0x28,other->area);
  V3 sz=a->size;sz.z*=2.0f;*(V3*)((char*)a->area+0x18)=sz;
  V3 pos=a->position;pos.z=z;position_set(transform(a->area),pos);
  V3 def=a->default_position;def.z=z;position_set(PTR(a->area,0x30),def);
  BYTE(a->area,0x39)=0;
 }
 s->modified=1;
}
static int mapped_slot(void* team,int slot){
 if(!doubles_enabled)return slot;
 for(int i=0;i<2;i++)if(rooted(team_saves[i].root)==team&&team_saves[i].modified)return team_saves[i].slots[slot&1];
 return slot;
}
static void prepare_match(void* o){
 bots_reset_v29();
 landing_clear_v20();
 serve_feedback_arm_v21();celebration_reset_v21();
 FLT(o,0x40)=.9f;
 hand_serve_reset();root_set(&local_player_root,0);
 root_set(&rules_root,o);reception_pending=0;reception_context=0;
 serve_flight_team=-1;serve_fault=0;deferred_serve_point=-1;player_airborne=0;root_set(&jumping_player_root,0);accepted_position_valid_v28=0;accepted_block_v28=0;
 doubles_enabled=(doubles_requested&&offline()||online_mode());
 quartet_enabled=!doubles_enabled&&(offline()||network_physics());
 doubles_spawned=0;doubles_team_counts[0]=doubles_team_counts[1]=0;
 void* teams=PTR(o,0x60);
 if(teams&&*(U64*)((char*)teams+0x18)==2){
  for(int i=0;i<2;i++)configure_team(PTR(teams,0x20+i*8),i,doubles_enabled?2:quartet_enabled?4:0);
  if(doubles_enabled&&(!team_saves[0].modified||!team_saves[1].modified)){
   doubles_enabled=0;
   for(int i=0;i<2;i++)configure_team(PTR(teams,0x20+i*8),i,0);
  }
 }else {doubles_enabled=0;quartet_enabled=0;}
}
EXPORT void game_go_hook(void* o,void* m){
 bots_roster_reset_v20(o);
 prepare_match(o);
 if(training_requested_v29())training_begin_v29(o);
 stats_prepare_v29(o);
 game_go_trampoline(o,m);
 void* teams=PTR(o,0x60);
 if(teams)for(int i=0;i<2;i++){
  void* team=PTR(teams,0x20+i*8);void* members=team?PTR(team,0x28):0;
  doubles_team_counts[i]=members?INT(members,0x18):0;
 }
}
EXPORT void spawn_bot_hook(void* o,void* prefab,int team,int slot,float yaw,void* m){
 if(training_active_v29())return;
 if(doubles_enabled&&(slot<0||slot>=2||(!online_mode()&&team==0&&slot!=0)))return;
 if(doubles_enabled){
  void* teams=PTR(o,0x60);
  if(teams&&team>=0&&team<2)slot=mapped_slot(PTR(teams,0x20+team*8),slot);
 }
 bots_spawn_begin_v20(o,team,slot);
 spawn_bot_trampoline(o,prefab,team,slot,yaw,m);
 bots_spawn_end_v20();
 if(doubles_enabled)doubles_spawned++;
}
EXPORT void add_player_hook(void* team,void* player,int slot,void* m){
 if(offline())root_set(&local_player_root,player);
 add_player_trampoline(team,player,mapped_slot(team,slot),m);
}
/* Only the two gameplay callers are redirected; the stored preference and UI
 * continue to expose the user's original front-row and movement settings. */
EXPORT _Bool front_row_hook(void* m){return doubles_enabled||quartet_enabled?0:FN(0xef32b0,_Bool(*)(void*))(m);}
EXPORT float player_speed_hook(void* m){
 float speed=FN(0xef33b0,float(*)(void*))(m);
 return doubles_enabled||quartet_enabled||lobby_active()?speed*doubles_player_speed:speed;
}
EXPORT void bot_body_hook(void* bot,void* m){
 float speed=FLT(bot,0x3c);if(doubles_enabled||quartet_enabled)FLT(bot,0x3c)=speed*(bot_has_human_mate(bot)?doubles_ally_speed:doubles_speed);
 void* rules=rooted(rules_root);void* area=PTR(bot,0x20);
 if(rules&&BYTE(rules,0x78)&&BYTE(rules,0x79)&&area&&BYTE(area,0x38)&&INT(bot,0x28)==INT(rules,0x7c))FLT(bot,0x3c)=0;
 bots_before_body_v29(bot);bot_body_trampoline(bot,m);FLT(bot,0x3c)=speed;
 celebration_bot_v21(bot);
}
/* Only the bot-serve placement reads through this call-site hook. Raising
 * the returned position leaves the court transform and human serve intact. */
EXPORT V3 bot_serve_position_hook(void* serve_transform,void* m){
 V3 fallback=FN(0xb74de0,GetVec)(serve_transform,m);
 void* rules=rooted(rules_root);if(!rules)return fallback;
 int team=INT(rules,0x7c);if(team<0||team>1)return fallback;
 void* sides=PTR(rules,0x60);void* side=sides?PTR(sides,0x20+8*team):0;
 void* list=side?PTR(side,0x30):0;void* array=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
 if(!array||n<1||n>4)return fallback;
 for(int i=0;i<n;i++){
  void* bot=PTR(array,0x20+8*i);void* area=bot?PTR(bot,0x20):0;
  if(area&&BYTE(area,0x38)){V3 p=position(transform(bot));p.y+=2.8f;return p;}
 }
 return fallback;
}
EXPORT void* pass_target_hook(void* bot,void* m){
 void* target=pass_target_trampoline(bot,m);
 if(quartet_enabled)return quartet_pass(bot,target,m);
 if(ally_setup(bot)&&(!target||!BYTE(target,0x24))){
  /* In rare cases the original chooser yields no human target. Reuse a
   * normally allocated target and aim a high set at the actual teammate. */
  void* rules=rooted(rules_root);void* teams=PTR(rules,0x60);
  void* team=teams?PTR(teams,0x20+INT(bot,0x28)*8):0;void* players=team?PTR(team,0x38):0;
  if(players&&INT(players,0x18)>0){
   void* array=PTR(players,0x10);void* player=array?PTR(array,0x20):0;
   if(player){
    if(!target)target=FN(0x270680,void*(*)(void*,void*))(bot,m);
    if(target){V3 point=position(transform(player));point.y+=1.2f;
     *(V3*)((char*)target+0x10)=point;FLT(target,0x20)=FLT(bot,0x44);BYTE(target,0x24)=1;}
   }
  }
 }
 if(doubles_enabled&&target&&BYTE(target,0x24)){
  float apex=FLT(target,0x20);if(apex<=0)apex=FLT(bot,0x44);
  FLT(target,0x20)=apex+doubles_set_extra;doubles_high_sets++;
 }else if(doubles_enabled&&target){
  /* The raised net also affects the opposing bots' normal sets. */
  float apex=FLT(target,0x20);if(apex<=0)apex=FLT(bot,0x44);
  FLT(target,0x20)=apex+.4f;
 }
 return target;
}
#include "spawn_input_v24.c"
#include "formation_serve.c"
#include "online_2v2.c"
#include "comfort_v14.c"
#include "celebration_v15.c"
#include "score_outline_v20.c"
#include "avatar_style_v21.c"
#include "identity_v16.c"
#include "customization_v19.c"
#include "graphics_v24.c"
#include "hand_visuals_v21.c"
#include "sleeves_v24.c"
#include "customization_v28.c"
#include "input_v19.c"
#include "bots_v20.c"
#include "landing_v20.c"
#include "serve_feedback_v21.c"
#include "lobby_v18.c"
#include "map_v19.c"
#include "gameplay_v19.c"
#include "ball_style_v26.c"
#include "elbow_v27.c"
#include "hit_feedback_v29.c"
#include "settings_audio_v28.c"
#include "training_v29.c"
#include "bots_refine_v29.c"
#include "rewards_v29.c"
#include "stats_v29.c"
#include "refinement_v29.c"
#ifdef MODE_PROBE
/* Built only in the disposable validation binary. Commands are consumed on
 * Unity's main thread, never invoked by an external thread. */
TRAMP(void,probe_start,(void* o,void* m))
TRAMP(void,probe_solo,(void* o,void* m))
EXPORT int probe_command=0,probe_page_ready=0,probe_ticks=0;
static void probe(void* start){
 probe_ticks++;
 void* page=rooted(page_root);probe_page_ready=page!=0;
 if(probe_command==1&&start){probe_command=0;solo_entry_hook(start,0);}
 if(probe_command==2&&page){probe_command=0;choose(page,2);solo_day_trampoline(page,0);}
 if(probe_command==3&&page){probe_command=0;choose(page,2);FN(0xef4320,void*(*)(void*,void*))(page,0);}
}
EXPORT void probe_start_hook(void* o,void* m){probe_start_trampoline(o,m);probe(o);}
EXPORT void probe_solo_hook(void* o,void* m){probe_solo_trampoline(o,m);probe(0);}
#endif
