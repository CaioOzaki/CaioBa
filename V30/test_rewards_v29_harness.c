/* Native material/persistence fixture: compiles the actual rewards module. */
#include <stdint.h>
#define EXPORT __declspec(dllexport)
typedef struct {float x,y;} V2;typedef struct {float x,y,z,w;} Q4;
typedef struct Node {int live,owned,enabled,id;Q4 color;V2 uv,scale;struct Node* texture,*material;} Node;
typedef struct {char data[0x170];} Body;
#define PTR(p,o) (*(void**)((char*)(p)+(o)))
static Body bodies[9];static Node players[10],mats[9][14],shared[9][14],sources[9][2],source_mats[9][2],textures[4],panel,mirror[8],mirror_shared[8],menu_sources[2],menu_source_mats[2];
static int styles[9],transparent[10],prefs[9],lookups,writes,bad_writes,saves,sets,sends,refreshes,source_disables;static float time_now;
static const char* keys[9]={"Cloudcourt.Aces.v29","Cloudcourt.ControlledReceives.v29","Cloudcourt.AssistedSets.v29","Cloudcourt.DirectKills.v29","Cloudcourt.AccurateServes.v29","Cloudcourt.AccurateSpikes.v29","Cloudcourt.RewardOutfit.v29","Cloudcourt.RewardFace.v29","Cloudcourt.RewardAccent.v29"};
static void* roots[4096];static unsigned root_count;static int root_assigns;
static void* rooted(unsigned r){return roots[r];}
static void root_set(unsigned* r,void* p){root_assigns++;if(!*r)*r=++root_count;roots[*r]=p;}
static int alive(void*p){return p&&((Node*)p)->live;}
static void* transform(void*p){return p;}
static void* gameobject(void*p){return p;}
static void* str(const char*p){return (void*)p;}
static int eq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static int named(void*p,const char*n){return eq(p,n);}
static void* local_avatar_player(void){return &players[0];}
static int preferred_style(void){return styles[0];}
static void* customization_panel_v19(void){return &panel;}
static void* customization_base_texture_v30(void* p,int i){return &textures[i];}
static int player_cosmetic_v28(void*p,int kind){return transparent[(Node*)p-players];}
static void select_appearance(int a,int b){sends++;}
static void customization_refresh_v19(void){refreshes++;}
static const Q4 sleeve_outfit_colors_v24[9]={{.06,.11,.16,1},{.97,.95,.94,1},{.06,.11,.16,1},{.94,.92,.91,1},{.97,.95,.94,1},{.06,.11,.16,1},{.13,.53,.81,1},{.09,.32,.26,1},{.45,.17,.29,1}};
typedef struct {unsigned body,materials[2];int skin;} AvatarSkin;static AvatarSkin skins[8];
typedef struct {unsigned body,materials[4],shared[4];} CosmeticBodyV28;static CosmeticBodyV28 cosmetic_bodies_v28[8];
typedef struct {unsigned body,materials[8],shared[8];} SleeveMaterialsV24;static SleeveMaterialsV24 sleeve_materials_v24[8];
typedef struct {unsigned material,shared;} MirrorMaterialV28;static MirrorMaterialV28 mirror_materials_v28[8];
static char state_label[512];static char value_labels[3][40];
static void copy(char*d,const char*s){while((*d++=*s++));}
static void child_label_v19(void*p,const char*name,const char*value){if(eq(name,"CC_RewardsState"))copy(state_label,value);else{const char* ns[3]={"CC_RewardOutfitValue","CC_RewardFaceValue","CC_RewardAccentValue"};for(int i=0;i<3;i++)if(eq(name,ns[i]))copy(value_labels[i],value);}}
static void* find_child(void*p,const char*path){
 lookups++;int part=eq(path,"CC_RewardSources/Face")?0:eq(path,"CC_RewardSources/Outfit")?1:-1;if(part<0)return 0;
 for(int i=0;i<9;i++)if(p==&bodies[i])return &sources[i][part];if(p==&panel)return &menu_sources[part];return 0;
}
static void* component(void*p,void*t,void*m){return p;}
static void* shared_material(void*p,void*m){return ((Node*)p)->material;}
static void* get_texture(void*p,void*m){return ((Node*)p)->texture;}
static void check_owned(void*p){writes++;if(!((Node*)p)->owned)bad_writes++;}
static void set_texture(void*p,void*t,void*m){check_owned(p);((Node*)p)->texture=t;}
static void set_color(void*p,Q4 c,void*m){check_owned(p);((Node*)p)->color=c;}
static void set_offset(void*p,V2 v,void*m){check_owned(p);((Node*)p)->uv=v;}
static void set_scale(void*p,V2 v,void*m){check_owned(p);((Node*)p)->scale=v;}
static void set_enabled(void*p,_Bool v,void*m){((Node*)p)->enabled=v;if(!v)source_disables++;}
static int get_int(void*p,int fallback,void*m){for(int i=0;i<9;i++)if(eq(p,keys[i]))return prefs[i];return fallback;}
static void set_int(void*p,int value,void*m){sets++;for(int i=0;i<9;i++)if(eq(p,keys[i]))prefs[i]=value;}
static float now(void*m){return time_now;}
static void save(void){saves++;}
static void* resolve(const char*n){return eq(n,"UnityEngine.PlayerPrefs::Save")?save:0;}
static void* dispatch(uintptr_t o){switch(o){case 0xa12690:return get_int;case 0xa12870:return set_int;case 0xb72a20:return now;case 0x14b030:return resolve;case 0x94f410:return component;case 0xa1af10:return shared_material;case 0x9564b0:return get_texture;case 0x956850:return set_texture;case 0x956610:return set_color;case 0x9566d0:return set_offset;case 0x956790:return set_scale;case 0xa1b2f0:return set_enabled;}return 0;}
#define FN(o,t) ((t)dispatch(o))
#include "rewards_v29.c"
static void initmat(Node* n,int owned,Node* tex){n->live=1;n->owned=owned;n->texture=tex;n->color=(Q4){1,1,1,1};n->uv=(V2){0,2/3.f};n->scale=(V2){1,1};}
EXPORT void setup(void){
 rewards_reset_v29();rewards_loaded_v29=0;rewards_dirty_v29=0;time_now=0;lookups=writes=bad_writes=saves=sets=sends=refreshes=source_disables=0;
 for(int i=0;i<9;i++)prefs[i]=0;
 for(int i=0;i<4;i++){textures[i].live=1;textures[i].id=i;}
 for(int i=0;i<10;i++){players[i].live=1;transparent[i]=0;}
 panel.live=1;
 for(int i=0;i<9;i++){
  *(int*)&bodies[i]=1;PTR(&bodies[i],0x168)=&players[i];styles[i]=18;
  for(int j=0;j<14;j++){initmat(&mats[i][j],1,&textures[j==1?1:0]);initmat(&shared[i][j],0,&textures[j==1?1:0]);}
  for(int j=0;j<2;j++){sources[i][j].live=1;sources[i][j].enabled=0;sources[i][j].material=&source_mats[i][j];initmat(&source_mats[i][j],0,&textures[j+2]);}
  if(i<8){root_set(&skins[i].body,&bodies[i]);root_set(&cosmetic_bodies_v28[i].body,&bodies[i]);root_set(&sleeve_materials_v24[i].body,&bodies[i]);
   for(int j=0;j<2;j++)root_set(&skins[i].materials[j],&mats[i][j]);
   for(int j=0;j<4;j++){root_set(&cosmetic_bodies_v28[i].materials[j],&mats[i][j+2]);root_set(&cosmetic_bodies_v28[i].shared[j],&shared[i][j+2]);}
   for(int j=0;j<8;j++){root_set(&sleeve_materials_v24[i].materials[j],&mats[i][j+6]);root_set(&sleeve_materials_v24[i].shared[j],&shared[i][j+6]);}
  }
 }
 for(int i=0;i<8;i++){initmat(&mirror[i],1,&textures[i==1?1:0]);initmat(&mirror_shared[i],0,&textures[i==1?1:0]);root_set(&mirror_materials_v28[i].material,&mirror[i]);root_set(&mirror_materials_v28[i].shared,&mirror_shared[i]);}
 for(int i=0;i<2;i++){menu_sources[i].live=1;menu_sources[i].enabled=0;menu_sources[i].material=&menu_source_mats[i];initmat(&menu_source_mats[i],0,&textures[i+2]);}
}
EXPORT void load(void){rewards_load_v29();}
EXPORT void restart(void){rewards_loaded_v29=0;rewards_load_v29();}
EXPORT void setpref(int i,int value){prefs[i]=value;}
EXPORT int getpref(int i){return prefs[i];}
EXPORT int value(int i){return i<6?rewards_counts_v29[i]:rewards_choices_v29[i-6];}
EXPORT int unlocked(int c){return rewards_unlocked_v29(c);}
EXPORT void progress(int k,int n){rewards_progress_v29(k,n);}
EXPORT void tick(float dt){time_now+=dt;rewards_tick_v29();}
EXPORT int count(int k){return k==8?root_assigns:k==0?lookups:k==1?writes:k==2?bad_writes:k==3?saves:k==4?sets:k==5?sends:k==6?refreshes:source_disables;}
EXPORT int click(int kind,int direction){const char* names[6]={"CC_RewardOutfitPrev","CC_RewardOutfitNext","CC_RewardFacePrev","CC_RewardFaceNext","CC_RewardAccentPrev","CC_RewardAccentNext"};return rewards_button_v29((void*)(kind<0?"Unrelated":names[kind*2+(direction>0)]));}
EXPORT int receive(int p,int packet){return rewards_receive_v29(&players[p],packet);}
EXPORT int peer(int p,int kind){return rewards_player_choice_v29(&players[p],kind);}
EXPORT void deadplayer(int p){players[p].live=0;}
EXPORT int peer_slots(int p){int n=0;for(int i=0;i<8;i++)n+=rooted(rewards_peers_v29[i].player)==&players[p];return n;}
EXPORT void run(int p){rewards_body_v29(&players[p],&bodies[p],styles[p]);}
EXPORT void style(int p,int v){styles[p]=v;}
EXPORT int texture(int p,int part){return mats[p][part].texture->id;}
EXPORT float uv(int p,int part,int axis){return ((float*)&mats[p][part].uv)[axis];}
EXPORT float scale(int p,int part,int axis){return ((float*)&mats[p][part].scale)[axis];}
EXPORT float color(int p,int part,int axis){return ((float*)&mats[p][part].color)[axis];}
EXPORT void show(void){rewards_refresh_v29(&panel);}
EXPORT const char* label_value(int k){return k<0?state_label:value_labels[k];}
EXPORT void mirror_run(void){rewards_mirror_v29(&panel);}
EXPORT int mirror_texture(int i){return mirror[i].texture->id;}
EXPORT float mirror_color(int i,int axis){return ((float*)&mirror[i].color)[axis];}
EXPORT void mirror_scene_loss(void){for(int i=0;i<2;i++)mirror[i].texture=0;root_set(&rewards_mirror_state_v29.owner,0);}
EXPORT void mirror_base(void){for(int i=0;i<2;i++){mirror[i].uv=(V2){0,0};mirror[i].color=(Q4){1,1,1,1};}for(int i=2;i<6;i++)mirror[i].color=sleeve_outfit_colors_v24[styles[0]/9];}
EXPORT void transparent_change(int p,int v){transparent[p]=v;for(int j=2;j<14;j++)mats[p][j].color=sleeve_outfit_colors_v24[styles[p]/9];}
EXPORT void reset(void){rewards_reset_v29();}
EXPORT void body_dead(int p){*(int*)&bodies[p]=0;}
EXPORT void material_missing(int p,int part){root_set(&skins[p].materials[part],0);}
EXPORT void material_return(int p,int part){root_set(&skins[p].materials[part],&mats[p][part]);}
EXPORT int root_total(void){return root_count;}
int __stdcall DllMain(void*a,unsigned long b,void*c){return 1;}

