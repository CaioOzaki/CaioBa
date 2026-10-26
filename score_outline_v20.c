/* Include after celebration_v15.c and before identity_v16.c.
 * Call after the existing font assignment in each TMP/UI.Text enable hook.
 * Runtime font replacement would discard a serialized TMP material outline. */
static int v20_score_name(void* text,const char* word){
 if(!text)return 0;int n=INT(text,0x10),i=0;
 for(;word[i];i++)if(i>=n||*(unsigned short*)((char*)text+0x14+2*i)!=(unsigned char)word[i])return 0;
 return i==n;
}
static int v20_is_score(void* component){
 void* t=component?transform(component):0;
 for(int depth=0;t&&depth<12;depth++){
  void* name=FN(0xa0bdd0,void*(*)(void*,void*))(gameobject(t),0);
  if(v20_score_name(name,"Scoreboard")||v20_score_name(name,"CloudBoard0")||v20_score_name(name,"CloudBoard1"))return 1;
  t=FN(0xb739d0,void*(*)(void*,void*))(t,0);
 }return 0;
}
EXPORT void score_outline_tmp_v20(void* text){
 if(!v20_is_score(text))return;
 FN(0x7911d0,void(*)(void*,_Bool,void*))(text,0,0);
 /* Color32 occupies one 32-bit value in the Windows x64 ABI: RGBA 0,0,0,255. */
 FN(0x2402d0,void(*)(void*,unsigned,void*))(text,0xff000000u,0);
 FN(0x240340,void(*)(void*,float,void*))(text,.18f,0);
}
static unsigned v20_outline_type;
static void* v20_get_outline_type(void){
 void* type=rooted(v20_outline_type);if(type)return type;
 void* domain=FN(0x14a920,void*(*)(void))();
 void* assembly=domain?FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI"):0;
 if(!assembly)return 0;void* image=FN(0x14a530,void*(*)(void*))(assembly);
 void* klass=image?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine.UI","Outline"):0;
 if(!klass)return 0;
 type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
 if(type)root_set(&v20_outline_type,type);return type;
}
EXPORT void score_outline_text_v20(void* text){
 if(!v20_is_score(text))return;
 FN(0x7911d0,void(*)(void*,_Bool,void*))(text,0,0);
 void* type=v20_get_outline_type();if(!type)return;void* go=gameobject(text);
 void* outline=FN(0x94f570,void*(*)(void*,void*,void*))(go,type,0);
 if(!outline)outline=FN(0x94f240,void*(*)(void*,void*,void*))(go,type,0);
 if(!outline)return;
 FN(0x83e5a0,void(*)(void*,Q4,void*))(outline,(Q4){0,0,0,1},0);
 FN(0x83e650,void(*)(void*,V2,void*))(outline,(V2){2.5f,2.5f},0);
 FN(0x83e7b0,void(*)(void*,_Bool,void*))(outline,1,0);
}
