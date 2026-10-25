/* Standalone test harness: production helpers are included without modification. */
typedef unsigned long long U64;
extern char __ImageBase;
#ifndef PATCH_DELTA
#define PATCH_DELTA 0x194f000
#endif
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define FLT(o,n) (*(float*)((char*)(o)+(n)))
static U64 base(void){return (U64)&__ImageBase-PATCH_DELTA;}
#define FN(rva,type) ((type)(base()+(rva)))
int DllMain(void* module,unsigned reason,void* reserved){return 1;}
static void* rooted(unsigned root){return root?FN(0x14ac80,void*(*)(unsigned))(root):0;}
static void root_set(unsigned* root,void* obj){
 if(*root)FN(0x14ac70,void(*)(unsigned))(*root);
 *root=obj?FN(0x14ac90,unsigned(*)(void*,_Bool))(obj,0):0;
}
static int alive(void* obj){return obj&&FN(0xa0bfb0,_Bool(*)(void*,void*))(obj,0);}
static void* gameobject(void* c){return FN(0x94b570,void*(*)(void*,void*))(c,0);}
static void* str(const char* s){return FN(0x14b790,void*(*)(const char*))(s);}
#include "input_v19.c"
EXPORT int input_probe(int original){return ui_input_v19(original);}
EXPORT int valid_probe(void* button){return ui_button_valid_v19(button);}
EXPORT void click_probe(void* button){ui_click_v19(button);}
EXPORT int pointer_probe(void){return ui_pointer_over_button_v19();}
