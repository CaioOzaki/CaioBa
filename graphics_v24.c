/* Local rendering preferences only. Never SetQualityLevel: that also changes
 * skinning, particle raycast budgets and frame scheduling in this Unity build.
 * The stripped setters below are resolved by their original Unity icall names;
 * every pointer and value is verified by the disposable Unity runtime probe. */
typedef struct {
 int aa,texture,aniso,shadows,shadow_resolution,soft_particles,reflections;
 float scale,shadow_distance,lod;
} GraphicsPresetV24;
static const GraphicsPresetV24 graphics_presets_v24[4]={
 {0,1,0,0,0,0,0,.70f,15.f,.60f},
 {2,0,1,1,0,0,0,.85f,30.f,1.f},
 {4,0,2,2,1,1,1,.95f,60.f,1.4f},
 {4,0,2,2,2,1,1,1.f,150.f,2.f}
};
static const char* graphics_names_v24[4]={"LOW","MEDIUM","HIGH","ULTRA"};
static const char* graphics_details_v24[4]={
 "70% render scale | No MSAA\nHalf textures | Shadows off | Light effects",
 "85% render scale | 2x MSAA\nFull textures | Hard shadows, 30 m | Light effects",
 "95% render scale | 4x MSAA\nFull textures | Soft shadows, 60 m | Full effects",
 "100% render scale | 4x MSAA\nFull textures | Soft shadows, 150 m | Full effects"
};
static int graphics_loaded_v24,graphics_selected_v24=3,graphics_api_checked_v24;
static unsigned graphics_overlay_v24;
static void (*graphics_texture_v24)(int),(*graphics_aniso_v24)(int),(*graphics_shadows_v24)(int);
static void (*graphics_shadow_resolution_v24)(int),(*graphics_particles_v24)(_Bool),(*graphics_reflections_v24)(_Bool);
static void (*graphics_shadow_distance_v24)(float),(*graphics_lod_v24)(float);
static void (*graphics_save_v24)(void);
static void graphics_resolve_v24(void){
 if(graphics_api_checked_v24)return;graphics_api_checked_v24=1;
 graphics_texture_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_masterTextureLimit");
 graphics_aniso_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_anisotropicFiltering");
 graphics_shadows_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_shadows");
 graphics_shadow_resolution_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_shadowResolution");
 graphics_shadow_distance_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_shadowDistance");
 graphics_lod_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_lodBias");
 graphics_particles_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_softParticles");
 graphics_reflections_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.QualitySettings::set_realtimeReflectionProbes");
 graphics_save_v24=FN(0x14b030,void*(*)(const char*))("UnityEngine.PlayerPrefs::Save");
}
static void* graphics_panel_v24(void){
 if(!alive(rooted(graphics_overlay_v24))){void* menu=menu_transform_v19();root_set(&graphics_overlay_v24,find_child(menu,"CC_Graphics"));}
 return rooted(graphics_overlay_v24);
}
static void graphics_refresh_v24(void){
 void* menu=menu_transform_v19();void* panel=graphics_panel_v24();
 const char* buttons[4]={"CC_GraphicsLow/Text","CC_GraphicsMedium/Text","CC_GraphicsHigh/Text","CC_GraphicsUltra/Text"};
 const char* selected[4]={"[ LOW ]","[ MEDIUM ]","[ HIGH ]","[ ULTRA ]"};
 const char* settings[4]={"GRAPHICS: LOW","GRAPHICS: MEDIUM","GRAPHICS: HIGH","GRAPHICS: ULTRA"};
 if(menu)child_label_v19(menu,"Pages/Settings/CC_GraphicsOpen/Text",settings[graphics_selected_v24]);
 if(!panel)return;
 child_label_v19(panel,"CC_GraphicsDetails",graphics_details_v24[graphics_selected_v24]);
 for(int i=0;i<4;i++)child_label_v19(panel,buttons[i],i==graphics_selected_v24?selected[i]:graphics_names_v24[i]);
}
static void graphics_apply_v24(int index){
 if(index<0||index>3)index=3;
 graphics_selected_v24=index;graphics_resolve_v24();
 const GraphicsPresetV24* p=&graphics_presets_v24[index];
 FN(0xa12bf0,void(*)(int,void*))(p->aa,0);
 FN(0xed8cf0,void(*)(float,void*))(p->scale,0);
 if(graphics_texture_v24)graphics_texture_v24(p->texture);
 if(graphics_aniso_v24)graphics_aniso_v24(p->aniso);
 if(graphics_shadows_v24)graphics_shadows_v24(p->shadows);
 if(graphics_shadow_resolution_v24)graphics_shadow_resolution_v24(p->shadow_resolution);
 if(graphics_shadow_distance_v24)graphics_shadow_distance_v24(p->shadow_distance);
 if(graphics_lod_v24)graphics_lod_v24(p->lod);
 if(graphics_particles_v24)graphics_particles_v24(p->soft_particles!=0);
 if(graphics_reflections_v24)graphics_reflections_v24(p->reflections!=0);
}
static void graphics_start_v24(void){
 if(!graphics_loaded_v24){
  graphics_loaded_v24=1;
  int selected=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),3,0);
  graphics_apply_v24(selected);
 }
 graphics_refresh_v24();
}
static void graphics_close_v24(void){
 void* panel=rooted(graphics_overlay_v24);
 if(alive(panel))FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),0,0);
}
static int graphics_button_v24(void* button){
 if(named(button,"CC_GraphicsOpen")){
  graphics_start_v24();customization_close_v19();void* panel=graphics_panel_v24();
  if(panel)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);
  return 1;
 }
 if(named(button,"CC_GraphicsBack")){graphics_close_v24();return 1;}
 int index=named(button,"CC_GraphicsLow")?0:named(button,"CC_GraphicsMedium")?1:
           named(button,"CC_GraphicsHigh")?2:named(button,"CC_GraphicsUltra")?3:-1;
 if(index<0)return 0;
 graphics_loaded_v24=1;graphics_apply_v24(index);
 FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),index,0);
 if(graphics_save_v24)graphics_save_v24();
 graphics_refresh_v24();return 1;
}
/* Preserve AdaptiveGraphics' original event subscriptions and lifecycle,
 * then apply the preset after its old three-step resolution setter.
 * Verified dump.cs RVAs: Start 2641D0 / ApplyResolutionScale 264080. */
