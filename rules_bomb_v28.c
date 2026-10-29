/* v28 block accounting and the original compact Bomb court.
 * A supported block is an airborne opponent interception near the net, at or
 * above the authored 2.4m top tape. Jumping in the back court is a normal hit.
 * Accepted ball centre is the stable contact proxy available in this build;
 * no hand contact/penetration or full FIVB referee simulation is claimed. */
static V3 accepted_position_v28;
static int accepted_position_valid_v28;
static int accepted_block_v28;
static void landing_bomb_v28(void* ball,V3 p,int outside);
static int v28_indoor(void){
 void* k=PTR((void*)base(),0x15422a0);void* s=k?PTR(k,0xb8):0;void* e=s?PTR(s,0):0;
 return e&&v19_word(PTR(e,0x18),"Indoor");
}
static void* v28_ball(void){
 void* k=PTR((void*)base(),0x15426f0);void* s=k?PTR(k,0xb8):0;return s?PTR(s,0):0;
}
static void* v28_member(void* rules,int id,int team,int* bot){
 if(!rules||team<0||team>1)return 0;
 void* teams=PTR(rules,0x60);void* side=teams?PTR(teams,0x20+team*8):0;
 for(int kind=0;side&&kind<2;kind++){
  void* list=PTR(side,kind?0x30:0x38);void* items=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
  if(items&&n>=0&&n<=4)for(int i=0;i<n;i++){
   void* p=PTR(items,0x20+i*8);
   if(p&&FN(0x30cb70,int(*)(void*,void*))(p,0)==id){if(bot)*bot=kind;return p;}
  }
 }
 return 0;
}
EXPORT int block_geometry_v28(int airborne,int team,V3 player,V3 ball){
 if(!airborne||team<0||team>1||!finitev(player)||!finitev(ball))return 0;
 return ball.x>=-4.5f&&ball.x<=4.5f&&ball.y>=2.4f&&ball.z>=-1.25f&&ball.z<=1.25f&&
        player.z>=-1.6f&&player.z<=1.6f&&(team?player.z>=0:player.z<=0);
}
static int v28_block_at(void* rules,int id,int team,V3 p){
 int bot=0;void* member=v28_member(rules,id,team,&bot);if(!member)return 0;
 V3 mp=bot?position(transform(member)):player_court_position(member);
 return block_geometry_v28(bot?BYTE(member,0x80):player_is_airborne(member),team,mp,p);
}
static int v28_block(void* rules,int id,int team){
 if(accepted_position_valid_v28)return v28_block_at(rules,id,team,accepted_position_v28);
 void* ball=v28_ball();return ball&&v28_block_at(rules,id,team,position(transform(ball)));
}
/* Exact small AllowedToHitBall replacement. The original ignores ballPosition.
 * Native lastTouchId=-1 after one block permits its immediate next contact;
 * that accepted contact restores the real id, so no unlimited double touches. */
EXPORT _Bool allowed_hit_v28_hook(void* rules,int id,int team,V3 ball,void* m){
 (void)ball;(void)m;
 if(!rules||team<0||team>1)return 0;
 if(network_physics()&&!FN(0x61f230,_Bool(*)(void*))(0))
  return net_rally_active&&id!=net_last_id_v28&&(net_touch_team!=team||net_touch_count<3);
 return BYTE(rules,0x78)&&id!=INT(rules,0x98)&&(INT(rules,0x7c)!=team||INT(rules,0x9c)<3);
}
TRAMP(void,bomb_ground_v28,(void* rules,void* ball,void* m))
EXPORT int court_inside_v28(int bomb,V3 p){
 return finitev(p)&&p.x>-(bomb?2.f:4.5f)&&p.x<(bomb?2.f:4.5f)&&p.z>-(bomb?4.5f:9.f)&&p.z<(bomb?4.5f:9.f);
}
EXPORT void bomb_ground_v28_hook(void* rules,void* ball,void* m){
 if(!rules||!BYTE(rules,0x68)){bomb_ground_v28_trampoline(rules,ball,m);return;}
 if(!ball||!BYTE(rules,0x78)||!FN(0x61f230,_Bool(*)(void*))(0))return;
 V3 p=position(transform(ball));if(!finitev(p))return;
 int inside=court_inside_v28(1,p),last=INT(rules,0x7c);
 if(last<0||last>1)return;
 point_reason=inside?3:4;landing_bomb_v28(ball,p,!inside);
 int winner=inside?(p.z<0?1:0):1-last;
 if(serve_flight_team>=0)point_reason=6;
 FN(0x2533a0,void(*)(void*,int,void*))(rules,winner,m);
}
/* The two online Instantiate call sites use the same existing Photon prefabs
 * and RPC registry as solo Bomb. Namespace selection travels with the room. */
