#include <stdint.h>
typedef struct {float x,y;} V2;typedef struct {float x,y,z,w;} Q4;
#define EXPORT __declspec(dllexport)
#define PTR(p,o) (*(void**)((char*)(p)+(o)))
typedef struct {int live,active,enabled;Q4 color,q;V2 uv;void* texture;} Node;
typedef struct {char data[0x170];} Body;
static Body bodies[9];static Node hats[9][7],arms[9][4],head[9],follow[9],preview[16],panel;
static Node arm_mats[9][4],preview_mats[16],raw_previews[2],base_atlases[2];
static int created,destroyed,restored;
static int players[9],styles[9],prefhat,prefarms,loaded,sets,finds,colors,enables,activates,refreshes,sends;
static int preferred_hand_tone_v21,style;
static unsigned custom_overlay;
static void* roots[512];static unsigned nextroot;
static void* rooted(unsigned r){return roots[r];}
static void root_set(unsigned* r,void* p){if(!*r)*r=++nextroot;roots[*r]=p;}
static int alive(void* p){return p&&((Node*)p)->live;}
static void* gameobject(void* p){return p;}
static void* transform(void* p){return p;}
static void* str(const char* p){return (void*)p;}
static int eq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static int named(void* b,const char*n){return eq((const char*)b,n);}
static int player_skin(void* p){return styles[(int*)p-players];}
static void* local_avatar_player(void){return &players[0];}
static int preferred_style(void){return style;}
static const Q4 hand_tone_colors_v21[6]={{1,.85,.74,1},{.91,.69,.49,1},{.76,.49,.29,1},{.58,.32,.17,1},{.36,.18,.1,1},{.19,.085,.05,1}};
static const Q4 sleeve_outfit_colors_v24[9]={{.06,.11,.16,1},{.97,.95,.94,1},{.06,.11,.16,1},{.94,.92,.91,1},{.97,.95,.94,1},{.06,.11,.16,1},{.13,.53,.81,1},{.09,.32,.26,1},{.45,.17,.29,1}};
static const char* names[7]={"CC_Hat_Cap","CC_Hat_Fedora","CC_Hat_Cowboy","CC_Hat_MotorcycleHelmet","CC_Hat_Beanie","CC_Hat_Crown","CC_Hat_Visor"};
static void* find_child(void* p,const char* path){
 finds++;if(!p)return 0;
 for(int i=0;i<9;i++){
  if(p==&bodies[i]){if(eq(path,"Physical Head/Visual Head Root/Head"))return &head[i];const char* paths[4]={"Physical Upper Arm L","Physical Lower Arm L","Physical Upper Arm R","Physical Lower Arm R"};for(int j=0;j<4;j++)if(eq(path,paths[j]))return &arms[i][j];}
  if(p==&head[i])for(int j=0;j<7;j++)if(eq(path,names[j]))return &hats[i][j];
 }
 if(p==&panel){if(eq(path,"CC_FacePreview"))return &raw_previews[0];if(eq(path,"CC_OutfitPreview"))return &raw_previews[1];const char* paths[8]={"CC_MirrorHead","CC_MirrorBody","CC_MirrorUpperL","CC_MirrorLowerL","CC_MirrorUpperR","CC_MirrorLowerR","CC_MirrorHandL","CC_MirrorHandR"};for(int j=0;j<8;j++)if(eq(path,paths[j]))return &preview[j];}
 if(p==&preview[0])for(int j=0;j<7;j++)if(eq(path,names[j]))return &preview[j+8];
 return 0;
}
static void* component(void*p,void*t,void*m){return p;}
static void* material(void*p,void*m){
 Node* node=0;for(int i=0;i<9;i++)for(int j=0;j<4;j++)if(p==&arms[i][j])node=&arm_mats[i][j];
 for(int i=0;i<16;i++)if(p==&preview[i])node=&preview_mats[i];
 if(!node)return p;if(!node->live){node->live=1;created++;}return node;
}
static void* sharedmaterial(void*p,void*m){return p;}
static void color(void*p,Q4 c,void*m){colors++;((Node*)p)->color=c;}
static void uv(void*p,V2 c,void*m){((Node*)p)->uv=c;}
static void active(void*p,_Bool c,void*m){activates++;((Node*)p)->active=c;}
static _Bool isactive(void*p,void*m){return ((Node*)p)->active;}
static void enabled(void*p,_Bool c,void*m){enables++;((Node*)p)->enabled=c;}
static Q4 rotation(void*p,void*m){return ((Node*)p)->q;}
static void setrotation(void*p,Q4 q,void*m){((Node*)p)->q=q;}
static int getint(void*p,int fallback,void*m){return eq(p,"Cloudcourt.Hat.v28")?prefhat:prefarms;}
static void setint(void*p,int v,void*m){sets++;if(eq(p,"Cloudcourt.Hat.v28"))prefhat=v;else prefarms=v;}
static void restore(void*r,void*s,void*m){restored++;}
static void destroy(void*r,void*m){((Node*)r)->live=0;destroyed++;}
static void queue(void*p,int q,void*m){}
static void* get_texture(void*p,void*m){return ((Node*)p)->texture;}
static void set_texture(void*p,void*t,void*m){((Node*)p)->texture=t;}
static void* dispatch(uintptr_t o){switch(o){case 0x223290:return get_texture;case 0x956850:return set_texture;case 0x956790:return uv;case 0x956900:return queue;case 0xa1af10:return sharedmaterial;case 0xa1b0e0:return restore;case 0xa0ab40:return destroy;case 0x94f410:return component;case 0xa1ae90:return material;case 0x956610:return color;case 0x9566d0:return uv;case 0x94f700:return active;case 0x94f9a0:return isactive;case 0xa1b2f0:return enabled;case 0xb74b50:return rotation;case 0xb754c0:return setrotation;case 0xa12690:return getint;case 0xa12870:return setint;}return 0;}
#define FN(o,t) ((t)dispatch(o))
static void customization_preferences_v28(void);
static void customization_mirror_refresh_v28(void*);
static void ensure_preferences_v19(void){if(!loaded){loaded=1;customization_preferences_v28();}}
static void customization_refresh_v19(void){refreshes++;customization_mirror_refresh_v28(&panel);}
static void child_label_v19(void*p,const char*a,const char*b){}
static void select_appearance(int a,int b){sends++;}
static void* customization_panel_v19(void){return &panel;}
static void customization_close_v19(void){panel.active=0;}
static int customization_button_v19(void*b){return 1;}
static void sleeves_reset_v28(void){}
#include "customization_v28.c"
EXPORT void setup(void){
 for(int i=0;i<2;i++){base_atlases[i].live=1;raw_previews[i].live=1;raw_previews[i].texture=&base_atlases[i];}
 panel.live=1;panel.active=0;root_set(&custom_overlay,&panel);
 for(int i=0;i<16;i++)preview[i].live=1;
 for(int i=0;i<9;i++){*(int*)&bodies[i]=1;PTR(&bodies[i],0x168)=&players[i];PTR(&bodies[i],0x30)=&follow[i];head[i].live=follow[i].live=1;follow[i].q=(Q4){.1,.2,.3,.9};for(int j=0;j<7;j++)hats[i][j].live=1;for(int j=0;j<4;j++)arms[i][j].live=1;}
}
EXPORT void load(int h,int a){prefhat=h;prefarms=a;loaded=0;ensure_preferences_v19();}
EXPORT int pref(int i){return i?preferred_transparent_arms_v28:preferred_hat_v28;}
EXPORT int click(int i){return customization_button_v28((void*)(i==0?"CC_HatNext":i==1?"CC_HatPrev":i==2?"CC_ArmsNext":"Unrelated"));}
EXPORT int receive(int i,int value){return appearance_receive_v28(&players[i],value);}
EXPORT void run(int i){avatar_cosmetics_v28(&bodies[i]);}
EXPORT int status(int i,int j){return j<7?hats[i][j].active:arms[i][j-7].enabled;}
EXPORT int count(int i){return i==0?finds:i==1?colors:i==2?enables:i==3?activates:i==4?sets:i==5?sends:i==6?refreshes:i==7?created:i==8?destroyed:restored;}
EXPORT void show(int v){panel.active=v;customization_refresh_v19();}
EXPORT float channel(int i,int c){return ((float*)&preview_mats[i].color)[c];}
EXPORT float mirrorq(int i){return ((float*)&preview[0].q)[i];}
EXPORT int base_textures_valid(void){return preview_mats[0].texture==&base_atlases[0]&&preview_mats[1].texture==&base_atlases[1];}
EXPORT void drop_material_textures(void){preview_mats[0].texture=preview_mats[1].texture=0;}
EXPORT void reset_all(void){customization_reset_v28();}
EXPORT void kill(int i){*(int*)&bodies[i]=0;}
int __stdcall DllMain(void*a,unsigned long b,void*c){return 1;}

