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

/* v22: same public point/reset API, now bounded by the serve whistle event.
 * A display-only override of arm bones and the head runs AFTER FinalIK.
 * RootMotion's pre-solver stage receives the restored animation pose. */
TRAMP(void,bot_ik,(void* ik,void* m))
static unsigned celebration_rules_v21;
static int celebration_team_v21=-1;
static unsigned celebration_target_v24;
static unsigned celebration_serve_rules_v24;
static int celebration_serve_id_v24=-1,celebration_serve_team_v24=-1;
typedef struct {
 unsigned bot,visual,ik,look,upper,lower,hand,head,headbone;int shown,posed,bound,displayed;
 Q4 saved[4];V3 scale;V3 toward,recipient;
} BotCelebrationV21;
static BotCelebrationV21 bot_celebrations_v21[8];
static V3 celebration_gaze_v24(void* player){
 void* body=PTR(player,0x80),*head=body?PTR(body,0x30):0,*torso=body?PTR(body,0x38):0;
 if(alive(head)){V3 p=position(head);if(finitev(p))return p;}
 if(alive(torso)){V3 p=position(torso);if(finitev(p)){p.y+=.35f;return p;}}
 V3 p=position(transform(player));p.y+=1.6f;return p;
}
/* Team.players contains humans only. Photon touchId gives a stable ordering
 * even when each peer's List insertion order differs. Never use distance or
 * the pass/receive target to attribute a winning hit. */
static int celebration_humans_v24(void* rules,int team,void** players,int* ids){
 if(!rules||team<0||team>1)return 0;
 void* teams=PTR(rules,0x60),*side=teams?PTR(teams,0x20+8*team):0;
 void* list=side?PTR(side,0x38):0,*array=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0,count=0;
 if(!array||n<0||n>4)return 0;
 for(int i=0;i<n;i++){
  void* p=PTR(array,0x20+8*i);if(!alive(p)||INT(p,0x28)!=team||!finitev(player_court_position(p)))continue;
  int id=FN(0x30cb70,int(*)(void*,void*))(p,0),j=count;
  while(j>0&&ids[j-1]>id){players[j]=players[j-1];ids[j]=ids[j-1];j--;}
  players[j]=p;ids[j]=id;count++;
 }
 return count;
}
static void celebration_serve_clear_v24(void){
 root_set(&celebration_serve_rules_v24,0);celebration_serve_id_v24=celebration_serve_team_v24=-1;
}
static void celebration_serve_touch_v24(void* rules,int player,int team){
 if(!rules||rules!=rooted(rules_root)||BYTE(rules,0x78)||!BYTE(rules,0x79)||!BYTE(rules,0x94)||INT(rules,0x7c)!=team)return;
 void* humans[4];int ids[4],n=celebration_humans_v24(rules,team,humans,ids);
 for(int i=0;i<n;i++)if(ids[i]==player){
  root_set(&celebration_serve_rules_v24,rules);celebration_serve_id_v24=player;celebration_serve_team_v24=team;return;
 }
}
/* Called only by the authoritative existing EndRally boxing call. The chosen
 * rank travels in spare upper bits; all existing low 16 bits stay identical.
 * Random.Range executes once per point, never once per bot/frame/client. */
