#include <stdint.h>
typedef struct {float x,y,z,w;} Q4;
#define EXPORT __declspec(dllexport)
#define PTR(p,o) (*(void**)((char*)(p)+(o)))
typedef struct {int live;Q4 color;} Node;
typedef struct {char pad[0x168];void* player;} Body;
typedef struct {int style,tone;} Player;
static Body bodies[9];static Player players[9];static Node nodes[9][8];
static int bodylive[9],finds,reads,writes,missing=-1;
static void* roots[512];static unsigned nextroot;
static void* rooted(unsigned r){return roots[r];}
static void root_set(unsigned* r,void* p){if(!*r)*r=++nextroot;roots[*r]=p;}
static int alive(void* p){
 if(!p)return 0;
 for(int i=0;i<9;i++){if(p==&bodies[i])return bodylive[i];for(int j=0;j<8;j++)if(p==&nodes[i][j])return nodes[i][j].live;}
 return 1;
}
static void* transform(void* p){return p;}
static void* gameobject(void* p){return p;}
static void* str(const char* s){return (void*)s;}
static int player_skin(void* p){return ((Player*)p)->style;}
static int player_hand_tone_v21(void* p){return ((Player*)p)->tone;}
static const Q4 hand_tone_colors_v21[6]={{1,.85f,.74f,1},{.91f,.69f,.49f,1},{.76f,.49f,.29f,1},{.58f,.32f,.17f,1},{.36f,.18f,.10f,1},{.19f,.085f,.05f,1}};
static int contains(const char* s,const char* p){for(;*s;s++){const char *a=s,*b=p;while(*a&&*a==*b){a++;b++;}if(!*b)return 1;}return 0;}
static void* find_child(void* body,const char* path){
 finds++;int side=contains(path,"Root R"),index;
 if(contains(path,"ThumbsUp"))index=4+side;
 else if(contains(path,"SettingOpen"))index=6+side;
 else index=side*2+contains(path,"/Closed/");
 int n=(int)((Body*)body-bodies);return &nodes[n][index];
}
static void* get_renderer(void* go,void* type,void* m){return go;}
static void* get_material(void* go,void* m){reads++;return go==&nodes[2][missing>=0?missing:0]&&missing>=0?0:go;}
static void set_color(void* mat,Q4 color,void* m){writes++;((Node*)mat)->color=color;}
static void* dispatch(uintptr_t offset){switch(offset){case 0x94f410:return get_renderer;case 0xa1ae90:return get_material;case 0x956610:return set_color;}return 0;}
#define FN(o,t) ((t)dispatch(o))
#include "sleeves_v24.c"
EXPORT void setup(void){for(int i=0;i<9;i++){bodies[i].player=&players[i];bodylive[i]=1;players[i].style=i*9;players[i].tone=i%6;for(int j=0;j<8;j++)nodes[i][j].live=1;}}
EXPORT void run_body(int i){avatar_sleeves_v24(&bodies[i]);}
EXPORT void set_style(int i,int style,int tone){players[i].style=style;players[i].tone=tone;}
EXPORT void set_live(int i,int live){bodylive[i]=live;}
EXPORT void set_missing(int slot){missing=slot;}
EXPORT void kill_visual(int i,int slot){nodes[i][slot].live=0;}
EXPORT int count(int index){return index==0?finds:index==1?reads:writes;}
EXPORT float channel(int i,int slot,int channel){return ((float*)&nodes[i][slot].color)[channel];}
int __stdcall DllMain(void* a,unsigned long b,void* c){return 1;}