EXPORT void* online_rules_prefab_v28(void* name,V3 p,void* rotation,int group,void* data,void* m){
 if(online_bomb_v28)name=FN(0x14b790,void*(*)(const char*))("GameRulesBomb");
 return FN(0x60fb50,void*(*)(void*,V3,void*,int,void*,void*))(name,p,rotation,group,data,m);
}
EXPORT void* online_ball_prefab_v28(void* name,V3 p,void* rotation,int group,void* data,void* m){
 if(online_bomb_v28)name=FN(0x14b790,void*(*)(const char*))("VolleyballBomb");
 return FN(0x60fb50,void*(*)(void*,V3,void*,int,void*,void*))(name,p,rotation,group,data,m);
}

/* Original solo Bomb builds only a 1v1 roster. Use its regular roster path
 * just while constructing members; restore the mode before rally/fuse code. */
TRAMP(void,bomb_team_a_v28,(void* rules,void* m))
TRAMP(void,bomb_team_b_v28,(void* rules,void* m))
EXPORT void bomb_team_a_v28_hook(void* rules,void* m){
 unsigned char bomb=BYTE(rules,0x68);BYTE(rules,0x68)=0;
 bomb_team_a_v28_trampoline(rules,m);BYTE(rules,0x68)=bomb;
}
EXPORT void bomb_team_b_v28_hook(void* rules,void* m){
 unsigned char bomb=BYTE(rules,0x68);BYTE(rules,0x68)=0;
 bomb_team_b_v28_trampoline(rules,m);BYTE(rules,0x68)=bomb;
}

/* Prefixes leave the existing 24-bit spin payload and low3 native context
 * untouched. 0x48 = block without spin, 0x58 = block with packed spin.
 * The sender sees its own airborne state; peers must not infer Bot.jumping
 * from PhotonTransformView, because that bool is not serialized. */
EXPORT int block_wire_context_v28(int context,int block){
 if(!block)return context;
 unsigned prefix=(unsigned)context&0xf8000000u;
 return prefix==0x50000000u||prefix==0x58000000u?
        (int)(((unsigned)context&0x07ffffffu)|0x58000000u):(int)(0x48000000u|((unsigned)context&7u));
}
TRAMP(void,change_motion_v28,(void* ball,V3 p,V3 velocity,_Bool hit,_Bool isThrow,int id,int team,int context,void* m))
EXPORT void change_motion_v28_hook(void* ball,V3 p,V3 velocity,_Bool hit,_Bool isThrow,int id,int team,int context,void* m){
 if(ball&&hit&&network_physics()&&team>=0&&team<2&&id>=0&&finitev(p)&&!lobby_is_ball(ball)){
  void* rules=rooted(rules_root);int candidate=0;
  if(rules&&!BYTE(rules,0x68)){
   if(FN(0x61f230,_Bool(*)(void*))(0))candidate=BYTE(rules,0x78)&&!BYTE(rules,0x79)&&serve_flight_team<0&&INT(rules,0x7c)==1-team;
   else candidate=net_rally_active&&!net_first_touch&&net_serve_team<0&&net_touch_team==1-team;
   if(candidate&&v28_block_at(rules,id,team,p))context=block_wire_context_v28(context,1);
  }
 }
 change_motion_v28_trampoline(ball,p,velocity,hit,isThrow,id,team,context,m);
}
