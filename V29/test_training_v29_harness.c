#include <stdint.h>
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define BYTE(o,n) (*((unsigned char*)(o)+(n)))
typedef struct{float x,y,z;} V3;
typedef struct{float x,y,z,w;} Q4;
typedef void (*SetVec)(void*,V3,void*);
static int offline_=1,connected_,freeze_count,motion_count,spawn_count,visible_,target_visible[3];
static unsigned rules_root,local_player_root;
static unsigned char rules_[512],ball_[512],hand_[512],player_[512],body_[512],target_[3][64],target_go_[64],target_transform_[64];
static int api_errors,find_count,go_transform_count;
static V3 target_positions[3];
static void* roots[128];static V3 ballpos,handpos,playerpos,feed_origin,feed_velocity;static float now_;
static char labels[3][200];
static int equal(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static int finitev(V3 v){return __builtin_isfinite(v.x)&&__builtin_isfinite(v.y)&&__builtin_isfinite(v.z);}
static float sqroot(float n){return __builtin_sqrtf(n);}
static int offline(void){return offline_;}
static void* rooted(unsigned i){return i?roots[i]:0;}
static void root_set(unsigned* h,void* p){if(*h)roots[*h]=p;else if(p){for(unsigned i=1;i<128;i++)if(!roots[i]){roots[i]=p;*h=i;break;}}if(!p)*h=0;}
static int alive(void*p){return p!=0;}
static void* transform(void*p){if(p==target_go_){api_errors++;return 0;}return p;}
static void* gameobject(void*p){return p;}
static void* str(const char*p){return(void*)p;}
static void* find_child(void*p,const char*s){if(p!=target_transform_)api_errors++;return target_[equal(s,"GroundTarget")?0:equal(s,"AirTarget")?1:2];}
static int named(void*p,const char*s){return p&&equal(p,s);}
static void managed_field(void*p,int n,void*v){PTR(p,n)=v;}
static V3 position(void*p){return p==ball_?ballpos:p==player_?playerpos:handpos;}
static void position_set(void*p,V3 v){if(p==ball_)ballpos=v;for(int i=0;i<3;i++)if(p==target_[i])target_positions[i]=v;}
static V3 player_court_position(void*p){return playerpos;}
static void* v19_ball(void){return spawn_count?ball_:0;}
static void serve_visible(void*p,int b){visible_=b;}
static int hand_ball_place_v26(void*p,void*h){if(!h)return 0;ballpos=handpos;return 1;}
static int spawn_trigger_v24(void*h){return BYTE(h,0);}
static int ui_pointer_over_button_v19(void){return BYTE(hand_,1);}
static void label(void* p,const char*text){int i=p==(void*)1?0:p==(void*)2?1:2;int n=0;while(text[n]&&n<199){labels[i][n]=text[n];n++;}labels[i][n]=0;}
static _Bool connected(void*p){return connected_;}
static void* find(void*s,void*m){find_count++;return target_go_;}
static void* gameobject_transform(void*p,void*m){if(p!=target_go_)api_errors++;go_transform_count++;return target_transform_;}
static void* spawn(void*s,V3 p,Q4 q,unsigned char g,void*d,void*m){spawn_count++;ballpos=p;return ball_;}
static void* component(void*g,void*s,void*m){return ball_;}
static void active(void*p,_Bool b,void*m){for(int i=0;i<3;i++)if(p==target_[i])target_visible[i]=b;}
static void scale(void*p,V3 v,void*m){}
static void parent(void*p,void*q,void*m){}
static _Bool child(void*p,void*q,void*m){return p==hand_&&q==body_;}
static void freeze(void*p,void*m){freeze_count++;}
static void motion(void*p,V3 pos,V3 v,_Bool hit,_Bool thr,int id,int team,int context,void*m){motion_count++;feed_origin=ballpos=pos;feed_velocity=v;*(V3*)(ball_+0x8c)=v;}
static float time(void*m){return now_;}
static float dt(void*m){return .1f;}
static void tmp(void*p,void*s,void*m){label(p,s);}
static float font(void*p,void*m){return 30;}
static _Bool automatic(void*p,void*m){return 0;}
static void* no_parent(void*p,void*m){return 0;}
static void noop(void){}
static void* dispatch(uintptr_t n){switch(n){case 0x61efc0:return connected;case 0x94f3d0:return find;case 0x94fb00:return gameobject_transform;case 0x60fb50:return spawn;case 0x94f410:return component;case 0x94f700:return active;case 0xb75560:return scale;case 0xb755b0:return parent;case 12008720:return child;case 0x77ea70:return freeze;case 0x77e5c0:return motion;case 0xb72960:return dt;case 0xb72b40:return time;case 0x2405f0:return tmp;case 0x23e820:case 0x23e810:case 0x23e800:case 0x23e4a0:case 0xecce20:return font;case 0x23e600:return automatic;case 0xb739d0:return no_parent;default:return noop;}}
#define FN(n,t) ((t)dispatch(n))
#include "training_v29.c"
EXPORT int DllMain(void*a,unsigned b,void*c){return 1;}
EXPORT void reset(void){
 training_reset_v29();for(int i=0;i<128;i++)roots[i]=0;rules_root=local_player_root=0;
 for(int i=0;i<512;i++){rules_[i]=ball_[i]=hand_[i]=player_[i]=body_[i]=0;}
 offline_=1;connected_=freeze_count=motion_count=spawn_count=api_errors=find_count=go_transform_count=0;visible_=0;now_=0;
 training_difficulty_v29=1;handpos=(V3){0,1.2f,-7.6f};playerpos=(V3){0,0,-5.2f};
 root_set(&rules_root,rules_);root_set(&local_player_root,player_);PTR(player_,0x80)=body_;PTR(hand_,0x18)=hand_;
 PTR(rules_,0x28)=(void*)1;PTR(rules_,0x30)=(void*)2;PTR(rules_,0x38)=(void*)3;
}
EXPORT void start(int drill){training_request_v29(drill);training_begin_v29(rules_);}
EXPORT void trigger(int down){BYTE(hand_,0)=down;training_hand_update_v29(hand_);void* b=training_hand_ball_v29(hand_);if(b){PTR(hand_,0x30)=b;PTR(ball_,0xd8)=hand_;BYTE(ball_,0xd0)=1;}}
EXPORT void tick(void){now_+=.1f;training_tick_v29();}
EXPORT void sample(float x,float y,float z,float vy){ballpos=(V3){x,y,z};*(V3*)(ball_+0x8c)=(V3){0,vy,0};training_tick_v29();}
EXPORT void contact(float x,float y,float z,float vx,float vy,float vz,int hit,int thr,int id,int team){training_motion_v29(ball_,(V3){x,y,z},(V3){vx,vy,vz},hit,thr,id,team);}
EXPORT int ground(float x,float y,float z){ballpos=(V3){x,y,z};return training_ball_ground_v29(ball_);}
EXPORT int value(int i){return i==0?training_phase_v29:i==1?training_attempts_v29:i==2?training_hits_v29:i==3?freeze_count:i==4?motion_count:i==5?spawn_count:i==6?visible_:i==7?INT(rules_,0x9c):i==8?target_visible[0]:i==9?target_visible[1]:i==10?target_visible[2]:i==12?api_errors:i==13?find_count:i==14?go_transform_count:training_active_v29();}
EXPORT float measure(int i){return i==0?training_error_v29:i==8?target_positions[2].x:i<4?((&feed_origin.x)[i-1]):((&feed_velocity.x)[i-4]);}
EXPORT const char* text(int i){return labels[i];}
EXPORT void network(int off,int room){offline_=off;connected_=room;}
EXPORT int press(const char*s){return training_button_v29((void*)s);}
