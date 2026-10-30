/* Cosmetic skill rewards. Include after customization_v28.c. Reuses only the
 * existing per-avatar/mirror material instances; never writes shared assets. */
static int rewards_loaded_v29,rewards_counts_v29[6],rewards_choices_v29[3];
static int rewards_dirty_v29;static float rewards_save_at_v29;
static void (*rewards_save_fn_v29)(void);
static unsigned rewards_panel_v29;
static const char* rewards_keys_v29[9]={
 "Cloudcourt.Aces.v29","Cloudcourt.ControlledReceives.v29","Cloudcourt.AssistedSets.v29",
 "Cloudcourt.DirectKills.v29","Cloudcourt.AccurateServes.v29","Cloudcourt.AccurateSpikes.v29",
 "Cloudcourt.RewardOutfit.v29","Cloudcourt.RewardFace.v29","Cloudcourt.RewardAccent.v29"};
static const char* rewards_names_v29[4]={"Base","Sunset","Skyline","Emerald"};
static const char* rewards_faces_v29[4]={"Base","Wink","Focus","Starry Joy"};
static const Q4 rewards_shirts_v29[3]={{215/255.f,107/255.f,69/255.f,1},{34/255.f,127/255.f,168/255.f,1},{39/255.f,124/255.f,98/255.f,1}};
static const Q4 rewards_accents_v29[3]={{1,207/255.f,88/255.f,1},{99/255.f,215/255.f,244/255.f,1},{164/255.f,240/255.f,207/255.f,1}};
static int rewards_unlocked_v29(int c){
 return c==0||(c==1&&(rewards_counts_v29[4]>=5||rewards_counts_v29[0]>=2))||
 (c==2&&rewards_counts_v29[1]+rewards_counts_v29[2]>=10)||
 (c==3&&(rewards_counts_v29[3]>=5||rewards_counts_v29[5]>=5));
}
static void rewards_mark_v29(void){rewards_dirty_v29=1;rewards_save_at_v29=FN(0xb72a20,float(*)(void*))(0)+1.25f;}
EXPORT void rewards_load_v29(void){
 if(rewards_loaded_v29)return;rewards_loaded_v29=1;
 rewards_save_fn_v29=FN(0x14b030,void*(*)(const char*))("UnityEngine.PlayerPrefs::Save");
 for(int i=0;i<6;i++){int v=FN(0xa12690,int(*)(void*,int,void*))(str(rewards_keys_v29[i]),0,0);rewards_counts_v29[i]=v<0?0:v>1000000?1000000:v;}
 for(int i=0;i<3;i++){int v=FN(0xa12690,int(*)(void*,int,void*))(str(rewards_keys_v29[i+6]),0,0);rewards_choices_v29[i]=v>=0&&v<4&&rewards_unlocked_v29(v)?v:0;}
}
static void rewards_flush_v29(void){if(rewards_dirty_v29&&rewards_save_fn_v29){rewards_save_fn_v29();rewards_dirty_v29=0;}}
EXPORT void rewards_tick_v29(void){if(rewards_dirty_v29&&FN(0xb72a20,float(*)(void*))(0)>=rewards_save_at_v29)rewards_flush_v29();}
EXPORT void rewards_refresh_v29(void* panel);
EXPORT void rewards_progress_v29(int kind,int amount){
 if(kind<1||kind>6||amount<=0)return;rewards_load_v29();int i=kind-1,old=rewards_counts_v29[i];
 rewards_counts_v29[i]=amount>=1000000-old?1000000:old+amount;if(rewards_counts_v29[i]==old)return;
 FN(0xa12870,void(*)(void*,int,void*))(str(rewards_keys_v29[i]),rewards_counts_v29[i],0);rewards_mark_v29();
 if(alive(rooted(rewards_panel_v29)))rewards_refresh_v29(rooted(rewards_panel_v29));
}
EXPORT int rewards_encode_v29(int outfit,int face,int accent){
 return outfit>=0&&outfit<4&&face>=0&&face<4&&accent>=0&&accent<4?(int)(0x5c290000u|(unsigned)outfit|((unsigned)face<<2)|((unsigned)accent<<4)):-1;
}
EXPORT int rewards_decode_v29(int packet,int* outfit,int* face,int* accent){
 if(((unsigned)packet&0xffff0000u)!=0x5c290000u)return 0;
 if(((unsigned)packet&0xffc0u)!=0)return -1;
 if(outfit)*outfit=packet&3;if(face)*face=(packet>>2)&3;if(accent)*accent=(packet>>4)&3;return 1;
}
typedef struct {unsigned player;int choices[3];} RewardPeerV29;
static RewardPeerV29 rewards_peers_v29[8];
EXPORT int rewards_packet_v29(void){rewards_load_v29();return rewards_encode_v29(rewards_choices_v29[0],rewards_choices_v29[1],rewards_choices_v29[2]);}
EXPORT int rewards_receive_v29(void* player,int packet){
 int c[3],r=rewards_decode_v29(packet,&c[0],&c[1],&c[2]);if(!r)return 0;if(r<0||!player)return 1;
 /* Prefer a matching player before recycling a dead earlier slot. */
 int slot=-1;for(int i=0;i<8;i++)if(rooted(rewards_peers_v29[i].player)==player){slot=i;break;}
 if(slot<0)for(int i=0;i<8;i++)if(!alive(rooted(rewards_peers_v29[i].player))){slot=i;break;}
 if(slot>=0){root_set(&rewards_peers_v29[slot].player,player);for(int i=0;i<3;i++)rewards_peers_v29[slot].choices[i]=c[i];}return 1;
}
static int rewards_player_choice_v29(void* player,int kind){
 if(player&&player==local_avatar_player()){rewards_load_v29();return rewards_choices_v29[kind];}
 for(int i=0;i<8;i++)if(player&&rooted(rewards_peers_v29[i].player)==player)return rewards_peers_v29[i].choices[kind];return 0;
}
typedef struct {unsigned material,base_texture;} RewardSurfaceV29;
typedef struct {unsigned owner,textures[2];RewardSurfaceV29 surfaces[2];unsigned arms[12];int style,transparent,choices[3];} RewardBodyV29;
static RewardBodyV29 rewards_bodies_v29[8],rewards_mirror_state_v29;
static void* rewards_source_v29(RewardBodyV29* s,void* parent,int face){
 if(!alive(rooted(s->textures[face]))){
  void* t=find_child(parent,face?"CC_RewardSources/Outfit":"CC_RewardSources/Face");
  void* r=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;
  if(r){FN(0xa1b2f0,void(*)(void*,_Bool,void*))(r,0,0);void* m=FN(0xa1af10,void*(*)(void*,void*))(r,0);
   if(m)root_set(&s->textures[face],FN(0x9564b0,void*(*)(void*,void*))(m,0));}
 }return rooted(s->textures[face]);
}
/* Head/body mesh UVs already contain their atlas division. A second material
 * division samples a blank corner and erases faces/shirt details in the mirror
 * and native avatar. Keep unit tiling for both base and reward atlases. */
