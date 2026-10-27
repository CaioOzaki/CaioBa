/* Independent face/outfit preferences and a single modal over the current page.
 * Opening this panel never re-enters a game page or rebuilds a match. */
static unsigned custom_overlay;
static const char* face_names_v19[9]={"Cool","Nerd","Smirk","Goofy","Crying","Surprised","Gigachad","Glam","Pleading"};
static const char* outfit_names_v19[9]={"Black Tank","White Tank","Black Suit","White Suit","White Tee","Black Tee","Blue Tee","Forest Tee","Wine Tee"};
static void ensure_preferences_v19(void){
 if(preferences_loaded)return;preferences_loaded=1;
 int old=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Skin"),0,0);
 if(old<0||old>3)old=0;
 int face=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Face"),old,0);
 int outfit=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Outfit"),2,0);
 if(face<0||face>=9)face=old;if(outfit<0||outfit>=9)outfit=2;
 preferred_skin=face+9*outfit;
 preferred_hand_tone_v21=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.HandTone.v21"),0,0);
 if(preferred_hand_tone_v21<0||preferred_hand_tone_v21>=6)preferred_hand_tone_v21=0;
 preferred_map=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Map"),0,0)==1;
}
static int preferred_style(void){ensure_preferences_v19();return preferred_skin;}
EXPORT int avatar_style_v19(void* player){return player_skin(player);}
static void* menu_transform_v19(void){
 void* go=FN(0x94f3d0,void*(*)(void*,void*))(str("Menu"),0);
 return go?FN(0x94fb00,void*(*)(void*,void*))(go,0):0;
}
static void* customization_panel_v19(void){
 if(!alive(rooted(custom_overlay))){void* root=menu_transform_v19();root_set(&custom_overlay,find_child(root,"CC_Customization"));}
 return rooted(custom_overlay);
}
static void child_label_v19(void* root,const char* path,const char* text){
 void* t=find_child(root,path);if(!t)return;
 void* label_component=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("Text"),0);
 label(label_component,text);
}
static void map_label_v19(void){
 ensure_preferences_v19();void* t=menu_transform_v19();if(t)child_label_v19(t,"Pages/Online/CC_MapLabel",preferred_map?"Beach":"Indoor");
}
static void customization_refresh_v19(void){
 void* panel=customization_panel_v19();if(!panel)return;int style=preferred_style();
 child_label_v19(panel,"CC_FaceLabel",face_names_v19[style%9]);
 child_label_v19(panel,"CC_OutfitLabel",outfit_names_v19[style/9]);
 child_label_v19(panel,"CC_HandToneLabel",hand_tone_names_v21[preferred_hand_tone_v21]);
 for(int i=0;i<2;i++){
  void* t=find_child(panel,i?"CC_OutfitPreview":"CC_FacePreview");
  void* raw=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("RawImage"),0):0;if(!raw)continue;
  int index=i?style/9:style%9;float scale=i?1/6.f:1/3.f;
  FN(0x832190,void(*)(void*,Q4,void*))(raw,(Q4){(index%3)/3.f,(2-index/3)/3.f,scale,scale},0);
  /* Graphic.set_color (verified separately); the texture is serialized. */
  FN(0x7910f0,void(*)(void*,Q4,void*))(raw,(Q4){1,1,1,1},0);
  /* RawImage dirties its own vertices, but CurvedUI caches UVs in the
   * tesselated and curved vertex lists. Invalidate that cache on every click.
   * Verified dump.cs: CurvedUIVertexEffect.SetDirty RVA 0x24bb80. */
  void* effect=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("CurvedUIVertexEffect"),0);
  if(effect)FN(0x24bb80,void(*)(void*,void*))(effect,0);
  FN(0x790530,void(*)(void*,void*))(raw,0);
 }
 void* swatch=find_child(panel,"CC_HandToneSwatch");
 void* graphic=swatch?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(swatch),str("Image"),0):0;
 if(graphic)FN(0x7910f0,void(*)(void*,Q4,void*))(graphic,hand_tone_colors_v21[preferred_hand_tone_v21],0);
}
static void customization_close_v19(void){
 void* panel=rooted(custom_overlay);if(alive(panel))FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),0,0);
}
static int customization_button_v19(void* button){
 if(named(button,"CC_CustomizeOpen")){
  graphics_close_v24();
  void* panel=customization_panel_v19();if(panel){customization_refresh_v19();FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);}return 1;
 }
 if(named(button,"CC_CustomizeBack")){customization_close_v19();return 1;}
 if(named(button,"CC_MapPrev")||named(button,"CC_MapNext")){
  ensure_preferences_v19();preferred_map^=1;FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Map"),preferred_map,0);map_label_v19();return 1;
 }
 int face_delta=named(button,"CC_FaceNext")?1:named(button,"CC_FacePrev")?-1:0;
 int outfit_delta=named(button,"CC_OutfitNext")?1:named(button,"CC_OutfitPrev")?-1:0;
 int tone_delta=named(button,"CC_HandToneNext")?1:named(button,"CC_HandTonePrev")?-1:0;
 if(!face_delta&&!outfit_delta&&!tone_delta)return 0;
 ensure_preferences_v19();
 if(tone_delta){preferred_hand_tone_v21=(preferred_hand_tone_v21+tone_delta+6)%6;
  FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.HandTone.v21"),preferred_hand_tone_v21,0);}
 int style=preferred_style(),face=(style%9+face_delta+9)%9,outfit=(style/9+outfit_delta+9)%9;
 preferred_skin=face+9*outfit;
 FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Face"),face,0);
 FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Outfit"),outfit,0);
 select_appearance(-1,0);customization_refresh_v19();return 1;
}
