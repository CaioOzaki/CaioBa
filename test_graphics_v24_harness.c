#include <stdint.h>
#define EXPORT __declspec(dllexport)
#define TRAMP(ret,name,args) static ret name##_trampoline args {}
#define BYTE(o,n) (*((unsigned char*)(o)+(n)))
static int strcmp(const char* a,const char* b){while(*a&&*a==*b){a++;b++;}return *a-*b;}
static const char* strstr(const char* a,const char* b){for(;*a;a++){int i=0;while(b[i]&&a[i]==b[i])i++;if(!b[i])return a;}return 0;}
EXPORT int DllMain(void* a,unsigned b,void* c){return 1;}
static int loaded_pref=-1,saved_count,visible,values[7],apply_calls,scale_calls;
static float floats[3];
static unsigned handle;
static void* rooted(unsigned r){return r?(void*)2:0;}
static void root_set(unsigned* r,void* p){*r=p?1:0;}
static int alive(void* p){return p!=0;}
static void* str(const char* s){return (void*)s;}
static void* menu_transform_v19(void){return (void*)1;}
static void* find_child(void* p,const char* s){return (void*)2;}
static void* gameobject(void* p){return p;}
static void child_label_v19(void* p,const char* path,const char* text){}
static void customization_close_v19(void){}
static int named(void* p,const char* s){return !strcmp(p,s);}
static int get_pref(void* s,int fallback,void* m){return loaded_pref==-1?fallback:loaded_pref;}
static void set_pref(void* s,int value,void* m){loaded_pref=value;}
static void active(void* p,_Bool b,void* m){visible=b;}
static void aa(int x,void* m){values[0]=x;apply_calls++;}
static void scale(float f,void* m){floats[0]=f;scale_calls++;}
static void texture(int x){values[1]=x;}
static void aniso(int x){values[2]=x;}
static void shadows(int x){values[3]=x;}
static void shadow_res(int x){values[4]=x;}
static void particles(_Bool x){values[5]=x;}
static void reflections(_Bool x){values[6]=x;}
static void distance(float x){floats[1]=x;}
static void lod(float x){floats[2]=x;}
static void save(void){saved_count++;}
static void* resolve(const char* name){
 if(strstr(name,"set_masterTextureLimit"))return texture;
 if(strstr(name,"set_anisotropicFiltering"))return aniso;
 if(strstr(name,"set_shadowResolution"))return shadow_res;
 if(strstr(name,"set_shadowDistance"))return distance;
 if(strstr(name,"set_shadows"))return shadows;
 if(strstr(name,"set_softParticles"))return particles;
 if(strstr(name,"set_realtimeReflectionProbes"))return reflections;
 if(strstr(name,"set_lodBias"))return lod;
 if(strstr(name,"PlayerPrefs::Save"))return save;
 return 0;
}
static void* dispatch(uintptr_t o){
 switch(o){case 0xa12690:return get_pref;case 0xa12870:return set_pref;
 case 0xa12bf0:return aa;case 0xed8cf0:return scale;case 0x14b030:return resolve;
 case 0x94f700:return active;default:return 0;}
}
#define FN(o,t) ((t)dispatch(o))
#include "graphics_v24.c"
EXPORT void test_reset(int pref){loaded_pref=pref;graphics_loaded_v24=0;saved_count=apply_calls=visible=0;}
EXPORT void test_start(void){graphics_start_v24();}
EXPORT int test_press(const char* s){return graphics_button_v24((void*)s);}
EXPORT int test_value(int i){return i<7?values[i]:i==7?graphics_selected_v24:i==8?loaded_pref:i==9?saved_count:i==10?visible:apply_calls;}
EXPORT float test_float(int i){return floats[i];}
EXPORT int test_ovr_fields(int loaded){
 unsigned char object[64];for(int i=0;i<64;i++)object[i]=(unsigned char)(i+1);
 graphics_loaded_v24=loaded;graphics_ovr_update_hook(object,0);
 for(int i=0;i<64;i++){unsigned char expected=loaded&&(i==0x25||i==0x27)?0:(unsigned char)(i+1);if(object[i]!=expected)return 0;}
 return 1;
}
EXPORT int test_adaptive_apply(void){
 graphics_loaded_v24=1;graphics_selected_v24=1;int before_aa=apply_calls,before_scale=scale_calls;
 graphics_adaptive_apply_hook(0,0);
 return apply_calls==before_aa&&scale_calls==before_scale+1&&floats[0]==.85f;
}
