/* Exact production module, controlled native API/ownership fixture. */
typedef unsigned long long U64;
typedef struct{float x,y,z;} V3;
typedef struct{float x,y,z,w;} Q4;
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define FLT(o,n) (*(float*)((char*)(o)+(n)))
#define BYTE(o,n) (*(unsigned char*)((char*)(o)+(n)))
#define TRAMP(ret,name,args) static ret name##_trampoline args {}
static float sqroot(float x){return __builtin_sqrtf(x);}
static int finitev(V3 v){return __builtin_isfinite(v.x)&&__builtin_isfinite(v.y)&&__builtin_isfinite(v.z);}
static V3 add(V3 a,V3 b){return(V3){a.x+b.x,a.y+b.y,a.z+b.z};}
static V3 sub(V3 a,V3 b){return(V3){a.x-b.x,a.y-b.y,a.z-b.z};}
static V3 mul(V3 a,float b){return(V3){a.x*b,a.y*b,a.z*b};}
static float dot(V3 a,V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static Q4 normalized(Q4 q){float f=sqroot(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w);return(Q4){q.x/f,q.y/f,q.z/f,q.w/f};}
static unsigned char objects[40][512];
static V3 points[40];static Q4 rotations[40];static int active[40];
static void* roots[128];static int rootn;
static void* rooted(unsigned i){return i?roots[i]:0;}
static void root_set(unsigned* i,void* o){if(!*i&&o)*i=++rootn;if(*i)roots[*i]=o;}
static int index(void* p){for(int i=0;i<40;i++)if(p==objects[i])return i;return -1;}
static int alive(void* p){return p&&index(p)>=0&&!BYTE(p,0x130);}
static void* transform(void* p){return p;}
static void* gameobject(void* p){return p;}
static V3 position(void* p){int i=index(p);return i<0?(V3){0,0,0}:points[i];}
static int position_writes;
static void position_set(void* p,V3 v){position_writes++;points[index(p)]=v;}
static V3 player_court_position(void* p){return position(p);}
static V3 celebration_gaze_v24(void* p){V3 v=position(p);v.y+=1.6f;return v;}
static Q4 bone_rotation_v22(void* p,int local){return rotations[index(p)];}
static void bone_rotation_set_v22(void* p,Q4 q,int local){rotations[index(p)]=q;}
static int master=1,offline_mode=1,net_mode,finds,active_writes;
static int offline(void){return offline_mode;}
static int network_physics(void){return net_mode;}
static int doubles_enabled=1,quartet_enabled,serve_flight_team=-1;
static unsigned rules_root;
static void* v19_ball(void){return objects[10];}
static void* local_avatar_player(void){return objects[11];}
static float audio_gain;
static float audio_gain_v28(int category){return audio_gain;}
static void* str(const char* text){return (void*)text;}
static int member_role(void* p){return INT(p,0x124);}
static int humans_count;
static int celebration_humans_v24(void* rules,int team,void** humans,int* ids){
 if(humans_count){humans[0]=objects[11];ids[0]=111;}return humans_count;
}
static void visual_active_v21(void* p,int a){if(p){active[index(p)]=a;active_writes++;}}
static int same(const char* a,const char* b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static void* find_child(void* p,const char* name){finds++;return same(name,"CC_CallMine_v29")?objects[28]:objects[29];}
typedef struct{unsigned bot;int shown;} CelebrationStub;
static CelebrationStub bot_celebrations_v21[8];
static float now;
static float gettime(void* m){return now;}
static _Bool getmaster(void* m){return master;}
static void* view(void* p,void* m){return p;}
static _Bool mine(void* p,void* m){return BYTE(p,0x120);}
static int touchid(void* p,void* m){return INT(p,0x128);}
static int canreach=1;
static _Bool reach(void* p,V3 q,void* m){return canreach;}
static _Bool allowed(void* rules,int id,int team,V3 impact,void* m){return id!=INT(rules,0x98)||team!=INT(rules,0x7c);}
static int clips_created,sources_created,audio_plays,audio_uploads;static float source_gain,spatial_blend;
static unsigned char audio_samples[15000];static float audio_energy[2];
static void* reflection(void){return objects[35];}
static void* addsource(void* go,void* type,void* m){sources_created++;return objects[30];}
static void* createclip(void* name,int count,int channels,int rate,_Bool stream,void* m){return count==3528&&channels==1&&rate==22050?objects[31+clips_created++]:0;}
static void* newarray(void* type,U64 size){return size==3528?audio_samples:0;}
static _Bool upload(void* clip,void* samples,int offset,void* m){int k=index(clip)-31;float e=0;for(int i=0;i<3528;i++){float x=FLT(samples,0x20+4*i);if(x<-.101f||x>.101f)return 0;e+=x*x;}audio_energy[k]=e;audio_uploads++;return 1;}
static void setgain(void* source,float gain,void* m){source_gain=gain;}
static void setspatial(void* source,float gain,void* m){spatial_blend=gain;}
static void setclip(void* source,void* clip,void* m){}
static void play(void* source,void* m){audio_plays++;}
static void* dispatch(U64 r){switch(r){case 0xb72ae0:return gettime;case 0x61f230:return getmaster;case 0x6054c0:return view;case 0xe6e000:return mine;case 0x30cb70:return touchid;case 0x31aae0:return reach;case 0x252430:return allowed;case 0x14a920:case 0x14a910:case 0x14a530:case 0x14a5a0:case 0x14b9c0:case 0x14a710:case 0x14acb0:return reflection;case 0x94f240:return addsource;case 0xebc590:return setspatial;case 0xeba090:return createclip;case 0x14a4f0:return newarray;case 0xeba5f0:return upload;case 0xebc760:return setgain;case 0xebc2d0:return setclip;case 0xebbe30:return play;default:return 0;}}
#define FN(r,t) ((t)dispatch(r))
#include "bots_refine_v29.c"
static void init(void){
 for(int i=0;i<40;i++){for(int j=0;j<512;j++)objects[i][j]=0;points[i]=(V3){0,0,0};rotations[i]=(Q4){0,0,0,1};active[i]=0;}
 rootn=0;for(int i=0;i<128;i++)roots[i]=0;
 for(int i=0;i<8;i++){BotRefineV29 empty={0};bots_refine_v29[i]=empty;bot_celebrations_v21[i]=(CelebrationStub){0};}
 for(int i=0;i<2;i++){BotTeamV29 empty={0};bot_team_v29[i]=empty;}
 bots_refine_rules_v29=0;bots_refine_winner_v29=-1;bots_refine_point_v29=-100;
 rules_root=0;root_set(&rules_root,objects[0]);PTR(objects[0],0x60)=objects[1];PTR(objects[1],0x20)=objects[2];PTR(objects[1],0x28)=objects[3];
 PTR(objects[2],0x30)=objects[4];PTR(objects[4],0x10)=objects[5];INT(objects[4],0x18)=3;
 for(int i=0;i<3;i++){
  void* b=objects[6+i];PTR(objects[5],0x20+8*i)=b;INT(b,0x28)=0;BYTE(b,0x120)=1;INT(b,0x124)=i;INT(b,0x128)=30-i*10;
  points[6+i]=(V3){(float)(i-1)*2,0,-4};*(V3*)((char*)b+0xa8)=(V3){0,0,-4};
 }
 FLT(objects[2],0x20)=1.25f;points[10]=(V3){0,4,-4};*(V3*)(objects[10]+0x8c)=(V3){0,-1,0};
 BYTE(objects[0],0x78)=1;INT(objects[0],0x7c)=1;INT(objects[0],0x98)=99;INT(objects[0],0x9c)=1;
 offline_mode=1;net_mode=0;master=1;doubles_enabled=0;quartet_enabled=1;serve_flight_team=-1;humans_count=0;now=10;finds=active_writes=position_writes=0;
 bot_calls_v29=bot_cover_decisions_v29=bot_reactions_v29=0;
 bot_call_clips_v29[0]=bot_call_clips_v29[1]=0;audio_gain=0;clips_created=sources_created=audio_plays=audio_uploads=0;
 /* One complete visual rig for bot6; other bot tests do not bind. */
 PTR(objects[6],0xb8)=objects[20];PTR(objects[20],0x28)=objects[21];PTR(objects[20],0x38)=objects[22];PTR(objects[22],0x38)=objects[23];PTR(objects[23],0x68)=objects[24];PTR(objects[24],0x10)=objects[25];points[25]=(V3){0,1.7f,-4};
}
#define CHECK(x) do{if(!(x))return -__LINE__;checks++;}while(0)
EXPORT int test_bot_decisions_v29(void){
 init();int checks=0;V3 predicted;float seconds;
 CHECK(bot_predict_v29((V3){0,4,-6},(V3){2,-1,0},1.25f,&predicted,&seconds));CHECK(seconds>.5f&&seconds<1&&predicted.x>1&&predicted.x<2);
 CHECK(!bot_predict_v29((V3){0,-2,-6},(V3){0,0,0},1.25f,&predicted,&seconds));
 CHECK(!bot_predict_v29((V3){0,4,-6},(V3){0,100,0},1.25f,&predicted,&seconds));
 CHECK(!bot_predict_v29((V3){__builtin_nanf(""),4,-6},(V3){0,-1,0},1.25f,&predicted,&seconds));
 int ids[4]={30,10,20,40},ok[4]={1,1,1,1};V3 ps[4]={{-1,0,-4},{1,0,-4},{3,0,-4},{-3,0,-4}};
 CHECK(bot_choose_v29(ids,ps,ok,4,(V3){0,1,-4},0,-1)==1);
 CHECK(bot_choose_v29(ids,ps,ok,4,(V3){0,1,-4},1,-1)==-1);
 ok[1]=0;CHECK(bot_choose_v29(ids,ps,ok,4,(V3){0,1,-4},0,-1)==0);
 ok[1]=1;CHECK(bot_choose_v29(ids,ps,ok,4,(V3){0,1,-4},0,30)==0);
 CHECK(bot_choose_v29(ids,ps,ok,5,(V3){0,1,-4},0,-1)==-1);
 V3 lane0=bot_cover_goal_v29(0,0,(V3){0,0,-4},(V3){0,0,-6},0),lane1=bot_cover_goal_v29(0,1,(V3){0,0,-4},(V3){0,0,-6},0);
 CHECK(bot_distance_v29(lane0,lane1)>10);V3 gap=bot_cover_goal_v29(0,1,(V3){0,0,-4},lane1,1);CHECK(gap.x>lane1.x);
 bots_team_v29(objects[2]);CHECK(BYTE(objects[7],0x70)==1&&BYTE(objects[6],0x70)==0&&BYTE(objects[8],0x70)==0);CHECK(bot_team_v29[0].valid);
 /* Array order changes never change the elected stable closest bot. */
 PTR(objects[5],0x20)=objects[8];PTR(objects[5],0x30)=objects[6];bots_team_v29(objects[2]);CHECK(rooted(bot_team_v29[0].owner)==objects[7]);
 bots_assess_v29(objects[7]);CHECK(bot_calls_v29==1);bots_assess_v29(objects[7]);CHECK(bot_calls_v29==1);
 INT(objects[6],0xa4)=1;bots_assess_v29(objects[6]);CHECK(INT(objects[6],0xa4)==0);
 int writes=position_writes;bots_before_body_v29(objects[6]);CHECK(position_writes==writes);CHECK((*(V3*)(objects[6]+0xa8)).z< -6);
 V3 old=*(V3*)(objects[7]+0xa8);bots_before_body_v29(objects[7]);CHECK(bot_distance_v29(old,*(V3*)(objects[7]+0xa8))==0);
 /* No client-owned, foreign-owner, waiting serve or Bomb path mutates. */
 offline_mode=0;net_mode=1;master=0;BYTE(objects[6],0x70)=1;bots_team_v29(objects[2]);CHECK(BYTE(objects[6],0x70)==1);
 master=1;BYTE(objects[6],0x120)=0;bots_team_v29(objects[2]);CHECK(BYTE(objects[6],0x70)==1);
 BYTE(objects[6],0x120)=1;BYTE(objects[0],0x79)=1;bots_team_v29(objects[2]);CHECK(BYTE(objects[6],0x70)==1);
 BYTE(objects[0],0x79)=0;BYTE(objects[0],0x68)=1;bots_team_v29(objects[2]);CHECK(BYTE(objects[6],0x70)==1);
 BYTE(objects[0],0x68)=0;humans_count=1;bots_team_v29(objects[2]);CHECK(!BYTE(objects[6],0x70)&&!BYTE(objects[7],0x70)&&!BYTE(objects[8],0x70));
 canreach=0;bots_team_v29(objects[2]);CHECK(BYTE(objects[7],0x70));canreach=1;humans_count=0;
 /* Once teammate already touched: retain quartet receiver flags exactly. */
 INT(objects[0],0x7c)=0;INT(objects[0],0x9c)=1;BYTE(objects[6],0x70)=1;BYTE(objects[7],0x70)=0;bots_team_v29(objects[2]);CHECK(BYTE(objects[6],0x70)&&!BYTE(objects[7],0x70));
 /* Invalid/stale ball clears the decision, and no stale walk goal is used. */
 points[10].y=-20;bots_team_v29(objects[2]);CHECK(!bot_team_v29[0].valid);old=*(V3*)(objects[8]+0xa8);bots_before_body_v29(objects[8]);CHECK(bot_distance_v29(old,*(V3*)(objects[8]+0xa8))==0);
 bots_reset_v29();CHECK(!bot_team_v29[0].valid&&!rooted(bot_team_v29[0].owner)&&!rooted(bots_refine_rules_v29));
 return checks;
}
EXPORT int test_bot_visuals_v29(void){
 init();int checks=0;bot_character_v29_hook(objects[6],30,0);BotRefineV29* s=bot_slot_v29(objects[6],0);CHECK(s&&s->style==2);
 bots_visual_v29(objects[6]);CHECK(s->bound&&finds==2);for(int i=0;i<100;i++)bots_visual_v29(objects[6]);CHECK(finds==2);
 bot_emit_v29(s,1,now);bots_visual_v29(objects[6]);CHECK(active[28]&&!active[29]);CHECK(s->visible==1);unsigned calls=bot_calls_v29;
 bot_emit_v29(s,2,now+.5f);CHECK(bot_calls_v29==calls&&s->call==1);now+=.86f;bots_visual_v29(objects[6]);CHECK(!active[28]&&!active[29]&&s->call==0);
 now+=2;bot_emit_v29(s,2,now);bots_visual_v29(objects[6]);CHECK(active[29]&&!active[28]);BYTE(objects[0],0x79)=1;bots_visual_v29(objects[6]);CHECK(!active[28]&&!active[29]);BYTE(objects[0],0x79)=0;
 /* All nine exact character identities yield restrained and reversible poses. */
 const int ids[9]={39,12,30,21,15,18,0,45,6};
 for(int j=0;j<9;j++){
  bot_character_v29_hook(objects[6],ids[j],0);s=bot_slot_v29(objects[6],0);CHECK(s->style==j);
  now+=3;bots_point_v29(objects[0],1);bots_visual_v29(objects[6]);now=s->reaction+.4f;bots_ik_after_v29(objects[21]);
  Q4 q=rotations[25];CHECK(s->posed&&(q.x!=0||q.z!=0)&&q.x*q.x+q.z*q.z<.002f);
  bots_ik_before_v29(objects[22]);CHECK(!s->posed&&rotations[25].x==0&&rotations[25].z==0&&rotations[25].w==1);
 }
 root_set(&bot_celebrations_v21[0].bot,objects[6]);bot_celebrations_v21[0].shown=1;bots_ik_after_v29(objects[21]);CHECK(!s->posed);
 bot_celebrations_v21[0].shown=0;now=s->reaction+1.2f;bots_visual_v29(objects[6]);CHECK(s->reaction==0);bots_ik_after_v29(objects[21]);CHECK(!s->posed);
 int style=s->style;bots_rally_reset_v29();CHECK(s->style==style&&s->bound&&!s->reaction&&!s->call);
 float energy=0;int bounded=1;for(int i=0;i<3528;i++){float sample=bot_call_sample_v29(1,i);if(sample<-.101f||sample>.101f)bounded=0;energy+=sample*sample;}CHECK(bounded);
 CHECK(energy>.1f&&bot_call_sample_v29(1,-1)==0&&bot_call_sample_v29(2,3528)==0);
 bot_emit_v29(s,1,now+3);bots_visual_v29(objects[6]);bots_reset_v29();CHECK(!active[28]&&!active[29]&&!rooted(s->bot)&&!rooted(s->head));
 return checks;
}
EXPORT int test_bot_audio_v29(void){
 init();int checks=0;BotRefineV29* s=bot_slot_v29(objects[6],1);
 bot_call_audio_v29(s,1);CHECK(clips_created==0&&sources_created==0&&audio_plays==0);
 audio_gain=.5f;bot_call_audio_v29(s,1);CHECK(clips_created==1&&sources_created==1&&audio_uploads==1&&audio_plays==1);
 CHECK(source_gain>.174f&&source_gain<.176f&&spatial_blend==1);CHECK(audio_energy[0]>.1f);
 bot_call_audio_v29(s,1);CHECK(clips_created==1&&sources_created==1&&audio_uploads==1&&audio_plays==2);
 bot_call_audio_v29(s,2);CHECK(clips_created==2&&sources_created==1&&audio_uploads==2&&audio_plays==3);CHECK(audio_energy[1]>.1f);
 bot_call_audio_v29(s,3);CHECK(audio_plays==3);audio_gain=0;bot_call_audio_v29(s,2);CHECK(audio_plays==3);
 bots_rally_reset_v29();CHECK(rooted(s->audio)&&rooted(bot_call_clips_v29[0])&&s->bot);bots_reset_v29();CHECK(!rooted(s->audio));
 return checks;
}
int DllMain(void* module,unsigned reason,void* reserved){return 1;}