TRAMP(void,graphics_adaptive_start,(void* o,void* m))
TRAMP(void,graphics_adaptive_apply,(void* o,void* m))
EXPORT void graphics_adaptive_start_hook(void* o,void* m){
 graphics_adaptive_start_trampoline(o,m);
 if(!graphics_loaded_v24)graphics_start_v24();else graphics_apply_v24(graphics_selected_v24);
}
EXPORT void graphics_adaptive_apply_hook(void* o,void* m){
 /* Exact original body 264080..2640CC only reads resolutionScaleStep and
  * sets XR scale. It has no events or other side effects to preserve.
  * Avoid allocating old-scale eye buffers immediately before new-scale ones. */
 if(!graphics_loaded_v24)graphics_start_v24();
 else FN(0xed8cf0,void(*)(float,void*))(graphics_presets_v24[graphics_selected_v24].scale,0);
}
/* OVRManager.Update (457FD0) can override both knobs every frame. These are
 * rendering-only fields: useRecommendedMSAALevel +25 and
 * enableAdaptiveResolution +27. Exact checks: 458501 / 459524. No per-frame
 * polling, searches, or render allocations. Original tracking/input is intact. */
TRAMP(void,graphics_ovr_update,(void* o,void* m))
EXPORT void graphics_ovr_update_hook(void* o,void* m){
 if(o&&graphics_loaded_v24){BYTE(o,0x25)=0;BYTE(o,0x27)=0;}
 graphics_ovr_update_trampoline(o,m);
}
