/* v28 companion cosmetic message; face/outfit/tone wire stays v21. */
static int preferred_hat_v28,preferred_transparent_arms_v28;
#ifdef MODE_PROBE
EXPORT int customization_stats_v28[12];
#define CUSTOM_STAT_V28(statement) statement
#else
#define CUSTOM_STAT_V28(statement) ((void)0)
#endif
static const char* hat_names_v28[8]={"None","Cap","Fedora","Cowboy","Motorcycle Helmet","Beanie","Crown","Visor"};
static const char* hat_paths_v28[7]={"CC_Hat_Cap","CC_Hat_Fedora","CC_Hat_Cowboy","CC_Hat_MotorcycleHelmet","CC_Hat_Beanie","CC_Hat_Crown","CC_Hat_Visor"};
typedef struct {unsigned player;int hat,arms;} CosmeticChoiceV28;
static CosmeticChoiceV28 cosmetics_v28[8];
EXPORT int appearance_encode_v28(int hat,int arms){return hat>=0&&hat<8&&arms>=0&&arms<2?(int)(0x5c280000u|(unsigned)hat|((unsigned)arms<<4)):-1;}
EXPORT int appearance_decode_v28(int value,int* hat,int* arms){
 if(((unsigned)value&0xffff0000u)!=0x5c280000u)return 0;
 if(((unsigned)value&0xffe8u)!=0)return -1;
 *hat=value&7;*arms=(value>>4)&1;return 1;
}
static int appearance_pack_v28(void){return appearance_encode_v28(preferred_hat_v28,preferred_transparent_arms_v28);}
static int appearance_receive_v28(void* player,int value){
 int hat=0,arms=0,result=appearance_decode_v28(value,&hat,&arms);if(!result)return 0;if(result<0||!player)return 1;
 for(int i=0;i<8;i++)if(rooted(cosmetics_v28[i].player)==player||!alive(rooted(cosmetics_v28[i].player))){root_set(&cosmetics_v28[i].player,player);cosmetics_v28[i].hat=hat;cosmetics_v28[i].arms=arms;break;}return 1;
}
static int player_cosmetic_v28(void* player,int arms){
 if(player&&player==local_avatar_player())return arms?preferred_transparent_arms_v28:preferred_hat_v28;
 for(int i=0;i<8;i++)if(rooted(cosmetics_v28[i].player)==player)return arms?cosmetics_v28[i].arms:cosmetics_v28[i].hat;
 return 0;
}
static void customization_preferences_v28(void){
 preferred_hat_v28=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Hat.v28"),0,0);
 preferred_transparent_arms_v28=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.TransparentArms.v28"),0,0);
 if(preferred_hat_v28<0||preferred_hat_v28>=8)preferred_hat_v28=0;
 preferred_transparent_arms_v28=preferred_transparent_arms_v28==1;
}
/* Only Renderer.enabled changes: tracking, collider and IK stay active. */
typedef struct {unsigned body,head,hats[7],arms[4],materials[4],shared[4];int hat,transparent,outfit;} CosmeticBodyV28;
static CosmeticBodyV28 cosmetic_bodies_v28[8];
static void cosmetic_body_release_v28(CosmeticBodyV28* s){
 for(int i=0;i<4;i++){
  void* r=rooted(s->arms[i]),*shared=rooted(s->shared[i]),*mat=rooted(s->materials[i]);
  if(alive(r)&&alive(shared))FN(0xa1b0e0,void(*)(void*,void*,void*))(r,shared,0);
  if(alive(mat)&&mat!=shared)FN(0xa0ab40,void(*)(void*,void*))(mat,0);
  root_set(&s->arms[i],0);root_set(&s->materials[i],0);root_set(&s->shared[i],0);
 }
 for(int i=0;i<7;i++)root_set(&s->hats[i],0);
 root_set(&s->body,0);root_set(&s->head,0);s->hat=s->transparent=s->outfit=-1;
}
static void customization_mirror_tick_v28(void* body);
EXPORT void avatar_cosmetics_v28(void* body){
 void* player=body?PTR(body,0x168):0;if(!player)return;
 CosmeticBodyV28* s=0;for(int i=0;i<8;i++)if(rooted(cosmetic_bodies_v28[i].body)==body){s=&cosmetic_bodies_v28[i];break;}
 if(!s)for(int i=0;i<8;i++)if(!alive(rooted(cosmetic_bodies_v28[i].body))){s=&cosmetic_bodies_v28[i];break;}if(!s)return;
 if(rooted(s->body)!=body){cosmetic_body_release_v28(s);root_set(&s->body,body);root_set(&s->head,0);s->hat=s->transparent=s->outfit=-1;for(int i=0;i<7;i++)root_set(&s->hats[i],0);for(int i=0;i<4;i++){root_set(&s->arms[i],0);root_set(&s->materials[i],0);}if(player!=local_avatar_player())select_appearance(-1,0);}
 int hat=player_cosmetic_v28(player,0),transparent=player_cosmetic_v28(player,1),style=player_skin(player),outfit=style>=0&&style<81?style/9:2,ready=1;
 if(!alive(rooted(s->head)))root_set(&s->head,find_child(transform(body),"Physical Head/Visual Head Root/Head"));
 for(int i=0;i<7;i++){int rebound=0;if(!alive(rooted(s->hats[i]))){root_set(&s->hats[i],find_child(rooted(s->head),hat_paths_v28[i]));rebound=1;}
  void* t=rooted(s->hats[i]);if(!t){ready=0;continue;}if(s->hat!=hat||rebound)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),hat==i+1,0);}
 const char* paths[4]={"Physical Upper Arm L","Physical Lower Arm L","Physical Upper Arm R","Physical Lower Arm R"};
 for(int i=0;i<4;i++){int rebound=0;if(!alive(rooted(s->arms[i]))){void* t=find_child(transform(body),paths[i]);root_set(&s->arms[i],t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0);root_set(&s->materials[i],0);rebound=1;}
  void* r=rooted(s->arms[i]);if(!r){ready=0;continue;}if(s->transparent!=transparent||rebound)FN(0xa1b2f0,void(*)(void*,_Bool,void*))(r,!transparent,0);
  if(!alive(rooted(s->materials[i]))){root_set(&s->shared[i],FN(0xa1af10,void*(*)(void*,void*))(r,0));root_set(&s->materials[i],FN(0xa1ae90,void*(*)(void*,void*))(r,0));rebound=1;}
  void* mat=rooted(s->materials[i]);if(!mat){ready=0;continue;}if(s->outfit!=outfit||rebound)FN(0x956610,void(*)(void*,Q4,void*))(mat,sleeve_outfit_colors_v24[outfit],0);
 }
 s->hat=ready?hat:-1;s->transparent=ready?transparent:-1;s->outfit=ready?outfit:-1;
 customization_mirror_tick_v28(body);
}
/* Same actual avatar meshes, independent material instances, no second camera,
 * RenderTexture, scripts, physics or per-frame allocation. */
