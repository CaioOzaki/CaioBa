/* Session-only end-match statistics. Include after training_v29.c.
 * Reads accepted motion/decoded point events; never changes game decisions.
 * No PlayerPrefs/file writes. Last completed summary survives menu/session reset. */
EXPORT void rewards_progress_v29(int kind,int amount);
enum {ST_ACE_V29,ST_ATTACK_V29,ST_RECEIVE_V29,ST_ERROR_V29,ST_CONTACT_V29};
typedef struct {
 int team[2][5],you[5],points,contacts,valid,complete;
 float longest_seconds;int longest_contacts;
} MatchStatsV29;
static MatchStatsV29 stats_current_v29,stats_last_v29;
static unsigned stats_rules_root_v29,stats_local_root_v29,stats_ball_root_v29;
static int stats_active_v29,stats_notice_v29,stats_local_id_v29=-1,stats_local_team_v29=-1;
static int stats_rally_open_v29,stats_rally_contacts_v29,stats_last_id_v29=-1,stats_last_team_v29=-1;
static int stats_serve_team_v29=-1,stats_last_attack_v29,stats_last_local_v29;
static int stats_set_id_v29=-1,stats_set_team_v29=-1,stats_set_local_v29;
static float stats_rally_start_v29,stats_event_time_v29;
static V3 stats_event_p_v29,stats_event_v_v29;
static int stats_event_valid_v29,stats_event_id_v29,stats_event_team_v29;
static float stats_now_v29(void){
 float n=FN(0xb72b40,float(*)(void*))(0);return __builtin_isfinite(n)&&n>=0?n:0;
}
static void stats_rally_reset_v29(void){
 stats_rally_open_v29=stats_rally_contacts_v29=stats_last_attack_v29=stats_last_local_v29=0;
 stats_last_id_v29=stats_last_team_v29=stats_serve_team_v29=-1;
 stats_set_id_v29=stats_set_team_v29=-1;stats_set_local_v29=0;stats_event_valid_v29=0;
}
static int stats_sets_v29(void* rules,int team){
 void* a=rules?PTR(rules,0xb0):0;
 if(!a||*(U64*)((char*)a+0x18)!=2)return 0;
 int n=INT(a,0x20+team*4);return n>=0&&n<=2?n:0;
}
static void stats_identity_v29(void){
 void* p=local_avatar_player();if(!alive(p))return;
 if(rooted(stats_local_root_v29)!=p){root_set(&stats_local_root_v29,p);stats_local_id_v29=FN(0x30cb70,int(*)(void*,void*))(p,0);}
 int t=INT(p,0x28);stats_local_team_v29=t>=0&&t<2?t:-1;
}
static int stats_is_local_v29(int id,int team){return id>=0&&id==stats_local_id_v29&&team==stats_local_team_v29;}
static void stats_add_v29(int team,int metric,int local){
 if(team<0||team>1)return;
 if(stats_current_v29.team[team][metric]<999999)stats_current_v29.team[team][metric]++;
 if(local&&stats_current_v29.you[metric]<999999)stats_current_v29.you[metric]++;
}
EXPORT void stats_prepare_v29(void* rules){
 stats_current_v29=(MatchStatsV29){0};stats_active_v29=0;
 root_set(&stats_rules_root_v29,0);root_set(&stats_local_root_v29,0);root_set(&stats_ball_root_v29,0);
 stats_local_id_v29=stats_local_team_v29=-1;stats_rally_reset_v29();
 if(!alive(rules)||training_active_v29()||training_requested_v29())return;
 root_set(&stats_rules_root_v29,rules);stats_active_v29=1;
 stats_identity_v29();
}
EXPORT void stats_tick_v29(void){
 if(!stats_active_v29||training_active_v29()||training_requested_v29())return;
 void* rules=rooted(stats_rules_root_v29);if(!alive(rules))return;
 if(!stats_current_v29.complete&&stats_current_v29.valid&&(stats_sets_v29(rules,0)>=2||stats_sets_v29(rules,1)>=2)){
  stats_current_v29.complete=1;stats_last_v29=stats_current_v29;stats_notice_v29=1;
 }
}
EXPORT void stats_session_reset_v29(void){
 stats_tick_v29();stats_active_v29=0;stats_current_v29=(MatchStatsV29){0};
 root_set(&stats_rules_root_v29,0);root_set(&stats_local_root_v29,0);root_set(&stats_ball_root_v29,0);
 stats_local_id_v29=stats_local_team_v29=-1;stats_rally_reset_v29();
}
EXPORT void stats_motion_v29(void* ball,V3 p,V3 v,int hit,int id,int team){
 if(!hit||!alive(ball)||!finitev(p)||!finitev(v)||id<0||team<0||team>1||
    !stats_active_v29||training_active_v29()||training_requested_v29()||lobby_is_ball(ball))return;
 float speed=dot(v,v);if(!__builtin_isfinite(speed)||speed>10000||p.y< -5||p.y>100||p.x< -100||p.x>100||p.z< -100||p.z>100)return;
 void* rules=rooted(stats_rules_root_v29);if(!alive(rules))return;
 /* Best-of-three may restart on the same persistent rules object. */
 if(stats_current_v29.complete){
  if(stats_sets_v29(rules,0)>=2||stats_sets_v29(rules,1)>=2)return;
  stats_prepare_v29(rules);
 }
 if(!(network_physics()?net_rally_active:BYTE(rules,0x78)||BYTE(rules,0x79)))return;
 float now=stats_now_v29();
 /* Repeated RPC delivery cannot create extra contacts or goal progress. */
 if(stats_event_valid_v29&&rooted(stats_ball_root_v29)==ball&&stats_event_id_v29==id&&stats_event_team_v29==team&&
    now>=stats_event_time_v29&&now-stats_event_time_v29<.08f&&
    p.x==stats_event_p_v29.x&&p.y==stats_event_p_v29.y&&p.z==stats_event_p_v29.z&&
    v.x==stats_event_v_v29.x&&v.y==stats_event_v_v29.y&&v.z==stats_event_v_v29.z)return;
 stats_identity_v29();int local=stats_is_local_v29(id,team);
 int first=!stats_rally_open_v29;
 int serving=first&&(network_physics()?net_first_touch:BYTE(rules,0x79));
 if(first){stats_rally_open_v29=1;stats_rally_start_v29=now;stats_rally_contacts_v29=0;stats_serve_team_v29=serving?team:-1;}
 int receive=!first&&stats_last_team_v29==1-team;
 int controlled=receive&&v.y>1.f&&speed<=18.f*18.f;
 if(receive){stats_add_v29(team,ST_RECEIVE_V29,local);if(local&&controlled)rewards_progress_v29(2,1);}
 /* A set only earns its goal when the next different teammate accepts it. */
 if(stats_set_local_v29&&stats_set_team_v29==team&&stats_set_id_v29!=id)rewards_progress_v29(3,1);
 stats_set_id_v29=stats_set_team_v29=-1;stats_set_local_v29=0;
 if(!serving&&v.y>=2.5f&&speed<=15.f*15.f&&p.y>1.f){
  stats_set_id_v29=id;stats_set_team_v29=team;stats_set_local_v29=local&&setting_context;
 }
 stats_last_attack_v29=!serving&&speed>=8.5f*8.5f&&v.y<3.f&&(team==0?v.z>1.5f:v.z< -1.5f);
 stats_add_v29(team,ST_CONTACT_V29,local);
 if(stats_rally_contacts_v29<999999)stats_rally_contacts_v29++;
 if(stats_current_v29.contacts<999999)stats_current_v29.contacts++;
 stats_current_v29.valid=1;stats_last_id_v29=id;stats_last_team_v29=team;stats_last_local_v29=local;
 if(rooted(stats_ball_root_v29)!=ball)root_set(&stats_ball_root_v29,ball);stats_event_valid_v29=1;stats_event_time_v29=now;
 stats_event_id_v29=id;stats_event_team_v29=team;stats_event_p_v29=p;stats_event_v_v29=v;
}
EXPORT void stats_point_v29(void* rules,int winner,int reason){
 if(!stats_active_v29||training_active_v29()||training_requested_v29()||stats_current_v29.complete||
    rules!=rooted(stats_rules_root_v29)||winner<0||winner>1||!stats_rally_open_v29)return;
 int ace=stats_rally_contacts_v29==1&&stats_serve_team_v29==winner&&stats_last_team_v29==winner&&(reason==3||reason==6||reason==0);
 if(ace){stats_add_v29(winner,ST_ACE_V29,stats_last_local_v29);if(stats_last_local_v29)rewards_progress_v29(1,1);}
 else if(reason==3&&stats_last_team_v29==winner&&stats_last_attack_v29){
  stats_add_v29(winner,ST_ATTACK_V29,stats_last_local_v29);if(stats_last_local_v29)rewards_progress_v29(4,1);
 }
 if((reason==1||reason==2||reason==4||reason==5||reason==6||reason==7)&&stats_last_team_v29==1-winner)
  stats_add_v29(1-winner,ST_ERROR_V29,stats_last_local_v29);
 float seconds=stats_now_v29()-stats_rally_start_v29;
 if(!(seconds>=0&&seconds<=3600))seconds=0;
 if(seconds>stats_current_v29.longest_seconds||(seconds==stats_current_v29.longest_seconds&&stats_rally_contacts_v29>stats_current_v29.longest_contacts)){
  stats_current_v29.longest_seconds=seconds;stats_current_v29.longest_contacts=stats_rally_contacts_v29;
 }
 if(stats_current_v29.points<999999)stats_current_v29.points++;
 /* Close first: duplicate Client_EndRally calls do not count twice. */
 stats_rally_reset_v29();
}
static char* stats_text_v29(char* p,const char* s){while(*s)*p++=*s++;return p;}
static char* stats_num_v29(char* p,int n){
 char b[12];int i=0;if(n<0)n=0;do{b[i++]=(char)('0'+n%10);n/=10;}while(n&&i<11);while(i)*p++=b[--i];return p;
}
static void stats_column_v29(void* panel,const char* path,const char* header,const int* values,int available){
 char text[128],*p=stats_text_v29(text,header);
 for(int i=0;i<5;i++){*p++='\n';if(available)p=stats_num_v29(p,values[i]);else *p++='-';}*p=0;
 child_label_v19(panel,path,text);
}
EXPORT void stats_refresh_v29(void* panel){
 if(!alive(panel))return;stats_tick_v29();
 MatchStatsV29* s=stats_active_v29&&stats_current_v29.valid?&stats_current_v29:&stats_last_v29;
 int available=s->valid;
 child_label_v19(panel,"CC_StatsState",!available?"PLAY A MATCH TO SEE YOUR STATS":s->complete?"LAST COMPLETED MATCH":"MATCH IN PROGRESS");
 stats_column_v29(panel,"CC_StatsYou","YOU",s->you,available);
 stats_column_v29(panel,"CC_StatsBlue","BLUE",s->team[0],available);
 stats_column_v29(panel,"CC_StatsRed","RED",s->team[1],available);
 char text[128],*p=stats_text_v29(text,"LONGEST RALLY  ");
 if(available){int dec=(int)(s->longest_seconds*10.f+.5f);p=stats_num_v29(p,dec/10);*p++='.';*p++=(char)('0'+dec%10);p=stats_text_v29(p,"s  /  ");p=stats_num_v29(p,s->longest_contacts);p=stats_text_v29(p," CONTACTS");}
 else *p++='-';*p=0;child_label_v19(panel,"CC_StatsLongest",text);
}
EXPORT void stats_open_v29(void* menu){
 if(!alive(menu))return;void* panel=find_child(menu,"CC_Stats");if(!panel)return;
 stats_refresh_v29(panel);FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);
}
EXPORT void stats_menu_v29(void* menu){
 if(!stats_notice_v29||!alive(menu)||!find_child(menu,"CC_Stats"))return;
 stats_notice_v29=0;stats_open_v29(menu);
}