static void rewards_surface_restore_v29(RewardSurfaceV29* s,int style,int part){
 void* m=rooted(s->material),*t=rooted(s->base_texture);if(!alive(m))return;
 if(alive(t))FN(0x956850,void(*)(void*,void*,void*))(m,t,0);
 int index=part?style/9:style%9;
 FN(0x9566d0,void(*)(void*,V2,void*))(m,(V2){(index%3)/3.f,(2-index/3)/3.f},0);
 FN(0x956790,void(*)(void*,V2,void*))(m,(V2){1,1},0);
 FN(0x956610,void(*)(void*,Q4,void*))(m,(Q4){1,1,1,1},0);
}
static void rewards_body_release_v29(RewardBodyV29* s){
 int style=s->style>=0&&s->style<81?s->style:18;
 for(int i=0;i<2;i++){rewards_surface_restore_v29(&s->surfaces[i],style,i);root_set(&s->surfaces[i].material,0);root_set(&s->surfaces[i].base_texture,0);root_set(&s->textures[i],0);}
 for(int i=0;i<12;i++){void* m=rooted(s->arms[i]);if(alive(m))FN(0x956610,void(*)(void*,Q4,void*))(m,sleeve_outfit_colors_v24[style/9],0);root_set(&s->arms[i],0);}
 root_set(&s->owner,0);s->style=s->transparent=-1;for(int i=0;i<3;i++)s->choices[i]=-1;
}
static int rewards_surface_bind_v29(RewardSurfaceV29* s,void* m){
 if(!alive(m))return 0;if(rooted(s->material)==m)return 0;
 root_set(&s->material,m);root_set(&s->base_texture,FN(0x9564b0,void*(*)(void*,void*))(m,0));return 1;
}
static void rewards_surface_apply_v29(RewardBodyV29* s,int part,int choice,int style){
 RewardSurfaceV29* surface=&s->surfaces[part];void* m=rooted(surface->material);if(!alive(m))return;
 void* t=choice?rooted(s->textures[part]):rooted(surface->base_texture);if(!alive(t))return;
 FN(0x956850,void(*)(void*,void*,void*))(m,t,0);
 int index=choice?choice-1:(part?style/9:style%9);
 FN(0x9566d0,void(*)(void*,V2,void*))(m,(V2){(index%3)/3.f,(2-index/3)/3.f},0);
 FN(0x956790,void(*)(void*,V2,void*))(m,(V2){1,1},0);
 FN(0x956610,void(*)(void*,Q4,void*))(m,(Q4){1,1,1,1},0);
}
static int rewards_arm_bind_v29(RewardBodyV29* s,int index,void* material,void* shared){
 if(!alive(material)||material==shared)return 0;int changed=rooted(s->arms[index])!=material;if(changed)root_set(&s->arms[index],material);return changed;
}
static void rewards_apply_v29(RewardBodyV29* s,int style,int* choices){
 rewards_surface_apply_v29(s,0,choices[1],style);rewards_surface_apply_v29(s,1,choices[0],style);
 Q4 shirt=choices[0]?rewards_shirts_v29[choices[0]-1]:sleeve_outfit_colors_v24[style/9];
 Q4 cuff=choices[2]?rewards_accents_v29[choices[2]-1]:shirt;
 for(int i=0;i<12;i++){void* m=rooted(s->arms[i]);if(alive(m))FN(0x956610,void(*)(void*,Q4,void*))(m,i<4?shirt:cuff,0);}
 s->style=style;for(int i=0;i<3;i++)s->choices[i]=choices[i];
}
EXPORT void rewards_body_v29(void* player,void* body,int style){
 if(!player||!body||style<0||style>=81)return;
 RewardBodyV29* s=0;for(int i=0;i<8;i++)if(rooted(rewards_bodies_v29[i].owner)==body){s=&rewards_bodies_v29[i];break;}
 if(!s)for(int i=0;i<8;i++)if(!alive(rooted(rewards_bodies_v29[i].owner))){s=&rewards_bodies_v29[i];break;}if(!s)return;
 if(rooted(s->owner)!=body){rewards_body_release_v29(s);root_set(&s->owner,body);}
 int transparent=player_cosmetic_v28(player,1);int c[3],changed=s->style!=style||s->transparent!=transparent;for(int i=0;i<3;i++){c[i]=rewards_player_choice_v29(player,i);changed|=s->choices[i]!=c[i];}
 for(int i=0;i<8;i++)if(rooted(skins[i].body)==body)for(int j=0;j<2;j++){
  int rebound=rewards_surface_bind_v29(&s->surfaces[j],rooted(skins[i].materials[j]));changed|=rebound;
  if(rebound||!alive(rooted(s->surfaces[j].base_texture))){void* tex=customization_base_texture_v30(customization_panel_v19(),j);if(tex)root_set(&s->surfaces[j].base_texture,tex);}
 }
 for(int i=0;i<8;i++)if(rooted(cosmetic_bodies_v28[i].body)==body)for(int j=0;j<4;j++)changed|=rewards_arm_bind_v29(s,j,rooted(cosmetic_bodies_v28[i].materials[j]),rooted(cosmetic_bodies_v28[i].shared[j]));
 for(int i=0;i<8;i++)if(rooted(sleeve_materials_v24[i].body)==body)for(int j=0;j<8;j++)changed|=rewards_arm_bind_v29(s,j+4,rooted(sleeve_materials_v24[i].materials[j]),rooted(sleeve_materials_v24[i].shared[j]));
 for(int i=0;i<2;i++)if(!alive(rooted(s->textures[i]))){if(rewards_source_v29(s,transform(body),i))changed=1;}
 if(changed)rewards_apply_v29(s,style,c);s->transparent=transparent;
}
/* Called after customization_refresh_v19, which resets the mirror's base UV
 * and colors each time. No cloning, second camera or activation changes. */