typedef struct {unsigned renderer,shared,material;} MirrorMaterialV28;
static MirrorMaterialV28 mirror_materials_v28[8];
static unsigned mirror_panel_v28;
static void mirror_materials_release_v28(void){
 for(int i=0;i<8;i++){
  MirrorMaterialV28* s=&mirror_materials_v28[i];void* r=rooted(s->renderer),*shared=rooted(s->shared),*mat=rooted(s->material);
  if(alive(r)&&alive(shared))FN(0xa1b0e0,void(*)(void*,void*,void*))(r,shared,0);
  if(alive(mat)&&mat!=shared)FN(0xa0ab40,void(*)(void*,void*))(mat,0);
  root_set(&s->renderer,0);root_set(&s->shared,0);root_set(&s->material,0);
 }
}
static void* mirror_material_v28(void* renderer,int index){
 MirrorMaterialV28* s=&mirror_materials_v28[index];
 if(rooted(s->renderer)!=renderer||!alive(rooted(s->material))){
  void* old=rooted(s->material),*shared=rooted(s->shared),*r=rooted(s->renderer);
  if(alive(r)&&alive(shared))FN(0xa1b0e0,void(*)(void*,void*,void*))(r,shared,0);
  if(alive(old)&&old!=shared)FN(0xa0ab40,void(*)(void*,void*))(old,0);
  root_set(&s->renderer,renderer);root_set(&s->shared,renderer?FN(0xa1af10,void*(*)(void*,void*))(renderer,0):0);
  root_set(&s->material,renderer?FN(0xa1ae90,void*(*)(void*,void*))(renderer,0):0);
 }
 if(alive(rooted(s->material)))FN(0x956900,void(*)(void*,int,void*))(rooted(s->material),4001,0);
 return rooted(s->material);
}
/* These inactive, serialized UI references retain the original atlases across
 * match/scene resets. Mutable renderer instances may have null/reward textures
 * after the native lifecycle, so they are never the authoritative base source. */
