/* All clients in this version namespace run two slots per team. The
 * original Photon RPCs carry team/slot assignments; no new RPC indices. */
TRAMP(void,network_version,(void* manager,void* m))
TRAMP(void,clear_teams,(void* rules,void* m))
TRAMP(void,online_setup,(void* rules,void* m))
TRAMP(void,choose_team,(void* player,int team,void* m))
TRAMP(void,online_awake,(void* page,void* m))
TRAMP(void,client_motion,(void* ball,V3 pos,V3 velocity,_Bool hit,int touch,int team,int context,void* m))
TRAMP(void,client_end,(void* rules,int team,V3 pos,void* m))
static int net_first_touch=0,net_serve_team=-1;
static int net_touch_team=-1,net_touch_count=0,net_rally_active=0;
static int network_physics(void){return online_version_ready&&!offline();}
static void* network_player_statics(void){
 /* NetworkPlayer class metadata is initialized by the original lobby. */
 void* klass=*(void**)(base()+0x1542650);
 return klass?PTR(klass,0xb8):0;
}
static void* online_local_player(void){void* s=network_player_statics();return s?PTR(s,0):0;}
static void* online_players(void){void* s=network_player_statics();return s?PTR(s,8):0;}
static int player_is_airborne(void* player){
 if(player_airborne&&rooted(jumping_player_root)==player)return 1;
 if(!network_physics()||!player||player==online_local_player())return 0;
 void* body=PTR(player,0x80);if(!body)return 0;
 /* CapturePlayerPose serializes the InputSystem transform position.
  * The game's jump raises that transform; room-scale head height does
  * not affect it. Compare against the avatar's ground placement. */
 float y=FLT(body,0xb8),floor=position(transform(player)).y;
 return __builtin_isfinite(y)&&y-floor>0.08f;
}
static int bot_has_human_mate(void* bot){
 if(!bot)return 0;if(!network_physics())return INT(bot,0x28)==0;
 void* rules=rooted(rules_root);int team=INT(bot,0x28);if(!rules||team<0||team>1)return 0;
 void* teams=PTR(rules,0x60);void* side=teams?PTR(teams,0x20+team*8):0;
 void* players=side?PTR(side,0x38):0;return players&&INT(players,0x18)>0;
}
static int online_reception(void* player){
 return player&&player==online_local_player()&&net_serve_team==1-INT(player,0x28);
}
static void set_mod_version(void* app){
 online_version_ready=0;
 if(app){
  void* version=FN(0x14b790,void*(*)(const char*))(online_format==2?"CaioBa-2v2-v15":"CaioBa-4v4-v15");
  managed_field(app,0x28,version);online_version_ready=1;
 }
}
EXPORT void network_version_hook(void* manager,void* m){
 network_version_trampoline(manager,m);
 void* settings=FN(0x61fcd0,void*(*)(void*))(0);
 set_mod_version(settings?PTR(settings,0x18):0);
}
/* ConnectToMasterServer inlines SetPhotonAppVersion, overwriting the
 * settings again. Cover BOTH final connect call sites, after that write
 * and after the fixed-region copy, not only the standalone method. */
EXPORT _Bool connect_settings_hook(void* app,_Bool start_offline,void* m){
 set_mod_version(app);
 return FN(0x60acf0,_Bool(*)(void*,_Bool,void*))(app,start_offline,m);
}
EXPORT _Bool connect_default_hook(void* m){
 void* settings=FN(0x61fcd0,void*(*)(void*))(0);
 set_mod_version(settings?PTR(settings,0x18):0);
 return FN(0x60abf0,_Bool(*)(void*))(m);
}
EXPORT void clear_teams_hook(void* rules,void* m){
 clear_teams_trampoline(rules,m);
 if(online_version_ready&&!offline()){prepare_match(rules);net_first_touch=0;net_serve_team=-1;net_touch_team=-1;net_touch_count=0;net_rally_active=0;}
}
static int team_population(int team,void* exclude){
 void* list=online_players();void* items=list?PTR(list,0x10):0;
 int n=list?INT(list,0x18):0,count=0;if(!items||n<0||n>4)return 0;
 for(int i=0;i<n;i++){void* p=PTR(items,0x20+i*8);if(p&&p!=exclude&&INT(p,0x28)==team)count++;}
 return count;
}
EXPORT void choose_team_hook(void* player,int team,void* m){
 if(online_mode()&&(team<0||team>1||team_population(team,player)>=2))return;
 choose_team_trampoline(player,team,m);
}
EXPORT void online_setup_hook(void* rules,void* m){
 if(online_mode()){
  /* The host resolves simultaneous lobby choices before broadcasting
   * the original authoritative team assignments. Preserve valid choices. */
  void* list=online_players();void* items=list?PTR(list,0x10):0;
  int n=list?INT(list,0x18):0,counts[2]={0,0};void* overflow[4];int extra=0;
  if(!items||n<1||n>4)return;
  for(int i=0;i<n;i++){
   void* p=PTR(items,0x20+i*8);if(!p)continue;int team=INT(p,0x28);
   if(team>=0&&team<2&&counts[team]<2)counts[team]++;else overflow[extra++]=p;
  }
  for(int i=0;i<extra;i++){
   int team=counts[0]<2?0:1;counts[team]++;INT(overflow[i],0x28)=team;
   choose_team_trampoline(overflow[i],team,0);
  }
 }
 online_setup_trampoline(rules,m);
}
EXPORT void online_awake_hook(void* page,void* m){
 online_awake_trampoline(page,m);
 label(text_component(page,0x40),"Criar sala");
 label(text_component(page,0x48),"Entrar na sala");
}
/* Client_NewRally originally only tail-calls RefreshUI. Replace its exact
 * seven bytes instead of relocating that short relative jump. */
EXPORT void net_new_rally_hook(void* rules,int team,void* m){
 if(network_physics()){net_first_touch=1;net_serve_team=-1;net_touch_team=-1;net_touch_count=0;net_rally_active=1;}
 FN(0x253e30,void(*)(void*,void*))(rules,0);
}
EXPORT void client_motion_hook(void* ball,V3 pos,V3 velocity,_Bool hit,int touch,int team,int context,void* m){
 int encoded=network_physics()&&hit&&((unsigned)context&0xf8000000u)==0x50000000u;
 V3 spin=encoded?decode_spin(context):(V3){0,0,0};
 if(encoded)context&=7;
 client_motion_trampoline(ball,pos,velocity,hit,touch,team,context,m);
 if(network_physics()){
  if(encoded)activate_spin(ball,spin);
  else {if(spinning_ball==ball)spinning_ball=0;setspin(ball,(V3){0,0,0});}
 }
 if(network_physics()&&hit&&team>=0&&team<2){
  net_touch_count=net_touch_team==team?net_touch_count+1:1;net_touch_team=team;
  net_serve_team=net_first_touch?team:-1;net_first_touch=0;
 }
}
EXPORT void client_end_hook(void* rules,int team,V3 pos,void* m){
 int reason=0;if((team&0xff00)==0x4300){reason=(team>>1)&15;team&=1;}
 if(network_physics()){net_first_touch=0;net_serve_team=-1;net_touch_team=-1;net_touch_count=0;net_rally_active=0;}
 client_end_trampoline(rules,team,pos,m);
 if(reason)point_message(rules,team,reason);
}
