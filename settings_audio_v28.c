/* Categorized settings and local sound mix. No streaming service or downloads. */
static unsigned settings_page_v28,audio_system_v28;
static int settings_tab_v28,audio_loaded_v28;
static int audio_levels_v28[4]={100,65,100,80}; /* Master, Music, Game, Interface. */
static const char* audio_keys_v28[4]={"Cloudcourt.Volume.Master.v28","Cloudcourt.Volume.Music.v28","Cloudcourt.Volume.Game.v28","Cloudcourt.Volume.UI.v28"};
static void (*audio_master_set_v28)(float);
typedef struct {unsigned source;float base;} AudioEffectV28;
static AudioEffectV28 audio_effects_v28[32];
static unsigned audio_bound_source_v28,audio_bound_clip_v28;
TRAMP(void,audio_music_v28,(void* o,void* name,float fadeout,float fadein,void* m))
TRAMP(void,audio_music_now_v28,(void* o,void* name,void* m))
TRAMP(void,audio_stop_v28,(void* o,void* m))
TRAMP(void,audio_options_v28,(void* o,void* m))
TRAMP(void,audio_update_v28,(void* o,void* m))
TRAMP(void*,audio_effect_v28,(void* o,void* clip,V3* position,void* effect,void* group,float delay,void* m))
TRAMP(void,settings_refresh_v28,(void* o,void* m))
static void audio_preferences_v28(void){
 if(audio_loaded_v28)return;audio_loaded_v28=1;
 for(int i=0;i<4;i++){
  int n=FN(0xa12690,int(*)(void*,int,void*))(str(audio_keys_v28[i]),audio_levels_v28[i],0);
  audio_levels_v28[i]=n<0?0:n>100?100:n;
 }
 audio_master_set_v28=FN(0x14b030,void*(*)(const char*))("UnityEngine.AudioListener::set_volume");
 if(audio_master_set_v28)audio_master_set_v28(audio_levels_v28[0]/100.f);
}
static float audio_gain_v28(int category){audio_preferences_v28();return category>=0&&category<4?audio_levels_v28[category]/100.f:1.f;}
static void audio_playlist_v28(void* o,int refresh){
 if(!o)return;audio_preferences_v28();if(rooted(audio_system_v28)!=o)root_set(&audio_system_v28,o);
 void* source=PTR(o,0x58),*secondary=PTR(o,0x60),*entries=PTR(o,0x18);
 void* array=entries?PTR(entries,0x10):0;
 void* entry=array&&INT(entries,0x18)>0?PTR(array,0x20):0;
 void* clip=entry?PTR(entry,0x18):0;
 if(!alive(source)||!alive(clip))return;
 if(rooted(audio_bound_source_v28)!=source||rooted(audio_bound_clip_v28)!=clip){
  FN(0xebc2d0,void(*)(void*,void*,void*))(source,clip,0);
  FN(0xebc370,void(*)(void*,_Bool,void*))(source,1,0);
  FN(0xebc590,void(*)(void*,float,void*))(source,0,0);
  FN(0xebbe30,void(*)(void*,void*))(source,0);
  root_set(&audio_bound_source_v28,source);root_set(&audio_bound_clip_v28,clip);
  managed_field(o,0x50,entry);refresh=1;
  if(alive(secondary)){FN(0xebc000,void(*)(void*,void*))(secondary,0);FN(0xebc760,void(*)(void*,float,void*))(secondary,0,0);}
 }
 if(refresh){
  float level=FN(0xef33f0,_Bool(*)(void*))(0)?audio_levels_v28[1]/100.f:0;
  FLT(o,0x80)=level;
  FN(0xebc760,void(*)(void*,float,void*))(source,level,0);
 }
}
static void audio_apply_v28(void){
 audio_preferences_v28();
 if(audio_master_set_v28)audio_master_set_v28(audio_levels_v28[0]/100.f);
 audio_playlist_v28(rooted(audio_system_v28),1);
 for(int i=0;i<32;i++){
  void* s=rooted(audio_effects_v28[i].source);
  if(alive(s))FN(0xebc760,void(*)(void*,float,void*))(s,audio_effects_v28[i].base*audio_levels_v28[2]/100.f,0);
  else root_set(&audio_effects_v28[i].source,0);
 }
 void* ui=rooted(ui_v19_click_source),*whistle=rooted(serve_whistle_source_v21);
 if(alive(ui))FN(0xebc760,void(*)(void*,float,void*))(ui,.55f*audio_levels_v28[3]/100.f,0);
 if(alive(whistle))FN(0xebc760,void(*)(void*,float,void*))(whistle,.32f*audio_levels_v28[2]/100.f,0);
}
EXPORT void audio_music_v28_hook(void* o,void* name,float a,float b,void* m){audio_playlist_v28(o,1);}
EXPORT void audio_music_now_v28_hook(void* o,void* name,void* m){audio_playlist_v28(o,1);}
EXPORT void audio_stop_v28_hook(void* o,void* m){audio_playlist_v28(o,1);}
EXPORT void audio_options_v28_hook(void* o,void* m){audio_playlist_v28(o,1);}
EXPORT void audio_update_v28_hook(void* o,void* m){
 audio_playlist_v28(o,0);
 if(o&&BYTE(o,0xc4))FN(0x26d470,void(*)(void*,void*))(o,0);
}
EXPORT void* audio_effect_v28_hook(void* o,void* clip,V3* pos,void* effect,void* group,float delay,void* m){
 void* s=audio_effect_v28_trampoline(o,clip,pos,effect,group,delay,m);if(!alive(s))return s;
 float v=FN(0xebc290,float(*)(void*,void*))(s,0);if(!__builtin_isfinite(v))v=1;
 int slot=-1;
 for(int i=0;i<32;i++)if(rooted(audio_effects_v28[i].source)==s){slot=i;break;}
 if(slot<0)for(int i=0;i<32;i++)if(!alive(rooted(audio_effects_v28[i].source))){slot=i;break;}
 if(slot>=0){root_set(&audio_effects_v28[slot].source,s);audio_effects_v28[slot].base=v;}
 FN(0xebc760,void(*)(void*,float,void*))(s,v*audio_gain_v28(2),0);return s;
}
static void settings_set_active_v28(void* root,const char* path,int state){
 void* t=find_child(root,path);if(t)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),state!=0,0);
}
static void settings_refresh_labels_v28(void){
 void* page=rooted(settings_page_v28);if(!alive(page))return;
 static const char* name[4]={"MASTER VOLUME","MUSIC VOLUME","GAME SOUNDS","INTERFACE SOUNDS"};
 static const char* path[4]={"CC_VolumeMasterValue","CC_VolumeMusicValue","CC_VolumeGameValue","CC_VolumeUIValue"};
 for(int i=0;i<4;i++){
  char text[64];int n=0;for(const char* p=name[i];*p;p++)text[n++]=*p;
  text[n++]=' ';text[n++]=' ';
  int v=audio_levels_v28[i];if(v>=100)text[n++]='1';if(v>=10)text[n++]=(char)('0'+v/10%10);text[n++]=(char)('0'+v%10);text[n++]='%';text[n]=0;
  void* controls=find_child(transform(page),"CC_AudioControls");
  if(controls)child_label_v19(controls,path[i],text);
 }
 const char* names[3]={"CC_SettingsGame/Text","CC_SettingsGraphics/Text","CC_SettingsAudio/Text"};
 const char* texts[3]={"GAME","GRAPHICS","SOUND"};const char* chosen[3]={"[ GAME ]","[ GRAPHICS ]","[ SOUND ]"};
 for(int i=0;i<3;i++)child_label_v19(transform(page),names[i],settings_tab_v28==i?chosen[i]:texts[i]);
}
static void settings_select_v28(int tab){
 if(tab<0||tab>2)tab=0;settings_tab_v28=tab;
 void* page=rooted(settings_page_v28);if(!alive(page))return;void* t=transform(page);
 const char* game[]={"Movement Button","Jump Button","Jump Height Button","Snap Turn Button","Front Row Only Button","Aim Assist Button","Friend Bot Pro Button","Opponent Bot Pro Button","Movement Speed Slider","Region Button","CC_GameHint"};
 for(int i=0;i<11;i++)settings_set_active_v28(t,game[i],tab==0);
 const char* graphics[]={"CC_GraphicsOpen","CC_GraphicsSummary","CC_GraphicsWarning"};
 for(int i=0;i<3;i++)settings_set_active_v28(t,graphics[i],tab==1);
 settings_set_active_v28(t,"CC_AudioControls",tab==2);
 settings_set_active_v28(t,"Music Button",tab==2);
 settings_refresh_labels_v28();graphics_refresh_v24();
}
static void settings_close_v28(void){graphics_close_v24();}
EXPORT void settings_refresh_v28_hook(void* o,void* m){
 settings_refresh_v28_trampoline(o,m);root_set(&settings_page_v28,o);audio_preferences_v28();settings_select_v28(settings_tab_v28);
}
static int settings_button_v28(void* button){
 int tab=named(button,"CC_SettingsGame")?0:named(button,"CC_SettingsGraphics")?1:named(button,"CC_SettingsAudio")?2:-1;
 if(tab>=0){settings_select_v28(tab);return 1;}
 const char* minus[4]={"CC_VolumeMasterMinus","CC_VolumeMusicMinus","CC_VolumeGameMinus","CC_VolumeUIMinus"};
 const char* plus[4]={"CC_VolumeMasterPlus","CC_VolumeMusicPlus","CC_VolumeGamePlus","CC_VolumeUIPlus"};
 for(int i=0;i<4;i++){
  int delta=named(button,minus[i])?-10:named(button,plus[i])?10:0;if(!delta)continue;
  audio_preferences_v28();int v=audio_levels_v28[i]+delta;audio_levels_v28[i]=v<0?0:v>100?100:v;
  FN(0xa12870,void(*)(void*,int,void*))(str(audio_keys_v28[i]),audio_levels_v28[i],0);
  graphics_resolve_v24();if(graphics_save_v24)graphics_save_v24();audio_apply_v28();settings_refresh_labels_v28();return 1;
 }
 return 0;
}