EXPORT void rewards_mirror_v29(void* panel){
 if(!panel)return;rewards_load_v29();RewardBodyV29* s=&rewards_mirror_state_v29;
 if(rooted(s->owner)!=panel){rewards_body_release_v29(s);root_set(&s->owner,panel);}
 for(int i=0;i<2;i++){
  rewards_surface_bind_v29(&s->surfaces[i],rooted(mirror_materials_v28[i].material));
  void* tex=customization_base_texture_v30(panel,i);if(tex)root_set(&s->surfaces[i].base_texture,tex);
 }
 for(int i=0;i<4;i++)rewards_arm_bind_v29(s,i,rooted(mirror_materials_v28[i+2].material),rooted(mirror_materials_v28[i+2].shared));
 for(int i=0;i<2;i++)rewards_source_v29(s,panel,i);
 rewards_apply_v29(s,preferred_style(),rewards_choices_v29);
}
static char* rewards_append_v29(char* p,const char* text){while(*text)*p++=*text++;return p;}
static char* rewards_number_v29(char* p,int n){if(n>=10)*p++=(char)('0'+n/10);*p++=(char)('0'+n%10);return p;}
EXPORT void rewards_refresh_v29(void* panel){
 if(!panel)return;rewards_load_v29();root_set(&rewards_panel_v29,panel);
 const char* paths[3]={"CC_RewardOutfitValue","CC_RewardFaceValue","CC_RewardAccentValue"};
 for(int i=0;i<3;i++)child_label_v19(panel,paths[i],i==1?rewards_faces_v29[rewards_choices_v29[i]]:rewards_names_v29[rewards_choices_v29[i]]);
 char text[512],*p=text;
 for(int c=1;c<=3;c++){
  p=rewards_append_v29(p,rewards_names_v29[c]);p=rewards_append_v29(p,rewards_unlocked_v29(c)?"  UNLOCKED":"  LOCKED");
  if(c==1){p=rewards_append_v29(p,"  Serve targets ");p=rewards_number_v29(p,rewards_counts_v29[4]<5?rewards_counts_v29[4]:5);p=rewards_append_v29(p,"/5 or aces ");p=rewards_number_v29(p,rewards_counts_v29[0]<2?rewards_counts_v29[0]:2);p=rewards_append_v29(p,"/2");}
  if(c==2){int n=rewards_counts_v29[1]+rewards_counts_v29[2];p=rewards_append_v29(p,"  Controlled receives + assisted sets ");p=rewards_number_v29(p,n<10?n:10);p=rewards_append_v29(p,"/10");}
  if(c==3){p=rewards_append_v29(p,"  Direct kills ");p=rewards_number_v29(p,rewards_counts_v29[3]<5?rewards_counts_v29[3]:5);p=rewards_append_v29(p,"/5 or spike targets ");p=rewards_number_v29(p,rewards_counts_v29[5]<5?rewards_counts_v29[5]:5);p=rewards_append_v29(p,"/5");}
  *p++='\n';
 }*p=0;child_label_v19(panel,"CC_RewardsState",text);
}
EXPORT int rewards_button_v29(void* button){
 const char* prev[3]={"CC_RewardOutfitPrev","CC_RewardFacePrev","CC_RewardAccentPrev"};
 const char* next[3]={"CC_RewardOutfitNext","CC_RewardFaceNext","CC_RewardAccentNext"};
 for(int i=0;i<3;i++){
  int d=named(button,next[i])?1:named(button,prev[i])?-1:0;if(!d)continue;rewards_load_v29();
  int c=rewards_choices_v29[i];for(int step=0;step<4;step++){c=(c+d+4)%4;if(rewards_unlocked_v29(c))break;}
  if(c!=rewards_choices_v29[i]){rewards_choices_v29[i]=c;FN(0xa12870,void(*)(void*,int,void*))(str(rewards_keys_v29[i+6]),c,0);rewards_mark_v29();select_appearance(-1,0);customization_refresh_v19();}
  if(alive(rooted(rewards_panel_v29)))rewards_refresh_v29(rooted(rewards_panel_v29));return 1;
 }return 0;
}
EXPORT void rewards_reset_v29(void){
 rewards_flush_v29();for(int i=0;i<8;i++){rewards_body_release_v29(&rewards_bodies_v29[i]);root_set(&rewards_peers_v29[i].player,0);}
 rewards_body_release_v29(&rewards_mirror_state_v29);root_set(&rewards_panel_v29,0);
 /* Counters, unlocks and local choices deliberately survive scene/room resets. */
}