static void* customization_base_texture_v30(void* panel,int part){
 void* t=panel?find_child(panel,part?"CC_OutfitPreview":"CC_FacePreview"):0;
 void* raw=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("RawImage"),0):0;
 void* tex=raw?FN(0x223290,void*(*)(void*,void*))(raw,0):0;return alive(tex)?tex:0;
}
static void customization_mirror_refresh_v28(void* panel){
 if(rooted(mirror_panel_v28)!=panel){mirror_materials_release_v28();root_set(&mirror_panel_v28,panel);}
 int style=preferred_style();CUSTOM_STAT_V28(customization_stats_v28[0]++;customization_stats_v28[1]=style;customization_stats_v28[2]=preferred_hat_v28;customization_stats_v28[3]=preferred_transparent_arms_v28;customization_stats_v28[4]=0);const char* parts[2]={"CC_MirrorHead","CC_MirrorBody"};
 for(int i=0;i<2;i++){void* t=find_child(panel,parts[i]);void* r=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;void* mat=mirror_material_v28(r,i);
  if(mat){void* base_tex=customization_base_texture_v30(panel,i);if(base_tex)FN(0x956850,void(*)(void*,void*,void*))(mat,base_tex,0);FN(0x956790,void(*)(void*,V2,void*))(mat,(V2){1,1},0);int index=i?style/9:style%9;FN(0x9566d0,void(*)(void*,V2,void*))(mat,(V2){(index%3)/3.f,(2-index/3)/3.f},0);FN(0x956610,void(*)(void*,Q4,void*))(mat,(Q4){1,1,1,1},0);}
  if(!i)for(int h=0;h<7;h++){void* child=find_child(t,hat_paths_v28[h]);if(child)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(child),preferred_hat_v28==h+1,0);}
 }
 const char* arms[4]={"CC_MirrorUpperL","CC_MirrorLowerL","CC_MirrorUpperR","CC_MirrorLowerR"};
 for(int i=0;i<4;i++){void* t=find_child(panel,arms[i]);void* r=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;if(!r)continue;FN(0xa1b2f0,void(*)(void*,_Bool,void*))(r,!preferred_transparent_arms_v28,0);void* mat=mirror_material_v28(r,i+2);if(mat)FN(0x956610,void(*)(void*,Q4,void*))(mat,sleeve_outfit_colors_v24[style/9],0);}
 const char* hands[2]={"CC_MirrorHandL","CC_MirrorHandR"};
 for(int i=0;i<2;i++){void* t=find_child(panel,hands[i]);void* r=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;void* mat=mirror_material_v28(r,i+6);if(mat)FN(0x956610,void(*)(void*,Q4,void*))(mat,hand_tone_colors_v21[preferred_hand_tone_v21],0);}
 CUSTOM_STAT_V28(for(int i=0;i<8;i++)if(alive(rooted(mirror_materials_v28[i].material)))customization_stats_v28[4]|=1<<i);
 child_label_v19(panel,"CC_HatLabel",hat_names_v28[preferred_hat_v28]);
 child_label_v19(panel,"CC_ArmsLabel",preferred_transparent_arms_v28?"Transparent":"Outfit Color");
}
static unsigned mirror_head_v28,mirror_source_v28,mirror_body_v28,mirror_head_panel_v28;
static void customization_reset_v28(void){
 sleeves_reset_v28();
 for(int i=0;i<8;i++){cosmetic_body_release_v28(&cosmetic_bodies_v28[i]);root_set(&cosmetics_v28[i].player,0);}
 mirror_materials_release_v28();root_set(&mirror_panel_v28,0);root_set(&mirror_head_panel_v28,0);root_set(&mirror_head_v28,0);root_set(&mirror_source_v28,0);root_set(&mirror_body_v28,0);
}
static void customization_mirror_tick_v28(void* body){
 void* player=body?PTR(body,0x168):0;if(player!=local_avatar_player())return;
 void* panel=rooted(custom_overlay);if(!alive(panel)||!FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0))return;
 if(rooted(mirror_body_v28)!=body){root_set(&mirror_body_v28,body);root_set(&mirror_source_v28,0);}
 if(rooted(mirror_head_panel_v28)!=panel){root_set(&mirror_head_panel_v28,panel);root_set(&mirror_head_v28,0);}
 if(!alive(rooted(mirror_head_v28)))root_set(&mirror_head_v28,find_child(panel,"CC_MirrorHead"));
 if(!alive(rooted(mirror_source_v28)))root_set(&mirror_source_v28,PTR(body,0x30));
 void* head=rooted(mirror_head_v28),*source=rooted(mirror_source_v28);if(!head||!source)return;
 Q4 q=FN(0xb74b50,Q4(*)(void*,void*))(source,0);
 CUSTOM_STAT_V28(customization_stats_v28[5]++);
 FN(0xb754c0,void(*)(void*,Q4,void*))(head,(Q4){-q.z,q.w,-q.x,q.y},0);
}
static int customization_button_v28(void* button){
 int d=named(button,"CC_HatNext")?1:named(button,"CC_HatPrev")?-1:0;
 int arms=named(button,"CC_ArmsNext")||named(button,"CC_ArmsPrev");if(!d&&!arms)return 0;
 ensure_preferences_v19();if(d)preferred_hat_v28=(preferred_hat_v28+d+8)%8;if(arms)preferred_transparent_arms_v28^=1;
 FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Hat.v28"),preferred_hat_v28,0);
 FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.TransparentArms.v28"),preferred_transparent_arms_v28,0);
 select_appearance(-1,0);customization_refresh_v19();return 1;
}



#ifdef MODE_PROBE
/* Root's existing probe dispatcher may call this on its game-thread tick.
 * 1=open,2=close,3=face,4=outfit,5=hands,6=hat,7=arms,8=Done,9=snapshot.
 * This deliberately uses the real customization callbacks and installed nodes. */
static int customization_probe_v28(int command){
 void* panel=customization_panel_v19();if(!panel)return 0;
 if(command==1){customization_refresh_v19();FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);}
 else if(command==2)customization_close_v19();
 else if(command>=3&&command<=8){
  const char* names[6]={"CC_FaceNext","CC_OutfitNext","CC_HandToneNext","CC_HatNext","CC_ArmsNext","CC_CustomizeBack"};
  void* button=find_child(panel,names[command-3]);if(!button||!customization_button_v19(button))return 0;
 }
 customization_stats_v28[6]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);
 customization_stats_v28[7]=command;
 return customization_stats_v28[4]==255;
}



#endif /* MODE_PROBE */
