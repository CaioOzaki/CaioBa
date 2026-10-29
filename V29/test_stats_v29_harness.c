#include <stdint.h>
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define BYTE(o,n) (*((unsigned char*)(o)+(n)))
typedef uint64_t U64;typedef struct{float x,y,z;}V3;
static void* roots[32];static unsigned nextroot;static int handles,finds,label_count,opened,identity_calls;
static void* rooted(unsigned h){return h?roots[h]:0;}
static void root_set(unsigned* h,void* p){if(*h){roots[*h]=0;*h=0;handles--;}if(p)for(int i=1;i<32;i++)if(!roots[i]){roots[i]=p;*h=i;handles++;break;}}
static int alive(void*p){return p!=0;}
static float dot(V3 a,V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static int finitev(V3 a){return __builtin_isfinite(a.x)&&__builtin_isfinite(a.y)&&__builtin_isfinite(a.z);}
static unsigned char rules_[256],sets_[64],local_[64],other_[64],ball_[64],menu_[64],panel_[64];
static void* local;static int training,pending,network,net_rally_active,net_first_touch,setting_context,lobby,missing_panel;
static float now;static int goals[8];
static int training_active_v29(void){return training;}
static int training_requested_v29(void){return pending;}
static int network_physics(void){return network;}
static int lobby_is_ball(void*p){return lobby;}
static void* local_avatar_player(void){return local;}
static void* transform(void*p){return p;}
static void* gameobject(void*p){return p;}
static int eq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static void* find_child(void*p,const char*s){finds++;return !missing_panel&&p==menu_&&eq(s,"CC_Stats")?panel_:0;}
static char labels[5][160];
static void child_label_v19(void*p,const char*path,const char*text){
 const char* paths[5]={"CC_StatsState","CC_StatsYou","CC_StatsBlue","CC_StatsRed","CC_StatsLongest"};
 for(int i=0;i<5;i++)if(eq(path,paths[i])){int j=0;for(;text[j]&&j<159;j++)labels[i][j]=text[j];labels[i][j]=0;}
 label_count++;
}
static int touchid(void*p,void*m){identity_calls++;return p==local_?42:77;}
static float clock_(void*m){return now;}
static void active(void*p,_Bool on,void*m){opened+=on!=0;}
static void* dispatch(uintptr_t a){switch(a){case 0x30cb70:return touchid;case 0xb72b40:return clock_;case 0x94f700:return active;default:return 0;}}
#define FN(a,t) ((t)dispatch(a))
EXPORT void rewards_progress_v29(int kind,int amount){if(kind>=1&&kind<8)goals[kind]+=amount;}
#include "stats_v29.c"
EXPORT int DllMain(void*a,unsigned b,void*c){return 1;}
static void reset(void){
 stats_session_reset_v29();stats_last_v29=(MatchStatsV29){0};stats_notice_v29=0;
 for(int i=0;i<256;i++)rules_[i]=0;for(int i=0;i<64;i++)sets_[i]=local_[i]=0;
 for(int i=0;i<8;i++)goals[i]=0;
 local=local_;INT(local_,0x28)=0;PTR(rules_,0xb0)=sets_;*(U64*)(sets_+0x18)=2;
 BYTE(rules_,0x78)=1;BYTE(rules_,0x79)=1;now=10;training=pending=network=lobby=setting_context=0;net_rally_active=1;net_first_touch=1;
 label_count=opened=finds=identity_calls=missing_panel=0;stats_prepare_v29(rules_);
}
static void contact(int id,int team,V3 v){now+=1;stats_motion_v29(ball_,(V3){0,2,team?-2:2},v,1,id,team);BYTE(rules_,0x79)=0;net_first_touch=0;}
#define CHECK(x) do{count++;if(!(x))return -__LINE__;}while(0)
EXPORT int test_stats_v29(void){
 int count=0;reset();CHECK(stats_active_v29);CHECK(identity_calls==1);CHECK(handles==2);
 contact(42,0,(V3){0,3,10});CHECK(stats_current_v29.you[4]==1);CHECK(stats_current_v29.team[0][4]==1);
 stats_motion_v29(ball_,(V3){0,2,2},(V3){0,3,10},1,42,0);CHECK(stats_current_v29.contacts==1);
 now+=4;stats_point_v29(rules_,0,6);CHECK(stats_current_v29.you[0]==1);CHECK(goals[1]==1);CHECK(stats_current_v29.longest_seconds==4);CHECK(stats_current_v29.longest_contacts==1);
 stats_point_v29(rules_,0,6);CHECK(stats_current_v29.points==1);CHECK(goals[1]==1);
 BYTE(rules_,0x79)=1;contact(77,1,(V3){0,3,-10});contact(42,0,(V3){0,4,4});
 CHECK(stats_current_v29.you[2]==1);CHECK(goals[2]==1);CHECK(goals[3]==0);
 contact(13,0,(V3){0,-1,12});now+=2;stats_point_v29(rules_,0,3);
 CHECK(stats_current_v29.team[0][1]==1);CHECK(stats_current_v29.you[1]==0);CHECK(goals[4]==0);CHECK(stats_current_v29.longest_contacts==3);
 BYTE(rules_,0x79)=1;contact(77,1,(V3){0,3,-10});setting_context=1;contact(42,0,(V3){0,5,2});setting_context=0;
 contact(13,0,(V3){0,-2,12});CHECK(goals[3]==1);stats_point_v29(rules_,0,3);
 CHECK(stats_current_v29.team[0][1]==2);CHECK(stats_current_v29.you[2]==2);
 BYTE(rules_,0x79)=1;contact(77,1,(V3){0,4,-10});contact(42,0,(V3){0,-2,12});stats_point_v29(rules_,0,3);
 CHECK(stats_current_v29.you[1]==1);CHECK(goals[4]==1);
 BYTE(rules_,0x79)=1;contact(42,0,(V3){0,3,10});stats_point_v29(rules_,1,6);
 CHECK(stats_current_v29.you[3]==1);CHECK(stats_current_v29.you[0]==1);
 BYTE(rules_,0x79)=1;contact(42,0,(V3){0,3,10});contact(77,1,(V3){0,2,-4});contact(42,0,(V3){0,3,1});stats_point_v29(rules_,0,3);
 CHECK(stats_current_v29.you[1]==1);CHECK(stats_current_v29.you[0]==1);
 int total=stats_current_v29.contacts;V3 bad={__builtin_nanf(""),0,0};stats_motion_v29(ball_,bad,(V3){0,2,3},1,42,0);
 stats_motion_v29(ball_,(V3){0,2,2},(V3){0,__builtin_inff(),3},1,42,0);CHECK(stats_current_v29.contacts==total);
 stats_motion_v29(ball_,(V3){0,2,2},(V3){1000,0,0},1,42,0);CHECK(stats_current_v29.contacts==total);
 stats_motion_v29(ball_,(V3){0,2,2},(V3){0,2,3},0,42,0);stats_motion_v29(ball_,(V3){0,2,2},(V3){0,2,3},1,-1,0);
 stats_motion_v29(ball_,(V3){0,2,2},(V3){0,2,3},1,42,2);CHECK(stats_current_v29.contacts==total);
 training=1;contact(42,0,(V3){0,2,3});stats_point_v29(rules_,0,3);CHECK(stats_current_v29.contacts==total);
 training=0;pending=1;contact(42,0,(V3){0,2,3});CHECK(stats_current_v29.contacts==total);pending=0;
 lobby=1;contact(42,0,(V3){0,2,3});CHECK(stats_current_v29.contacts==total);lobby=0;
 stats_refresh_v29(panel_);CHECK(eq(labels[0],"MATCH IN PROGRESS"));CHECK(label_count==5);CHECK(opened==0);
 INT(sets_,0x20)=2;stats_tick_v29();CHECK(stats_last_v29.valid&&stats_last_v29.complete);CHECK(stats_notice_v29==1);
 int contacts=stats_last_v29.contacts;stats_tick_v29();contact(42,0,(V3){0,2,3});CHECK(stats_last_v29.contacts==contacts);CHECK(stats_current_v29.contacts==contacts);
 stats_session_reset_v29();CHECK(!stats_active_v29);CHECK(handles==0);CHECK(stats_last_v29.contacts==contacts);
 stats_refresh_v29(panel_);CHECK(eq(labels[0],"LAST COMPLETED MATCH"));CHECK(opened==0);
 missing_panel=1;stats_menu_v29(menu_);CHECK(stats_notice_v29==1);CHECK(opened==0);
 missing_panel=0;stats_menu_v29(menu_);CHECK(stats_notice_v29==0);CHECK(opened==1);stats_menu_v29(menu_);CHECK(opened==1);
 stats_open_v29(menu_);CHECK(opened==2);
 INT(sets_,0x20)=0;stats_prepare_v29(rules_);CHECK(stats_current_v29.contacts==0);CHECK(stats_last_v29.contacts==contacts);
 /* Same rules restart after completion, without a menu scene reload. */
 BYTE(rules_,0x79)=1;contact(42,0,(V3){0,4,10});stats_point_v29(rules_,0,3);INT(sets_,0x24)=2;stats_tick_v29();CHECK(stats_current_v29.complete);
 INT(sets_,0x24)=0;BYTE(rules_,0x79)=1;contact(42,0,(V3){0,4,10});CHECK(!stats_current_v29.complete);CHECK(stats_current_v29.contacts==1);CHECK(stats_last_v29.contacts==1);
 stats_session_reset_v29();training=1;stats_prepare_v29(rules_);CHECK(!stats_active_v29);CHECK(handles==0);training=0;
 /* Online receives use synchronized rally state and actual local team. */
 stats_prepare_v29(rules_);int ids_before=identity_calls;network=1;INT(local_,0x28)=1;net_rally_active=0;contact(42,1,(V3){0,4,-10});CHECK(stats_current_v29.contacts==0);
 net_rally_active=1;net_first_touch=1;contact(77,0,(V3){0,3,10});contact(42,1,(V3){0,4,-4});CHECK(goals[2]>=3);
 CHECK(stats_current_v29.you[2]==1);CHECK(stats_current_v29.team[1][2]==1);CHECK(stats_current_v29.team[0][2]==0);
 stats_point_v29(rules_,0,4);CHECK(stats_current_v29.you[3]==1);
 int own=stats_current_v29.you[4];local=0;contact(77,0,(V3){0,4,8});CHECK(stats_current_v29.you[4]==own);
 CHECK(identity_calls==ids_before);CHECK(finds==4);stats_session_reset_v29();CHECK(handles==0);
 reset();stats_open_v29(menu_);CHECK(eq(labels[0],"PLAY A MATCH TO SEE YOUR STATS"));CHECK(eq(labels[1],"YOU\n-\n-\n-\n-\n-"));
 CHECK(stats_notice_v29==0);CHECK(opened==1);
 for(int reason=1;reason<=7;reason++){
  if(reason==3)continue;
  reset();contact(42,0,(V3){0,3,10});stats_point_v29(rules_,1,reason);
  CHECK(stats_current_v29.you[3]==1);CHECK(stats_current_v29.team[0][3]==1);CHECK(stats_current_v29.team[1][3]==0);
  CHECK(stats_current_v29.you[0]==0);stats_point_v29(rules_,1,reason);CHECK(stats_current_v29.you[3]==1);
 }
 reset();contact(42,0,(V3){0,4,10});now=1;stats_point_v29(rules_,0,3);CHECK(stats_current_v29.longest_seconds==0);CHECK(stats_current_v29.longest_contacts==1);
 *(U64*)(sets_+0x18)=1;INT(sets_,0x20)=2;stats_tick_v29();CHECK(!stats_current_v29.complete);
 *(U64*)(sets_+0x18)=2;INT(sets_,0x20)=999;stats_tick_v29();CHECK(!stats_current_v29.complete);
 reset();BYTE(rules_,0x78)=BYTE(rules_,0x79)=0;contact(42,0,(V3){0,4,10});CHECK(stats_current_v29.contacts==0);
 return count;
}



