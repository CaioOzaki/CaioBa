/* Cloudcourt VR interface, balanced court limits and explicit online appearances. */
TRAMP(void,clamp_player,(void* player,void* m))
TRAMP(void,button_press,(void* button,void* m))
TRAMP(void,client_choose,(void* player,int value,void* m))
TRAMP(void,ui_submit,(_Bool value,void* m))
TRAMP(void,intro_page,(void* page,void* arg,void* m))
TRAMP(void,tmp_awake,(void* text,void* m))
TRAMP(void,tmp_ui_awake,(void* text,void* m))
TRAMP(void,ui_text_enable,(void* text,void* m))
TRAMP(void,refresh_score,(void* rules,void* m))
TRAMP(void,in_room_ui,(void* page,void* m))
TRAMP(void,in_game_active,(void* page,void* arg,void* m))
static int text_equals(void* s,const char* word){
 if(!s)return 0;int n=INT(s,0x10),i=0;
 for(;word[i];i++)if(i>=n||*(unsigned short*)((char*)s+0x14+i*2)!=(unsigned char)word[i])return 0;
 return i==n;
}
static int named(void* component,const char* name){return text_equals(FN(0xa0bdd0,void*(*)(void*,void*))(gameobject(component),0),name);}
/* Movement and teleport use distinct native paths. Enforce the same world
 * torso boundary at both; online eligibility does not depend on host Go(). */
static V3 clamp_player_position_v26(void* player,V3 desired){
 if(!player||!finitev(desired)||lobby_active())return desired;
 if(network_physics()){
  /* Photon/local avatar objects can survive room leave with an old area. */
  if(!FN(0x61efc0,_Bool(*)(void*))(0)||player!=online_local_player()||!PTR(player,0x20))return desired;
 }else if(!doubles_enabled&&!quartet_enabled)return desired;
 int team=INT(player,0x28);if(team<0||team>1)return desired;
 void* t=transform(player);if(!t)return desired;
 V3 current=position(t);void* body=PTR(player,0x80);void* torso=body?PTR(body,0x38):0;
 V3 center=torso?position(torso):current;if(!finitev(current)||!finitev(center))return desired;
 float z=desired.z+center.z-current.z;
 if(team==0&&z>-.18f)desired.z+=-.18f-z;
 if(team==1&&z<.18f)desired.z+=.18f-z;
 return desired;
}
static void clamp_local_player_v26(void* body){
 void* player=network_physics()?online_local_player():rooted(local_player_root);
 if(!body||!player||PTR(player,0x80)!=body)return;
 void* t=transform(player);if(!t)return;
 V3 p=position(t),q=clamp_player_position_v26(player,p);
 if(q.z!=p.z)position_set(t,q);
}
EXPORT void clamp_player_hook(void* player,void* m){
 if(lobby_active())return;
 clamp_player_trampoline(player,m);
 if(!player)return;void* t=transform(player);if(!t)return;
 V3 p=position(t),q=clamp_player_position_v26(player,p);
 if(q.z!=p.z)position_set(t,q);
}

