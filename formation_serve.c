/* Roles follow areas through the existing rotation: rear, wing, setter,
 * wing. No player identity permanently owns a role. */
TRAMP(void,team_update,(void* team,void* m))
TRAMP(_Bool,local_serve,(void* routine,void* m))
TRAMP(void*,hand_find,(void* hand,void* m))
static unsigned waiting_ball_root;
static unsigned attack_receiver[2];
static unsigned wing_turn[2];
static void* lobby_hand_ball(void* hand);
static int member_role(void* member){
 if(!member)return -1;
 int team=INT(member,0x28);if(team<0||team>1)return -1;
 TeamSave* s=&team_saves[team];void* area=PTR(member,0x20);
 if(!area||!s->modified)return -1;
 for(int i=0;i<4;i++)if(s->areas[i].area==area)return (i-s->slots[0]+4)%4;
 return -1;
}
static void* team_member_for_role(void* team,int role,void* exclude){
 void* list=team?PTR(team,0x28):0;void* array=list?PTR(list,0x10):0;
 if(!array)return 0;int n=INT(list,0x18);if(n<0||n>4)return 0;
 for(int i=0;i<n;i++){void* p=PTR(array,0x20+i*8);if(p&&p!=exclude&&member_role(p)==role)return p;}
 return 0;
}
static int quartet_setup(void* bot){
 if(!quartet_enabled||!bot)return 0;
 void* rules=rooted(rules_root);if(!rules||!BYTE(rules,0x78)||BYTE(rules,0x79)||serve_flight_team==INT(bot,0x28))return 0;
 int used=INT(rules,0x7c)==INT(bot,0x28)?INT(rules,0x9c):0;
 return used>=0&&used<2;
}
static void* quartet_pass(void* bot,void* target,void* m){
 if(!quartet_setup(bot))return target;
 void* rules=rooted(rules_root);int team=INT(bot,0x28);if(team<0||team>1)return target;
 void* array=PTR(rules,0x60);void* side=array?PTR(array,0x20+team*8):0;
 int used=INT(rules,0x7c)==team?INT(rules,0x9c):0;
 void* receiver=used==0?team_member_for_role(side,2,bot):0;
 if(!receiver){
  /* Prefer a human wing when present; otherwise alternate the wings. */
  void* human=rooted(local_player_root);int role=member_role(human);
  if(human&&human!=bot&&INT(human,0x28)==team&&(role==1||role==3))receiver=human;
  if(!receiver)receiver=team_member_for_role(side,(wing_turn[team]++&1)?3:1,bot);
  if(!receiver)receiver=team_member_for_role(side,3,bot);
  if(!receiver)receiver=team_member_for_role(side,1,bot);
 }
 if(!receiver)return target;
 if(!target)target=FN(0x270680,void*(*)(void*,void*))(bot,m);
 if(target){
  V3 point=receiver==rooted(local_player_root)?player_court_position(receiver):position(transform(receiver));
  if(used==0){point.x=0;point.z=team==0?-.85f:.85f;point.y=1.65f;}
  else {point.x=point.x<0?-2.65f:2.65f;point.z=team==0?-1.15f:1.15f;point.y=2.65f;}
  *(V3*)((char*)target+0x10)=point;
  FLT(target,0x20)=FLT(bot,0x44)+doubles_set_extra;BYTE(target,0x24)=receiver==rooted(local_player_root);
  if(used==1)root_set(&attack_receiver[team],receiver);
 }
 return target;
}
EXPORT void team_update_hook(void* team,void* m){
 team_update_trampoline(team,m);
 if(!quartet_enabled)return;
 void* rules=rooted(rules_root);if(!rules||!BYTE(rules,0x78)||BYTE(rules,0x79))return;
 int index=rooted(team_saves[0].root)==team?0:rooted(team_saves[1].root)==team?1:-1;
 if(index<0||INT(rules,0x7c)!=index)return;
 int used=INT(rules,0x9c);if(used!=1&&used!=2)return;
 if(used==1&&attack_receiver[index])root_set(&attack_receiver[index],0);
 void* receiver=used==1?team_member_for_role(team,2,0):rooted(attack_receiver[index]);
 if(!receiver)return;
 /* A setter who received cannot touch twice. Keep the original chooser
  * for that emergency instead of freezing the team on an illegal touch. */
 if(FN(0x30cb70,int(*)(void*,void*))(receiver,0)==INT(rules,0x98))return;
 void* list=PTR(team,0x30);void* array=list?PTR(list,0x10):0;
 if(array){int n=INT(list,0x18);if(n>=0&&n<=4)for(int i=0;i<n;i++){
  void* bot=PTR(array,0x20+i*8);if(bot)BYTE(bot,0x70)=bot==receiver;
 }}
}
static void serve_visible(void* ball,int visible){
 void* renderer=ball?PTR(ball,0x40):0;
 if(renderer)FN(10597104,void(*)(void*,_Bool,void*))(renderer,visible!=0,0);
}
static void hand_serve_reset(void){
 void* ball=rooted(waiting_ball_root);if(ball)serve_visible(ball,1);
 root_set(&waiting_ball_root,0);
 for(int i=0;i<2;i++){root_set(&attack_receiver[i],0);wing_turn[i]=0;}
}
/* Replace just the waiting-ball placement in LocalPlayerServe. The ball
 * stays frozen and invisible until either hand asks to grab it. */
EXPORT void hand_serve_position_hook(void* t,V3 p,void* m){
 if(offline()||network_physics())p=(V3){0,-100,0};
 FN(0xb756b0,SetVec)(t,p,m);
}
EXPORT _Bool local_serve_hook(void* routine,void* m){
 _Bool result=local_serve_trampoline(routine,m);
 if(!offline()&&!network_physics())return result;
 void* closure=PTR(routine,0x28);void* ball=closure?PTR(closure,0x10):0;
 if(result&&INT(routine,0x10)==1&&ball&&!BYTE(ball,0xd0)){
  root_set(&waiting_ball_root,ball);serve_visible(ball,0);
 }
 return result;
}
EXPORT void* hand_find_hook(void* hand,void* m){
 /* Each avatar has Hands reading local input: reject remote avatar hands. */
 if(network_physics()){
  void* player=online_local_player();void* body=player?PTR(player,0x80):0;
  void* ht=hand?transform(hand):0;void* bt=body?transform(body):0;
  if(!ht||!bt||!FN(12008720,_Bool(*)(void*,void*,void*))(ht,bt,0))return 0;
 }
 if(lobby_active())return lobby_hand_ball(hand);
 void* ball=rooted(waiting_ball_root);void* rules=rooted(rules_root);
 if(ball&&rules&&BYTE(rules,0x7a)&&BYTE(ball,0x89)&&!BYTE(ball,0xd0)&&!PTR(hand,0x30)&&(offline()||network_physics())){
  void* center=PTR(hand,0x18);if(center){
   position_set(transform(ball),position(center));serve_visible(ball,1);
   root_set(&waiting_ball_root,0);
   /* The original Hand.Update starts interaction and owns release/throw. */
   return ball;
  }
 }
 return hand_find_trampoline(hand,m);
}