EXPORT int celebration_wire_v24(void* rules,int team){
 void* humans[4];int ids[4],n=celebration_humans_v24(rules,team,humans,ids),rank=-1;
 int hitter=rules?INT(rules,0x98):-1;
 int ace=rules&&INT(rules,0x9c)==0&&hitter==-1&&rooted(celebration_serve_rules_v24)==rules&&celebration_serve_team_v24==team;
 if(ace)hitter=celebration_serve_id_v24;
 if(n&&INT(rules,0x7c)==team&&(INT(rules,0x9c)>0||ace))
  for(int i=0;i<n;i++)if(ids[i]==hitter){rank=i;break;}
 if(n&&rank<0){rank=n==1?0:FN(0xa14da0,int(*)(int,int,void*))(0,n,0);if(rank<0||rank>=n)rank=0;}
 return 0x24000000|((rank+1)<<16);
}
static Q4 bone_rotation_v22(void* t,int local){Q4 q;FN(local?0xb74b50:0xb74fd0,void(*)(Q4*,void*,void*))(&q,t,0);return q;}
static void bone_rotation_set_v22(void* t,Q4 q,int local){FN(local?0xb754c0:0xb75750,void(*)(void*,Q4,void*))(t,q,0);}
static V3 bone_scale_v22(void* t){V3 v;FN(0xb74bf0,void(*)(V3*,void*,void*))(&v,t,0);return v;}
static void bone_scale_set_v22(void* t,V3 v){FN(0xb75560,void(*)(void*,V3,void*))(t,v,0);}
static Q4 aim_minus_x_v22(V3 v){
 float n=sqroot(dot(v,v));if(n<.0001f)return (Q4){0,0,0,1};v=mul(v,1/n);
 Q4 q={0,v.z,-v.y,1-v.x};float d=q.y*q.y+q.z*q.z+q.w*q.w;
 return d>.00001f?normalized(q):(Q4){0,1,0,0};
}
static void celebration_restore_v22(BotCelebrationV21* s){
 if(!s||!s->posed)return;
 void* bones[4]={rooted(s->upper),rooted(s->lower),rooted(s->hand),rooted(s->head)};
 for(int i=0;i<4;i++)if(alive(bones[i]))bone_rotation_set_v22(bones[i],s->saved[i],1);
 if(alive(bones[2]))bone_scale_set_v22(bones[2],s->scale);
 s->posed=0;
}
static void celebration_hide_v21(BotCelebrationV21* s){
 if(!s)return;celebration_restore_v22(s);
 if(s->displayed&&alive(rooted(s->visual)))visual_active_v21(rooted(s->visual),0);
 s->shown=0;s->displayed=0;
}
EXPORT void celebration_point_wire_v24(void* rules,int team,int wire){
 for(int i=0;i<8;i++)celebration_hide_v21(&bot_celebrations_v21[i]);
 root_set(&celebration_rules_v21,rules);celebration_team_v21=team>=0&&team<2?team:-1;
 void* humans[4];int ids[4],n=celebration_humans_v24(rules,team,humans,ids);
 int rank=((unsigned)wire>>16&7)-1;
 root_set(&celebration_target_v24,n?humans[rank>=0&&rank<n?rank:0]:0);
}
EXPORT void celebration_point_v21(void* rules,int team){
 celebration_point_wire_v24(rules,team,celebration_wire_v24(rules,team));
}
EXPORT void celebration_reset_v21(void){
 celebration_serve_clear_v24();
 celebration_team_v21=-1;root_set(&celebration_rules_v21,0);
 root_set(&celebration_target_v24,0);
 for(int i=0;i<8;i++)celebration_hide_v21(&bot_celebrations_v21[i]);
}
/* Legacy callable ABI kept for inspection tools; lifetime is event driven. */
EXPORT int celebration_allowed_v21(int winner,int bot_team,int human_team,int rally,float now,float until){
 (void)now;(void)until;return winner>=0&&winner<2&&bot_team==winner&&human_team==winner&&!rally;
}
static int celebration_bind_v22(BotCelebrationV21* s,void* bot){
 void* reach=PTR(bot,0xb8);void* ik=reach?PTR(reach,0x28):0;void* refs=ik?PTR(ik,0x38):0;
 if(!refs)return 0;
 void* upper=PTR(refs,0x68),*lower=PTR(refs,0x70),*hand=PTR(refs,0x78);
 if(!alive(upper)||!alive(lower)||!alive(hand))return 0;
 void* visual=find_child(transform(bot),"CC_WinThumb");
 void* base_mesh=find_child(transform(ik),"Base_mesh");
 void* skin=base_mesh?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(base_mesh),str("SkinnedMeshRenderer"),0):0;
 void* renderer=visual?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(visual),str("MeshRenderer"),0):0;
 void* mat=skin?FN(0xa1af10,void*(*)(void*,void*))(skin,0):0;
 if(!alive(visual)||!mat||!renderer)return 0;
 /* UV palette0 samples this character's existing skin swatch. Never recolor
  * the bot from the local player's preference or the neutral hand texture. */
 FN(0xa1b0e0,void(*)(void*,void*,void*))(renderer,mat,0);
 root_set(&s->visual,visual);root_set(&s->ik,ik);root_set(&s->look,PTR(reach,0x38));
 void* look=rooted(s->look),*solver=look?PTR(look,0x38):0,*headbone=solver?PTR(solver,0x68):0;
 root_set(&s->headbone,headbone);root_set(&s->head,headbone?PTR(headbone,0x10):0);
 root_set(&s->upper,upper);root_set(&s->lower,lower);root_set(&s->hand,hand);s->bound=1;return 1;
}
EXPORT void celebration_bot_v21(void* bot){
 if(!bot)return;BotCelebrationV21* s=0;
 for(int i=0;i<8;i++)if(rooted(bot_celebrations_v21[i].bot)==bot){s=&bot_celebrations_v21[i];break;}
 if(celebration_team_v21<0||INT(bot,0x28)!=celebration_team_v21||(!doubles_enabled&&!quartet_enabled)){
  celebration_hide_v21(s);return;
 }
 void* rules=rooted(rules_root);
 if(!rules||rules!=rooted(celebration_rules_v21)){celebration_hide_v21(s);return;}
 /* NewRally may already set rally_active while waiting for serve. Only the
  * actual serve whistle reset closes this point celebration. */
 int team=INT(bot,0x28);void* target=rooted(celebration_target_v24);
 V3 botp=position(transform(bot)),humanp={0,0,0};
 void* humans[4];int ids[4],n=celebration_humans_v24(rules,team,humans,ids),eligible=0;
 for(int i=0;i<n;i++)if(humans[i]==target)eligible=1;
 /* A disconnected, destroyed, or switched-team human is never retained.
  * The lowest remaining stable id is a deterministic point-local fallback. */
 if(!eligible){target=n?humans[0]:0;root_set(&celebration_target_v24,target);}
 if(!target||!finitev(botp)){celebration_hide_v21(s);return;}humanp=player_court_position(target);
 if(!s)for(int i=0;i<8;i++)if(!alive(rooted(bot_celebrations_v21[i].bot))){
  s=&bot_celebrations_v21[i];celebration_hide_v21(s);root_set(&s->bot,bot);s->bound=0;break;
 }
 if(!s||(!s->bound&&!celebration_bind_v22(s,bot)))return;
 V3 toward=sub(humanp,botp);toward.y=0;float length=sqroot(dot(toward,toward));
 if(length<.001f){celebration_hide_v21(s);return;}
 s->toward=mul(toward,1/length);s->recipient=celebration_gaze_v24(target);s->shown=1;
}
static void celebration_pose_v22(BotCelebrationV21* s){
 if(!s||!s->shown||celebration_team_v21<0)return;
 void* bones[4]={rooted(s->upper),rooted(s->lower),rooted(s->hand),rooted(s->head)},*visual=rooted(s->visual);
 if(!alive(bones[0])||!alive(bones[1])||!alive(bones[2])||!alive(visual))return;
 if(s->posed)celebration_restore_v22(s);
 for(int i=0;i<4;i++)if(alive(bones[i]))s->saved[i]=bone_rotation_v22(bones[i],1);
 s->scale=bone_scale_v22(bones[2]);s->posed=1;
 /* Arm bone local -X is measured from the actual serialized right arm rig.
  * Rotating it moves the existing skinned sleeve and forearm together. */
 bone_rotation_set_v22(bones[0],aim_minus_x_v22((V3){s->toward.x*.65f,.76f,s->toward.z*.65f}),0);
 bone_rotation_set_v22(bones[1],aim_minus_x_v22((V3){s->toward.x*.98f,.20f,s->toward.z*.98f}),0);
 V3 wrist=position(bones[2]);
 /* Collapse only the existing cosmetic hand bone, which has no collider;
  * its replacement is placed at that moved wrist, never a face-level offset. */
 bone_scale_set_v22(bones[2],(V3){.001f,.001f,.001f});
 position_set(visual,wrist);
 float w=sqroot((1+s->toward.z)*.5f),y=w>.0001f?s->toward.x/(2*w):1;
 bone_rotation_set_v22(visual,(Q4){0,y,0,w},0);if(!s->displayed){visual_active_v21(visual,1);s->displayed=1;}
 /* ReachForBall.Update writes the ball look position every frame. Aim the
  * actual calibrated head bone AFTER both existing FinalIK passes, so that
  * a later LookAtIK pass cannot replace this recipient with the ball. The
  * game's LookAtBone method respects this rig's initialized local axis. */
 void* headbone=rooted(s->headbone);
 if(alive(bones[3])&&headbone){
  V3 direction=sub(s->recipient,position(bones[3]));float len=sqroot(dot(direction,direction));
  if(finitev(direction)&&len>.001f)FN(0xafe880,void(*)(void*,V3,float,void*))(headbone,mul(direction,1/len),1.f,0);
 }
}
EXPORT void bot_ik_hook(void* ik,void* m){
 BotCelebrationV21* s=0;
 for(int i=0;i<8;i++)if(rooted(bot_celebrations_v21[i].ik)==ik||rooted(bot_celebrations_v21[i].look)==ik){s=&bot_celebrations_v21[i];break;}
 if(s)celebration_restore_v22(s);
 bot_ik_trampoline(ik,m);
 if(s)celebration_pose_v22(s);
}