typedef struct {unsigned player;int skin;} SkinChoice;
static SkinChoice choices[8];static int preferred_skin=-1,preferred_map,preferences_loaded;
static int chosen_skin(void* player){for(int i=0;i<8;i++)if(rooted(choices[i].player)==player)return choices[i].skin;return -1;}
static void remember_skin(void* player,int skin){
 if(skin<0||skin>=81)return;
 for(int i=0;i<8;i++)if(rooted(choices[i].player)==player||!alive(rooted(choices[i].player))){root_set(&choices[i].player,player);choices[i].skin=skin;return;}
}
static int list_index(void* list,void* value){void* a=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;if(!a||n<0||n>8)return -1;for(int i=0;i<n;i++)if(PTR(a,0x20+8*i)==value)return i;return -1;}
static int list_replace(void* list,void* old,void* value){int i=list_index(list,old);if(i<0)return 0;managed_field(PTR(list,0x10),0x20+8*i,value);INT(list,0x1c)++;return 1;}
static void list_remove(void* list,void* value){
 int i=list_index(list,value);if(i<0)return;void* a=PTR(list,0x10);int n=INT(list,0x18);
 for(int j=i;j<n-1;j++)managed_field(a,0x20+8*j,PTR(a,0x28+8*j));managed_field(a,0x18+8*n,0);INT(list,0x18)=n-1;INT(list,0x1c)++;
}
static int list_add(void* list,void* value){
 if(!list||list_index(list,value)>=0)return 0;void* a=PTR(list,0x10);int n=INT(list,0x18);if(!a||n<0||n>=8)return 0;
 if(*(U64*)((char*)a+0x18)<(U64)(n+1)){
  void* fresh=FN(0x14a510,void*(*)(void*,U64))(PTR(a,0),8);if(!fresh)return 0;
  for(int j=0;j<n;j++)managed_field(fresh,0x20+j*8,PTR(a,0x20+j*8));managed_field(list,0x10,fresh);a=fresh;
 }
 managed_field(a,0x20+n*8,value);INT(list,0x18)=n+1;INT(list,0x1c)++;return 1;
}
static int switch_team(void* player,int target){
 void* rules=rooted(rules_root);int old=INT(player,0x28);if(!rules||old<0||old>1||target==old)return 0;
 void* ts=PTR(rules,0x60);void* from=ts?PTR(ts,0x20+old*8):0;void* to=ts?PTR(ts,0x20+target*8):0;if(!from||!to)return 0;
 void* bots=PTR(to,0x30);void* a=bots?PTR(bots,0x10):0;if(!a||INT(bots,0x18)<1)return 0;
 void* bot=PTR(a,0x20);if(!bot||list_index(PTR(from,0x28),player)<0||list_index(PTR(to,0x28),bot)<0)return 0;
 void* old_area=PTR(player,0x20);void* new_area=PTR(bot,0x20);V3 p=position(transform(player)),q=position(transform(bot));
 /* Allocate list capacity before mutating membership. */
 if(!list_add(PTR(from,0x30),bot))return 0;
 if(!list_add(PTR(to,0x38),player)){list_remove(PTR(from,0x30),bot);return 0;}
 list_remove(PTR(to,0x30),bot);list_remove(PTR(from,0x38),player);
 list_replace(PTR(from,0x28),player,bot);list_replace(PTR(to,0x28),bot,player);
 INT(player,0x28)=target;INT(bot,0x28)=old;managed_field(player,0x20,new_area);managed_field(bot,0x20,old_area);
 if(player==online_local_player()){
  q.y=p.y;position_set(transform(player),q);
  FN(0xb75750,void(*)(void*,Q4,void*))(transform(player),(Q4){0,target?1.f:0,0,target?0:1.f},0);
 }
 position_set(transform(bot),p);BYTE(bot,0x80)=0;
 for(int i=0;i<2;i++)root_set(&attack_receiver[i],0);
 return 1;
}
typedef struct {unsigned player;int team;} PendingTeam;
static PendingTeam pending_teams[8];
static void pending_teams_reset_v26(void){
 for(int i=0;i<8;i++){root_set(&pending_teams[i].player,0);pending_teams[i].team=-1;}
}
static void finish_team_changes(void){
 for(int i=0;i<8;i++){void* p=rooted(pending_teams[i].player);if(alive(p))switch_team(p,pending_teams[i].team);root_set(&pending_teams[i].player,0);}
}
static int has_team_membership(void* player){
 void* rules=rooted(rules_root);if(!alive(rules))return 0;
 void* teams=PTR(rules,0x60);if(!teams)return 0;
 for(int i=0;i<2;i++){void* team=PTR(teams,0x20+i*8);if(team&&list_index(PTR(team,0x28),player)>=0)return 1;}
 return 0;
}
EXPORT void client_choose_hook(void* player,int value,void* m){
 if(!player)return;
 if(appearance_receive_v28(player,value))return;
 if(value==0x5c220000){serve_feedback_remote_v21(player);return;}
 int modern=((unsigned)value&0xfffffc00u)==0x5c190000u;
 int team=0,skin=0,change=0,tone=0,v21=appearance_decode_v21(value,&team,&skin,&change,&tone);
 if(v21<0)return;
 if(v21||modern||(value&0xff00)==0x5600){
  int face=v21?skin%9:modern?(value>>1)&15:(value>>2)&3,outfit=v21?skin/9:modern?(value>>5)&15:2;
  if(face>=9||outfit>=9)return;
  if(!v21){team=value&1;skin=face+9*outfit;change=modern?(value&0x200):(value&0x20);}
  if(change&&has_team_membership(player)){
   if(net_rally_active){for(int i=0;i<8;i++)if(rooted(pending_teams[i].player)==player||!alive(rooted(pending_teams[i].player))){root_set(&pending_teams[i].player,player);pending_teams[i].team=team;break;}}
   else switch_team(player,team);
  }
  /* A delayed appearance refresh can carry the team from before a swap.
   * Never detach the team field from the authoritative membership lists. */
  else if(!has_team_membership(player))INT(player,0x28)=team;
  remember_skin(player,skin);
  if(v21){remember_hand_tone_v21(player,tone);remember_hand_pose_v21(player,appearance_pose_v21(value));}
  return;
 }
 if(value==0||value==1)INT(player,0x28)=value;
}
static void send_mod_choice(void* player,int value){
 /* Original InvokeRpc_ChooseTeam sends AllBufferedViaServer (6). Appearance
  * refreshes are frequent and must not accumulate or replay old team swaps.
  * Initialize the same verified metadata and use AllViaServer (5), preserving
  * the reliable server ordering and the existing RPC name/argument format. */
 static int ready;
 if(!ready){FN(0x1c21b0,void(*)(unsigned))(INT((void*)base(),0x1294f48));ready=1;}
 void* view=FN(0x6054c0,void*(*)(void*,void*))(player,0);if(!view)return;
 void* array_class=PTR((void*)base(),0x15260b8),*int_class=PTR((void*)base(),0x15269d0);
 if(!array_class||!int_class)return;
 void* args=FN(0x1c1f90,void*(*)(void*,int))(array_class,1);if(!args)return;
 void* boxed=FN(0x14ba70,void*(*)(void*,void*))(int_class,&value);if(!boxed)return;
 managed_field(args,0x20,boxed);
 FN(0xe6bb50,void(*)(void*,void*,int,void*,void*))(view,str("Client_ChooseTeam"),5,args,0);
}
static void select_appearance(int skin,int change){
 ensure_preferences_v19();
 if(skin>=0&&skin<9){preferred_skin=skin+9*(preferred_skin/9);FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Face"),skin,0);}
 void* player=online_local_player();if(!player||!network_physics())return;
 int team=INT(player,0x28);if(team<0||team>1)return;
 if(change)team=1-team;
 send_mod_choice(player,appearance_pack_pose_v21(team,preferred_skin,change,preferred_hand_tone_v21,local_hand_pose_v21()));
 send_mod_choice(player,appearance_pack_v28());
}
EXPORT void button_press_hook(void* button,void* m){
 if(!ui_button_valid_v19(button))return;
 ui_click_v19(button);
 if(settings_button_v28(button))return;
 if(graphics_button_v24(button))return;
 if(customization_button_v19(button))return;
 if(named(button,"CC_LobbyClose")){lobby_selector_hide_v21();return;}
 if(named(button,"CC_LobbyChangeTeam")){lobby_selector_show_v21();return;}
 if(named(button,"PuloTeams")){if(lobby_active())lobby_selector_show_v21();else select_appearance(-1,1);return;}
 const char* names[4]={"PuloSkin0","PuloSkin1","PuloSkin2","PuloSkin3"};
 for(int i=0;i<4;i++)if(named(button,names[i])){select_appearance(i,0);return;}
 button_press_trampoline(button,m);
}
EXPORT void intro_page_hook(void* page,void* arg,void* m){FN(0xee37b0,void(*)(void*,void*,void*,void*))(page,str("Start"),0,0);}
EXPORT void ui_submit_hook(_Bool value,void* m){
 ui_submit_trampoline(ui_input_v19(value)!=0,m);
}
static unsigned cartoon_font,cartoon_tmp;static int font_busy;
static void* bubble_font(void){
 if(alive(rooted(cartoon_font)))return rooted(cartoon_font);
 void* klass=*(void**)(base()+0x1517ef0);if(!klass)return 0;
 void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
 void* all=FN(0xb6b720,void*(*)(void*,void*))(type,0);int n=all?(int)*(U64*)((char*)all+0x18):0;
 for(int i=0;i<n&&i<64;i++){void* f=PTR(all,0x20+8*i);if(text_equals(FN(0xa0bdd0,void*(*)(void*,void*))(f,0),"Cloudcourt Bubble")){root_set(&cartoon_font,f);return f;}}
 return 0;
}
static void style_tmp(void* text){
 if(font_busy)return;font_busy=1;void* font=bubble_font();
 if(font&&!alive(rooted(cartoon_tmp)))root_set(&cartoon_tmp,FN(0x201290,void*(*)(void*,void*))(font,0));
 if(alive(rooted(cartoon_tmp)))FN(0x23fb00,void(*)(void*,void*,void*))(text,rooted(cartoon_tmp),0);
 font_busy=0;
 score_outline_tmp_v20(text);
}
EXPORT void tmp_awake_hook(void* text,void* m){tmp_awake_trampoline(text,m);style_tmp(text);}
EXPORT void tmp_ui_awake_hook(void* text,void* m){tmp_ui_awake_trampoline(text,m);style_tmp(text);}
EXPORT void ui_text_enable_hook(void* text,void* m){ui_text_enable_trampoline(text,m);void* f=bubble_font();if(f)FN(0xe84a40,void(*)(void*,void*,void*))(text,f,0);score_outline_text_v20(text);}
static unsigned wall_scores[2];
static void append_string(char* out,int* n,const char* s){for(int i=0;s[i]&&*n<230;i++)out[(*n)++]=s[i];}
static void append_number(char* out,int* n,int value){if(value<0)value=0;if(value>999)value=999;if(value>=100)out[(*n)++]='0'+value/100;if(value>=10)out[(*n)++]='0'+(value/10)%10;out[(*n)++]='0'+value%10;}
EXPORT void refresh_score_hook(void* rules,void* m){
 refresh_score_trampoline(rules,m);void* scores=rules?PTR(rules,0xa8):0;if(!scores)return;
 char message[240];int n=0;append_string(message,&n,"<color=#75CFFF>");append_number(message,&n,INT(scores,0x20));append_string(message,&n,"</color> : <color=#FF7278>");append_number(message,&n,INT(scores,0x24));append_string(message,&n,"</color>");message[n]=0;
 for(int i=0;i<2;i++){
  if(!alive(rooted(wall_scores[i]))){
   void* go=FN(0x94f3d0,void*(*)(void*,void*))(str(i?"CloudBoard1/CanvasGroup/Score":"CloudBoard0/CanvasGroup/Score"),0);
   if(go)root_set(&wall_scores[i],FN(0x94f410,void*(*)(void*,void*,void*))(go,str("Text"),0));
  }
  void* text=rooted(wall_scores[i]);if(alive(text))FN(0xe84d60,void(*)(void*,void*,void*))(text,str(message),0);
 }
 void* score=PTR(rules,0x30);if(score)FN(0x2405f0,void(*)(void*,void*,void*))(score,str(message),0);
}
EXPORT void in_room_ui_hook(void* page,void* m){
 in_room_ui_trampoline(page,m);label(text_component(page,0x38),"BLUE TEAM");label(text_component(page,0x40),"RED TEAM");
}
EXPORT void in_game_active_hook(void* page,void* arg,void* m){
 customization_close_v19();
 graphics_close_v24();
 in_game_active_trampoline(page,arg,m);
 const char* names[5]={"PuloTeams","PuloSkin0","PuloSkin1","PuloSkin2","PuloSkin3"};
 for(int i=0;i<5;i++){void* t=find_child(transform(page),names[i]);if(t)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),i==0&&network_physics(),0);}
}
static float skin_refresh;
static void cloudcourt_avatar_tick(void* body){
 if(!network_physics()||PTR(body,0x168)!=online_local_player())return;
 skin_refresh-=FN(0xb72b10,float(*)(void*))(0);if(skin_refresh>0)return;skin_refresh=3;
 ensure_preferences_v19();select_appearance(-1,0);
}
