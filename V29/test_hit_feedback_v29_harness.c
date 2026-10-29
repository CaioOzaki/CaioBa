/* Isolated host for the actual hit_feedback_v29.c production implementation. */
#include <stdint.h>
#define EXPORT __declspec(dllexport)
typedef unsigned long long U64;
typedef struct {float x,y,z;}V3;
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define BYTE(o,n) (*((unsigned char*)(o)+(n)))
static V3 add(V3 a,V3 b){return (V3){a.x+b.x,a.y+b.y,a.z+b.z};}
static V3 sub(V3 a,V3 b){return (V3){a.x-b.x,a.y-b.y,a.z-b.z};}
static float dot(V3 a,V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static int finitev(V3 a){return __builtin_isfinite(a.x)&&__builtin_isfinite(a.y)&&__builtin_isfinite(a.z);}
static unsigned char body_[400],part_[100],ball_[256],collision_[100],contacts_[100],effect_[100],string_[100];
static unsigned char controllers_[3][128],hosts_[3][32],clips_[3][32],samples_[13000],routine_[64],running_[3][64],old_[3][32];
static int local_,setting_context,creates,sets,destroys,allocs,generic,stops,starts,backend,bad_abi,fail_create,fail_set,fail_routine;
static V3 hand_;static float pcm_[3][3087],amplitude_,duration_,frequency_;static void* roots_[128];static unsigned handles_,free_handles_;
static void* local_avatar_player(void){return local_?&local_:0;}
static void* rooted(unsigned h){return h?roots_[h]:0;}
static void root_set(unsigned* h,void* p){if(*h){roots_[*h]=0;free_handles_++;}*h=0;if(p){for(unsigned i=1;i<128;i++)if(!roots_[i]){roots_[i]=p;*h=i;handles_++;break;}}}
static int alive(void*p){return p&&p!=hosts_[2];}
static void* str(const char*s){return (void*)s;}
static void managed_field(void*p,int n,void*v){PTR(p,n)=v;}
static V3 velocity(void*p,V3 point,void*m){if(p!=part_||m)bad_abi++;return hand_;}
static void* create_clip(void*name,int n,int channels,int hz,_Bool stream,void*m){if(channels!=1||hz!=22050||stream||m||creates>=3)bad_abi++;if(fail_create)return 0;return clips_[creates++];}
static void* corlib(void){return &local_;}
static void* klass(void*image,const char*ns,const char*name){return image;}
static void* array(void*k,U64 n){allocs++;return samples_;}
static _Bool set_data(void*clip,void*samples,int offset,void*m){if(offset||m||samples!=samples_)bad_abi++;int k=(int)(((unsigned char*)clip-(unsigned char*)clips_)/32);for(int i=0;i<3087;i++)pcm_[k][i]=*(float*)((char*)samples+0x20+i*4);sets++;return !fail_set;}
static void destroy(void*o,void*m){destroys++;}
static const char* class_name(void*k){return k==controllers_[0]?"OculusVRController":k==controllers_[1]?"OpenVRController":"OtherController";}
static void generic_dispatch(int slot,void*type,void*controller,int effect){generic++;if(slot!=17||effect!=1)backend=9;}
static void* oculus(void*c,float f,float a,float d,void*m){if(c!=controllers_[0]||m)bad_abi++;backend=1;frequency_=f;amplitude_=a;duration_=d;return fail_routine?0:routine_;}
static void* openvr(void*c,float a,float d,void*m){if(c!=controllers_[1]||m)bad_abi++;backend=2;frequency_=0;amplitude_=a;duration_=d;return fail_routine?0:routine_;}
static void stop(void*host,void*prior,void*m){if(m||(prior!=old_[backend-1]&&prior!=running_[backend-1])||host!=hosts_[backend-1])bad_abi++;stops++;}
static void* start(void*host,void*r,void*m){if(host!=hosts_[backend-1]||r!=routine_||m)bad_abi++;starts++;return running_[backend-1];}
static void* dispatch(uintptr_t a){switch(a){case 0xeea0e0:return velocity;case 0xeba090:return create_clip;case 0x14acb0:return corlib;case 0x14a5a0:return klass;case 0x14a4f0:return array;case 0xeba5f0:return set_data;case 0xa0ab40:return destroy;case 0x14a6a0:return class_name;case 0xa3800:return generic_dispatch;case 0x383bf0:return oculus;case 0x384fd0:return openvr;case 0xa0a5e0:return stop;case 0xa0a0c0:return start;}bad_abi++;return 0;}
#define FN(a,t) ((t)dispatch(a))
#include "hit_feedback_v29.c"
EXPORT int DllMain(void*a,unsigned b,void*c){return 1;}
EXPORT void reset(void){
 hit_feedback_end_v29();for(int i=0;i<3;i++){hit_clips_v29[i]=0;hit_clip_failed_v29[i]=0;}
 for(int i=0;i<128;i++)roots_[i]=0;handles_=free_handles_=0;
 creates=sets=destroys=allocs=generic=stops=starts=bad_abi=0;fail_create=fail_set=fail_routine=0;
 amplitude_=duration_=frequency_=0;local_=1;setting_context=0;PTR(body_,0x168)=&local_;INT(part_,0x18)=3;BYTE(ball_,0x88)=1;
 INT(collision_,0x38)=1;PTR(collision_,0x40)=contacts_;*(U64*)(contacts_+0x18)=1;*(V3*)(contacts_+0x20)=(V3){0,2,0};
 PTR(effect_,0x10)=string_;INT(string_,0x10)=7;const char*s="BallHit";for(int i=0;i<7;i++)*(unsigned short*)(string_+0x14+2*i)=s[i];
 for(int i=0;i<3;i++){PTR(controllers_[i],0)=controllers_[i];PTR(controllers_[i],i==0?0x20:0x48)=hosts_[i];PTR(controllers_[i],i==0?0x28:0x58)=old_[i];}
}
EXPORT int classify(V3*incoming,V3*hand,V3*out,int assisted){return hit_classify_v29(*incoming,*hand,*out,assisted);}
EXPORT void begin(V3*incoming,V3*hand,int assisted,int owned){hand_=*hand;*(V3*)(ball_+0x8c)=*incoming;setting_context=assisted;local_=owned;hit_feedback_begin_v29(body_,part_,ball_,collision_);}
EXPORT void accept(V3*out,int same){hit_feedback_accept_v29(same?ball_:part_,*out);}
EXPORT void end(void){hit_feedback_end_v29();}
EXPORT int sound(int exact){if(!exact)INT(string_,0x10)=6;void*p=hit_feedback_clip_v29(part_,effect_);INT(string_,0x10)=7;return p==part_?-1:(int)(((unsigned char*)p-(unsigned char*)clips_)/32);}
EXPORT void haptic(int which){hit_haptic_dispatch_v29(17,part_,controllers_[which],1);}
EXPORT void other_haptic(int slot,int effect){hit_haptic_dispatch_v29(slot,part_,controllers_[0],effect);}
EXPORT int value(int k){switch(k){case 0:return creates;case 1:return sets;case 2:return allocs;case 3:return generic;case 4:return stops;case 5:return starts;case 6:return bad_abi;case 7:return destroys;case 8:return hit_contact_v29.active;case 9:return hit_contact_v29.accepted;case 10:return hit_contact_v29.kind;case 11:return handles_-free_handles_;case 12:return PTR(controllers_[0],0x28)==running_[0];case 13:return PTR(controllers_[1],0x58)==running_[1];}return -1;}
EXPORT float level(int k){return k==0?amplitude_:k==1?duration_:frequency_;}
EXPORT float sample(int clip,int n){return pcm_[clip][n];}
EXPORT void failure(int type){fail_create=type==1;fail_set=type==2;fail_routine=type==3;if(type==4)PTR(controllers_[0],0x20)=hosts_[2];}
EXPORT void invalid_contact(int type){if(type==1)INT(part_,0x18)=0;if(type==2)INT(collision_,0x38)=0;if(type==3)BYTE(ball_,0x88)=0;if(type==4)PTR(collision_,0x40)=0;}
