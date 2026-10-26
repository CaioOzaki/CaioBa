/* Include after customization_v19.c. Only decorative children/materials are
 * changed. Tracking poses, Hand Root transforms, colliders and set arc stay
 * under the original game/approved setting code. */
static int hand_grab_v21(int side){
 void* k=*(void**)(base()+0x1542b48);void* stat=k?PTR(k,0xb8):0;
 void* input=stat?PTR(stat,0):0;void* vr=input?PTR(input,0x40):0;
 void* system=*(void**)(base()+0x1541dc0);void* controller=*(void**)(base()+0x1541d98);
 if(!vr||!system||!controller)return 0;
 void* hand=FN(0xa2710,void*(*)(int,void*,void*))(side?6:5,system,vr);
 return hand&&FN(0xa2710,_Bool(*)(int,void*,void*))(1,controller,hand);
}
static void visual_active_v21(void* t,int active){if(t)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),active!=0,0);}
typedef struct {unsigned body,materials[8],visuals[8];int tone,pose;} HandMaterialsV21;
static HandMaterialsV21 hand_materials_v21[8];
EXPORT void avatar_hands_v21(void* body){
 void* player=body?PTR(body,0x168):0;if(!player)return;
 ensure_preferences_v19();
 int local=player==local_avatar_player();int left=local?hand_grab_v21(0):0,right=local?hand_grab_v21(1):0;
 int ready=local&&setting_ready(body),pose=player_hand_pose_v21(player);
 if(local){pose=left&&right&&ready?4:(left?1:0)|(right?2:0);
  if(pose!=local_pose_v21){local_pose_v21=pose;select_appearance(-1,0);}
 }
 HandMaterialsV21* slot=0;
 for(int i=0;i<8;i++)if(rooted(hand_materials_v21[i].body)==body){slot=&hand_materials_v21[i];break;}
 if(!slot)for(int i=0;i<8;i++)if(!alive(rooted(hand_materials_v21[i].body))){slot=&hand_materials_v21[i];break;}
 if(!slot)return;
 if(rooted(slot->body)!=body){root_set(&slot->body,body);slot->tone=-1;slot->pose=-1;
  for(int i=0;i<8;i++){root_set(&slot->materials[i],0);root_set(&slot->visuals[i],0);}
 }
 int tone=player_hand_tone_v21(player),ready_materials=1,ready_visuals=1,rebound=0,visual_rebound=0;
 const char* paths[8]={"Hand Root L/Open/Cloudcourt Open Glove","Hand Root L/Closed/Cloudcourt Closed Glove","Hand Root R/Open/Cloudcourt Open Glove","Hand Root R/Closed/Cloudcourt Closed Glove","Hand Root L/CC_ThumbsUp","Hand Root R/CC_ThumbsUp","Hand Root L/CC_SettingOpen","Hand Root R/CC_SettingOpen"};
 for(int i=0;i<8;i++){
  if(!alive(rooted(slot->visuals[i]))){root_set(&slot->visuals[i],find_child(transform(body),paths[i]));visual_rebound=1;}
  ready_visuals&=alive(rooted(slot->visuals[i]));
  if(!alive(rooted(slot->materials[i]))){
   void* t=rooted(slot->visuals[i]);void* renderer=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;
   root_set(&slot->materials[i],renderer?FN(0xa1ae90,void*(*)(void*,void*))(renderer,0):0);rebound=1;
  }
  ready_materials&=alive(rooted(slot->materials[i]));
 }
 if(slot->pose!=pose||visual_rebound)for(int side=0;side<2;side++){
  int thumb=pose!=4&&(pose&(side?2:1));
  visual_active_v21(rooted(slot->visuals[4+side]),thumb);
  visual_active_v21(rooted(slot->visuals[6+side]),pose==4);
  /* Original Open/Closed parent state remains under trigger/ball playback. */
  visual_active_v21(rooted(slot->visuals[side*2]),!thumb&&pose!=4);
  visual_active_v21(rooted(slot->visuals[side*2+1]),!thumb&&pose!=4);
 }
 slot->pose=ready_visuals?pose:-1;
 if(slot->tone==tone&&ready_materials&&!rebound)return;
 for(int i=0;i<8;i++){void* mat=rooted(slot->materials[i]);if(mat)FN(0x956610,void(*)(void*,Q4,void*))(mat,hand_tone_colors_v21[tone],0);}
 slot->tone=ready_materials?tone:-1;
}
static unsigned celebration_rules_v21;
static int celebration_team_v21=-1;
static float celebration_until_v21;
typedef struct {unsigned bot,visual;int shown;} BotCelebrationV21;
static BotCelebrationV21 bot_celebrations_v21[8];
static void celebration_hide_v21(BotCelebrationV21* slot){
 if(!slot||!slot->shown)return;
 void* visual=rooted(slot->visual);if(alive(visual))visual_active_v21(visual,0);slot->shown=0;
}
EXPORT void celebration_point_v21(void* rules,int scoring_team){
 root_set(&celebration_rules_v21,rules);celebration_team_v21=scoring_team>=0&&scoring_team<2?scoring_team:-1;
 celebration_until_v21=FN(0xb72b40,float(*)(void*))(0)+2.6f;
}
EXPORT void celebration_reset_v21(void){
 celebration_team_v21=-1;celebration_until_v21=0;root_set(&celebration_rules_v21,0);
 for(int i=0;i<8;i++)celebration_hide_v21(&bot_celebrations_v21[i]);
}
EXPORT int celebration_allowed_v21(int winner,int bot_team,int human_team,int rally_active,float now,float until){
 return winner>=0&&winner<2&&bot_team==winner&&human_team==winner&&!rally_active&&now<until;
}
EXPORT void celebration_bot_v21(void* bot){
 if(!bot)return;
 BotCelebrationV21* slot=0;
 for(int i=0;i<8;i++)if(rooted(bot_celebrations_v21[i].bot)==bot){slot=&bot_celebrations_v21[i];break;}
 /* No Transform, Find, position or clock calls during ordinary play. */
 if(celebration_team_v21<0||INT(bot,0x28)!=celebration_team_v21||(!doubles_enabled&&!quartet_enabled)){
  celebration_hide_v21(slot);return;
 }
 void* rules=rooted(rules_root);
 if(!rules||rules!=rooted(celebration_rules_v21)){celebration_hide_v21(slot);return;}
 int team=INT(bot,0x28),rally=network_physics()?net_rally_active:(rules&&BYTE(rules,0x78));
 if(rally){celebration_hide_v21(slot);return;}
 float now=FN(0xb72b40,float(*)(void*))(0);
 if(!celebration_allowed_v21(celebration_team_v21,team,team,rally,now,celebration_until_v21)){celebration_hide_v21(slot);return;}
 int active=1;
 void* target=0;float nearest=1.0e20f;V3 botp=position(transform(bot)),humanp={0,0,0};
 if(active&&finitev(botp)){
  void* teams=PTR(rules,0x60);void* side=teams?PTR(teams,0x20+8*team):0;
  void* list=side?PTR(side,0x38):0;void* array=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
  if(array&&n>0&&n<=4)for(int i=0;i<n;i++){
   void* player=PTR(array,0x20+i*8);if(!alive(player)||INT(player,0x28)!=team)continue;
   V3 p=player_court_position(player);if(!finitev(p))continue;float d=dot(sub(p,botp),sub(p,botp));
   if(d<nearest){nearest=d;target=player;humanp=p;}
  }
 }
 if(!target){celebration_hide_v21(slot);return;}
 if(!slot)for(int i=0;i<8;i++)if(!alive(rooted(bot_celebrations_v21[i].bot))){
  slot=&bot_celebrations_v21[i];root_set(&slot->bot,bot);root_set(&slot->visual,0);slot->shown=0;break;
 }
 if(!slot)return;
 if(!alive(rooted(slot->visual)))root_set(&slot->visual,find_child(transform(bot),"CC_WinThumb"));
 void* visual=rooted(slot->visual);if(!alive(visual))return;
 if(!slot->shown){visual_active_v21(visual,1);slot->shown=1;}
 /* Aim only this visual toward the chosen own-team human. The bot's body,
  * movement, IK, arms and hit shapes retain their normal transforms. */
 V3 toward=sub(humanp,botp);toward.y=0;float len=sqroot(dot(toward,toward));if(len<.001f)return;
 toward=mul(toward,1/len);
 V3 place=add(botp,(V3){toward.x*.45f,1.35f,toward.z*.45f});position_set(visual,place);
 /* Palm (+X) faces the human and raised thumb (+Z) points up in world space.
  * Compose the yaw with -90 degrees about X; only this decorative leaf moves. */
 float w=sqroot((1+toward.x)*.5f),y=w>.0001f?-toward.z/(2*w):1;
 FN(0xb75750,void(*)(void*,Q4,void*))(visual,(Q4){-w*.70710678f,y*.70710678f,y*.70710678f,w*.70710678f},0);
}
