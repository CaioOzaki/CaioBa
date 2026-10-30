#include <stdint.h>
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define FLT(o,n) (*(float*)((char*)(o)+(n)))
#define BYTE(o,n) (*((unsigned char*)(o)+(n)))
typedef struct{float x,y,z;}V3;
static int eq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static unsigned char system_[256],list_[64],array_[64],entry_[64],source_[64],secondary_[64],clip_[64],effect_[64],ui_[64],whistle_[64],page_[64];
static void* roots[512];static unsigned count;static int prefs[4],music_on=1,play_count,stop_count,loop_count,save_count;static float master,volumes[5];
static unsigned ui_v19_click_source,serve_whistle_source_v21;static void(*graphics_save_v24)(void);
static void* rooted(unsigned r){return r?roots[r]:0;}
static void root_set(unsigned*h,void*p){if(*h)roots[*h]=0;*h=p?++count:0;if(*h)roots[*h]=p;}
static int alive(void*p){return p!=0;}
static void* str(const char*s){return (void*)s;}
static void* transform(void*p){return p;}
static void* gameobject(void*p){return p;}
static void* find_child(void*p,const char*s){return (void*)s;}
static void child_label_v19(void*p,const char*path,const char*text){}
static int named(void*p,const char*s){return eq(p,s);}
static void managed_field(void*p,int offset,void*v){PTR(p,offset)=v;}
static void graphics_refresh_v24(void){}
static void graphics_close_v24(void){}
static void save(void){save_count++;}
static void graphics_resolve_v24(void){graphics_save_v24=save;}
static int pref_index(void*s){const char*n=s;for(;*n;n++)if(eq(n,"Master.v28"))return 0;else if(eq(n,"Music.v28"))return 1;else if(eq(n,"Game.v28"))return 2;else if(eq(n,"UI.v28"))return 3;return -1;}
static int get_pref(void*s,int fallback,void*m){int i=pref_index(s);return i<0||prefs[i]==-999?fallback:prefs[i];}
static void set_pref(void*s,int v,void*m){int i=pref_index(s);if(i>=0)prefs[i]=v;}
static void set_master(float v){master=v;}
static void* resolve(const char*s){return eq(s,"UnityEngine.AudioListener::set_volume")?set_master:0;}
static int source_index(void*s){return s==source_?0:s==secondary_?1:s==effect_?2:s==ui_?3:4;}
static void volume(void*s,float v,void*m){volumes[source_index(s)]=v;}
static float get_volume(void*s,void*m){return volumes[source_index(s)];}
static void set_clip(void*s,void*c,void*m){PTR(s,0)=c;}
static void loop(void*s,_Bool b,void*m){loop_count+=b;}
static void spatial(void*s,float f,void*m){}
static void play(void*s,void*m){play_count++;}
static void stop(void*s,void*m){stop_count++;}
static _Bool enabled(void*m){return music_on!=0;}
static void active(void*s,_Bool b,void*m){}
static void nothing(void){}
static void* trampoline_result(const char*name){return eq(name,"audio_effect_v28")?effect_:0;}
#define TRAMP(ret,name,args) static ret name##_trampoline args {return (ret)trampoline_result(#name);}
static void* dispatch(uintptr_t v){switch(v){case 0xa12690:return get_pref;case 0xa12870:return set_pref;case 0x14b030:return resolve;case 0xebc760:return volume;case 0xebc290:return get_volume;case 0xebc2d0:return set_clip;case 0xebc370:return loop;case 0xebc590:return spatial;case 0xebbe30:return play;case 0xebc000:return stop;case 0xef33f0:return enabled;case 0x94f700:return active;default:return nothing;}}
#define FN(o,t) ((t)dispatch(o))
#include "settings_audio_v28.c"
EXPORT int DllMain(void*a,unsigned b,void*c){return 1;}
EXPORT void reset(int a,int b,int c,int d){
 for(int i=0;i<512;i++)roots[i]=0;count=0;for(int i=0;i<5;i++)volumes[i]=0;
 prefs[0]=a;prefs[1]=b;prefs[2]=c;prefs[3]=d;audio_loaded_v28=0;audio_bound_source_v28=audio_bound_clip_v28=audio_system_v28=settings_page_v28=0;
 for(int i=0;i<32;i++)audio_effects_v28[i].source=0;
 int defaults[4]={100,65,100,80};for(int i=0;i<4;i++)audio_levels_v28[i]=defaults[i];
 music_on=1;play_count=stop_count=loop_count=save_count=0;
 PTR(system_,0x58)=source_;PTR(system_,0x60)=secondary_;PTR(system_,0x18)=list_;PTR(list_,0x10)=array_;INT(list_,0x18)=1;PTR(array_,0x20)=entry_;PTR(entry_,0x18)=clip_;
 root_set(&ui_v19_click_source,ui_);root_set(&serve_whistle_source_v21,whistle_);root_set(&settings_page_v28,page_);
}
EXPORT void start(void){audio_music_v28_hook(system_,0,0,0,0);}
EXPORT void tick(void){audio_update_v28_hook(system_,0);}
EXPORT void stop_request(void){audio_stop_v28_hook(system_,0);}
EXPORT void set_music(int on){music_on=on;audio_options_v28_hook(system_,0);}
EXPORT int press(const char*s){return settings_button_v28((void*)s);}
EXPORT int value(int i){return i<4?audio_levels_v28[i]:i==4?play_count:i==5?stop_count:i==6?loop_count:i==7?save_count:i==8?settings_tab_v28:count;}
EXPORT float level(int i){return i<5?volumes[i]:master;}
EXPORT void effect_play(void){volumes[2]=.8f;audio_effect_v28_hook(system_,clip_,0,0,0,0,0);}
EXPORT void rebind(void){audio_bound_source_v28=0;audio_playlist_v28(system_,1);}
