/* Isolated input predicate fixture; includes the production helper unchanged. */
typedef unsigned long long U64;
extern char __ImageBase;
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define BYTE(o,n) (*(unsigned char*)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
static U64 base(void){return (U64)&__ImageBase-0x194f000;}
#define FN(rva,type) ((type)(base()+(rva)))
int DllMain(void* module,unsigned reason,void* reserved){return 1;}
static void* rooted(unsigned root){return root?FN(0x14ac80,void*(*)(unsigned))(root):0;}
static void root_set(unsigned* root,void* obj){
 if(*root)FN(0x14ac70,void(*)(unsigned))(*root);
 *root=obj?FN(0x14ac90,unsigned(*)(void*,_Bool))(obj,0):0;
}
static int fixture_offline=1,fixture_network,fixture_original,fixture_original_calls;
static void* fixture_local_player;
static int offline(void){return fixture_offline;}
static int network_physics(void){return fixture_network;}
static void* online_local_player(void){return fixture_local_player;}
static void* transform(void* o){return o;}
#define TRAMP(ret,name,args) static ret name##_trampoline args {fixture_original_calls++;return fixture_original;}
#include "spawn_input_v24.c"
EXPORT int pressure_probe(void* hand){return spawn_trigger_v24(hand);}
EXPORT void fixture_mode(int offline_value,int network_value,int original_value,void* player){
 fixture_offline=offline_value;fixture_network=network_value;
 fixture_original=original_value;fixture_local_player=player;
}
EXPORT int original_calls(void){return fixture_original_calls;}
