/* Include after hand_visuals_v21.c; call immediately after avatar_hands_v21.
 * Decorative per-player children inherit their approved pose and activation.
 * Cloth samples come from the delivered outfit atlas palette1, after decoding.
 */
static const Q4 sleeve_outfit_colors_v24[9]={
 {16/255.f,28/255.f,41/255.f,1},{247/255.f,243/255.f,239/255.f,1},
 {16/255.f,28/255.f,41/255.f,1},{239/255.f,235/255.f,231/255.f,1},
 {247/255.f,243/255.f,239/255.f,1},{16/255.f,28/255.f,41/255.f,1},
 {33/255.f,134/255.f,206/255.f,1},{24/255.f,81/255.f,66/255.f,1},
 {115/255.f,44/255.f,74/255.f,1}};
typedef struct {unsigned body,visuals[8],materials[8],renderers[8],shared[8];int outfit,tone,transparent;} SleeveMaterialsV24;
static SleeveMaterialsV24 sleeve_materials_v24[8];
static void sleeve_release_v28(SleeveMaterialsV24* s){
 for(int i=0;i<8;i++){
  void* r=rooted(s->renderers[i]),*shared=rooted(s->shared[i]),*mat=rooted(s->materials[i]);
  if(alive(r)&&alive(shared))FN(0xa1b0e0,void(*)(void*,void*,void*))(r,shared,0);
  if(alive(mat)&&mat!=shared)FN(0xa0ab40,void(*)(void*,void*))(mat,0);
  root_set(&s->materials[i],0);root_set(&s->renderers[i],0);root_set(&s->shared[i],0);root_set(&s->visuals[i],0);
 }
 root_set(&s->body,0);s->outfit=s->tone=s->transparent=-1;
}
static void sleeves_reset_v28(void){for(int i=0;i<8;i++)sleeve_release_v28(&sleeve_materials_v24[i]);}
EXPORT void avatar_sleeves_v24(void* body){
 void* player=body?PTR(body,0x168):0;if(!player)return;
 int style=player_skin(player),outfit=style>=0&&style<81?style/9:2;
 int transparent=player_cosmetic_v28(player,1);
 int tone=player_hand_tone_v21(player);if(tone<0||tone>=6)tone=0;
 SleeveMaterialsV24* slot=0;
 for(int i=0;i<8;i++)if(rooted(sleeve_materials_v24[i].body)==body){slot=&sleeve_materials_v24[i];break;}
 if(!slot)for(int i=0;i<8;i++)if(!alive(rooted(sleeve_materials_v24[i].body))){slot=&sleeve_materials_v24[i];break;}
 if(!slot)return;
 if(rooted(slot->body)!=body){
  sleeve_release_v28(slot);root_set(&slot->body,body);slot->outfit=-1;slot->tone=-1;slot->transparent=-1;
  for(int i=0;i<8;i++){root_set(&slot->visuals[i],0);root_set(&slot->materials[i],0);}
 }
 const char* paths[8]={
 "Hand Root L/Open/Cloudcourt Open Glove/CC_Sleeve","Hand Root L/Closed/Cloudcourt Closed Glove/CC_Sleeve",
 "Hand Root R/Open/Cloudcourt Open Glove/CC_Sleeve","Hand Root R/Closed/Cloudcourt Closed Glove/CC_Sleeve",
 "Hand Root L/CC_ThumbsUp/CC_Sleeve","Hand Root R/CC_ThumbsUp/CC_Sleeve",
 "Hand Root L/CC_SettingOpen/CC_Sleeve","Hand Root R/CC_SettingOpen/CC_Sleeve"};
 int ready=1,rebound=0;
 for(int i=0;i<8;i++){
  if(!alive(rooted(slot->visuals[i]))){
   root_set(&slot->visuals[i],find_child(transform(body),paths[i]));root_set(&slot->materials[i],0);
  }
  if(!alive(rooted(slot->materials[i]))){
   void* t=rooted(slot->visuals[i]);void* renderer=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;
   root_set(&slot->renderers[i],renderer);root_set(&slot->shared[i],renderer?FN(0xa1af10,void*(*)(void*,void*))(renderer,0):0);
   root_set(&slot->materials[i],renderer?FN(0xa1ae90,void*(*)(void*,void*))(renderer,0):0);rebound=1;
  }
  ready&=alive(rooted(slot->materials[i]));
 }
 if(slot->outfit==outfit&&slot->transparent==transparent&&ready&&!rebound)return;
 Q4 color=sleeve_outfit_colors_v24[outfit];
 if(slot->transparent!=transparent||rebound)for(int i=0;i<8;i++){void* r=rooted(slot->renderers[i]);if(r)FN(0xa1b2f0,void(*)(void*,_Bool,void*))(r,!transparent,0);}
 slot->transparent=ready?transparent:-1;
 for(int i=0;i<8;i++){void* mat=rooted(slot->materials[i]);if(mat)FN(0x956610,void(*)(void*,Q4,void*))(mat,color,0);}
 slot->outfit=ready?outfit:-1;slot->tone=ready?tone:-1;
}

