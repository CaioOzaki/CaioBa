/* Reuse the native Settings controller as a modal over the active InGame
 * page. Native pause/menu ownership and each existing game option callback
 * stay intact. Only Game and Sound are available during a live session. */
static int settings_in_match_v30,settings_saved_tab_v30;
static unsigned settings_match_transform_v30;
static void settings_match_layout_v30(void){
 void* page=rooted(settings_page_v28);if(!alive(page))return;
 void* t=transform(page);
 settings_set_active_v28(t,"CC_MatchSettingsBlocker",settings_in_match_v30);
 settings_set_active_v28(t,"CC_SettingsGraphics",!settings_in_match_v30);
 if(settings_in_match_v30){
  settings_set_active_v28(t,"Region Button",0);
  child_label_v19(t,"CC_GameHint","Comfort, controls and audio. Changes apply while you play.");
  child_label_v19(t,"Back Button/Text","BACK TO MATCH MENU");
 }else{
  child_label_v19(t,"CC_GameHint","Comfort, controls, bots and connection.");
  child_label_v19(t,"Back Button/Text","BACK");
 }
}
static void settings_match_close_v30(void){
 if(!settings_in_match_v30)return;
 settings_in_match_v30=0;
 void* t=rooted(settings_match_transform_v30);
 if(alive(t))FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),0,0);
 root_set(&settings_match_transform_v30,0);
 settings_select_v28(settings_saved_tab_v30);
}
static int settings_match_button_v30(void* button){
 if(settings_in_match_v30){
  void* page=rooted(settings_page_v28);
  if(page&&button==PTR(page,0x78)){settings_match_close_v30();return 1;}
  if(named(button,"CC_SettingsGraphics")||named(button,"CC_GraphicsOpen"))return 1;
 }
 if(!named(button,"CC_MatchSettings"))return 0;
 void* menu=menu_transform_v19();void* t=menu?find_child(menu,"Pages/Settings"):0;
 void* ingame=menu?find_child(menu,"Pages/InGame"):0;
 if(!alive(t)||!alive(ingame)||!FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(ingame),0))return 1;
 void* controller=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("SettingsPageController"),0);
 if(!alive(controller))return 1;
 customization_close_v19();refinement_close_v29();graphics_close_v24();
 settings_saved_tab_v30=settings_tab_v28;
 settings_in_match_v30=1;root_set(&settings_match_transform_v30,t);
 /* First activation runs native Awake once, wiring original option events. */
 FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),1,0);
 settings_tab_v28=0;settings_refresh_v28_hook(controller,0);
 void (*last)(void*)=FN(0x14b030,void*(*)(const char*))("UnityEngine.Transform::SetAsLastSibling");
 if(last)last(t);
 FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),1,0);
 return 1;
}
