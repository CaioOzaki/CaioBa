/* v29 cooperative coverage and restrained, cosmetic bot personality.
 * Include after gameplay_v19.c / hand_visuals_v21.c. All movement still runs
 * through Bot.UpdateBody's original MoveTowards and player comfort checks.
 * No player/root transform, ball, score, serve, ownership or fuse is written.
 */
TRAMP(void,bot_character_v29,(void* bot,int character,void* m))
typedef struct {
 unsigned bot,ik,look,head,mine,set,audio;int style,bound,visible,call,last_team,last_touch;
 float until,next_call,reaction,point_time;int result,posed;Q4 saved;
} BotRefineV29;
static BotRefineV29 bots_refine_v29[8];
static unsigned bots_refine_rules_v29;
static int bots_refine_winner_v29=-1;
static float bots_refine_point_v29=-100;
static void bot_team_clear_v29(int side);
static unsigned bot_call_clips_v29[2];
EXPORT unsigned bot_calls_v29,bot_cover_decisions_v29,bot_reactions_v29;
static float bot_now_v29(void){return FN(0xb72ae0,float(*)(void*))(0);}
static float bot_clamp_v29(float x,float a,float b){return x<a?a:x>b?b:x;}
static float bot_distance_v29(V3 a,V3 b){float x=a.x-b.x,z=a.z-b.z;return x*x+z*z;}
static int bot_host_v29(void){return offline()||(network_physics()&&FN(0x61f230,_Bool(*)(void*))(0));}
static int bot_owned_v29(void* bot){
 if(!bot_host_v29())return 0;
 void* view=FN(0x6054c0,void*(*)(void*,void*))(bot,0);
 return view&&FN(0xe6e000,_Bool(*)(void*,void*))(view,0);
}
static int bot_regular_v29(void* rules){
 return alive(rules)&&(doubles_enabled||quartet_enabled)&&!BYTE(rules,0x68);
}
static int bot_live_v29(void* rules){return bot_regular_v29(rules)&&BYTE(rules,0x78)&&!BYTE(rules,0x79);}
static BotRefineV29* bot_slot_v29(void* bot,int create){
 for(int i=0;i<8;i++)if(rooted(bots_refine_v29[i].bot)==bot)return &bots_refine_v29[i];
 if(!create)return 0;
 for(int i=0;i<8;i++)if(!alive(rooted(bots_refine_v29[i].bot))){
  BotRefineV29* s=&bots_refine_v29[i];root_set(&s->bot,bot);s->style=0;s->bound=0;s->visible=0;
  s->last_team=s->last_touch=-1;s->until=0;s->next_call=0;s->reaction=0;s->point_time=-100;s->posed=0;return s;
 }return 0;
}
static void bot_pose_restore_v29(BotRefineV29* s){
 if(s&&s->posed){void* head=rooted(s->head);if(alive(head))bone_rotation_set_v22(head,s->saved,1);s->posed=0;}
}
static void bot_call_hide_v29(BotRefineV29* s){
 if(!s)return;
 if(s->visible){visual_active_v21(rooted(s->mine),0);visual_active_v21(rooted(s->set),0);}
 s->visible=0;s->call=0;s->until=0;
}
EXPORT void bots_rally_reset_v29(void){
 for(int i=0;i<2;i++)bot_team_clear_v29(i);
 for(int i=0;i<8;i++){
  BotRefineV29* s=&bots_refine_v29[i];bot_pose_restore_v29(s);bot_call_hide_v29(s);
  s->reaction=0;s->last_team=s->last_touch=-1;
 }
 bots_refine_winner_v29=-1;bots_refine_point_v29=-100;
}
EXPORT void bots_reset_v29(void){
 for(int i=0;i<2;i++)bot_team_clear_v29(i);
 for(int i=0;i<8;i++){
  BotRefineV29* s=&bots_refine_v29[i];bot_pose_restore_v29(s);bot_call_hide_v29(s);
  unsigned* roots[7]={&s->bot,&s->ik,&s->look,&s->head,&s->mine,&s->set,&s->audio};
  for(int j=0;j<7;j++)root_set(roots[j],0);s->bound=0;s->reaction=0;s->point_time=-100;
 }
 root_set(&bots_refine_rules_v29,0);bots_refine_winner_v29=-1;bots_refine_point_v29=-100;
}
/* Original soft two-note call signs reinforce the English captions. They are
 * synthesized locally (no voice recordings/TTS/downloads) and respect Game
 * and Master volume. Audio resources are created only on the first call. */
EXPORT float bot_call_sample_v29(int call,int sample){
 if(sample<0||sample>=3528)return 0;
 float time=sample/22050.f,split=.075f,frequency=call==2?(time<split?620.f:820.f):(time<split?820.f:620.f);
 float phase=time*frequency;phase-=(int)phase;
 float triangle=phase<.5f?4*phase-1:3-4*phase;
 float pulse=time<split?time/split:(time-split)/(.16f-split);
 if(pulse<0||pulse>1)return 0;
 float envelope=4*pulse*(1-pulse);return triangle*envelope*.10f;
}
static void bot_call_audio_v29(BotRefineV29* s,int call){
 float gain=audio_gain_v28(2);if(!s||gain<=0||call<1||call>2)return;
 void* bot=rooted(s->bot);if(!alive(bot))return;
 if(!alive(rooted(s->audio))){
  void* domain=FN(0x14a920,void*(*)(void))();
  void* assembly=domain?FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.AudioModule"):0;
  void* img=assembly?FN(0x14a530,void*(*)(void*))(assembly):0;
  void* klass=img?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine","AudioSource"):0;
  if(!klass)return;
  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
  void* source=type?FN(0x94f240,void*(*)(void*,void*,void*))(gameobject(bot),type,0):0;
  if(!source)return;root_set(&s->audio,source);
  FN(0xebc590,void(*)(void*,float,void*))(source,1.f,0);
 }
 int k=call-1;
 if(!alive(rooted(bot_call_clips_v29[k]))){
  void* clip=FN(0xeba090,void*(*)(void*,int,int,int,_Bool,void*))(str(call==2?"Cloudcourt_SetCall_v29":"Cloudcourt_MineCall_v29"),3528,1,22050,0,0);
  if(!clip)return;
  void* corlib=FN(0x14acb0,void*(*)(void))();
  void* single=corlib?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(corlib,"System","Single"):0;
  void* samples=single?FN(0x14a4f0,void*(*)(void*,U64))(single,3528):0;if(!samples)return;
  for(int i=0;i<3528;i++)FLT(samples,0x20+i*4)=bot_call_sample_v29(call,i);
  if(!FN(0xeba5f0,_Bool(*)(void*,void*,int,void*))(clip,samples,0,0))return;
  root_set(&bot_call_clips_v29[k],clip);
 }
 void* source=rooted(s->audio);FN(0xebc760,void(*)(void*,float,void*))(source,gain*.35f,0);
 FN(0xebc2d0,void(*)(void*,void*,void*))(source,rooted(bot_call_clips_v29[k]),0);FN(0xebbe30,void(*)(void*,void*))(source,0);
}
EXPORT void bot_character_v29_hook(void* bot,int character,void* m){
 bot_character_v29_trampoline(bot,character,m);
 if(!alive(bot))return;BotRefineV29* s=bot_slot_v29(bot,1);if(!s)return;
 bot_pose_restore_v29(s);bot_call_hide_v29(s);s->bound=0;
 root_set(&s->ik,0);root_set(&s->look,0);root_set(&s->head,0);
 static const int ids[9]={39,12,30,21,15,18,0,45,6};
 s->style=0;for(int i=0;i<9;i++)if(character==ids[i])s->style=i;
}
/* Ballistic reception at the existing team intercept height. A finite bounded
 * horizon prevents a malformed/no-longer-live ball from assigning stale work. */
EXPORT int bot_predict_v29(V3 p,V3 velocity,float height,V3* impact,float* seconds){
 if(!impact||!seconds||!finitev(p)||!finitev(velocity)||!__builtin_isfinite(height))return 0;
 float d=velocity.y*velocity.y+19.62f*(p.y-height);if(d<0||!__builtin_isfinite(d))return 0;
 float t=(velocity.y+sqroot(d))/9.81f;if(t<.015f||t>2.5f)return 0;
 *impact=(V3){p.x+velocity.x*t,height,p.z+velocity.z*t};*seconds=t;
 return finitev(*impact)&&impact->x> -5.5f&&impact->x<5.5f&&impact->z> -10&&impact->z<10;
}
/* Four stable lanes follow the rotated role, not a transient list order.
 * When a human leaves a lane, the nearest supporting lane shades into that
 * empty space. Nobody is repositioned; this returns only a normal walk goal. */
EXPORT V3 bot_cover_goal_v29(int team,int role,V3 impact,V3 human,int has_human){
 float sign=team?1.f:-1.f;V3 p;
 switch(role&3){
  case 0:p=(V3){0,0,6.4f*sign};break;
  case 1:p=(V3){-2.65f,0,4.1f*sign};break;
  case 2:p=(V3){0,0,2.15f*sign};break;
  default:p=(V3){2.65f,0,4.1f*sign};break;
 }
 p.x+=bot_clamp_v29(impact.x*.13f,-.55f,.55f);
 if(has_human&&finitev(human)){
  /* Avoid chasing into the human's personal lane: shade toward the opposite
   * uncovered half. The existing native comfort-zone step is also retained. */
  float distance=bot_distance_v29(p,human);
  if(distance<6.25f)p.x+=human.x>=0?-.85f:.85f;
 }
 p.x=bot_clamp_v29(p.x,-3.9f,3.9f);return p;
}
/* Pure owner election: the human retains a reachable nearby reception. The
 * 0.45s sticky window below avoids frame-to-frame pursuit swaps at a tie. */
EXPORT int bot_choose_v29(const int* ids,const V3* positions,const int* eligible,int count,V3 impact,int human_near,int previous){
 if(!ids||!positions||!eligible||count<1||count>4||!finitev(impact)||human_near)return -1;
 int best=-1;float cost=1e20f;
 for(int i=0;i<count;i++)if(eligible[i]&&finitev(positions[i])){
  float c=bot_distance_v29(positions[i],impact);if(ids[i]==previous)c-=.8f;
  if(c<cost-.0001f||(c<cost+.0001f&&(best<0||ids[i]<ids[best]))){cost=c;best=i;}
 }return best;
}
typedef struct {unsigned owner;float until;int last_id,last_team,last_count;V3 impact;int valid;} BotTeamV29;
static BotTeamV29 bot_team_v29[2];
static void bot_team_clear_v29(int side){
 BotTeamV29* s=&bot_team_v29[side];root_set(&s->owner,0);s->until=0;s->valid=0;s->last_id=-1;s->last_team=-1;s->last_count=-1;
}
static int bot_snapshot_v29(void* team,void** bots,int* ids,V3* positions,int* eligible,void* rules,V3 impact){
 void* list=team?PTR(team,0x30):0;void* array=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
 if(!array||n<1||n>4)return 0;int count=0;
 for(int i=0;i<n;i++){
  void* bot=PTR(array,0x20+8*i);if(!alive(bot))continue;
  int id=FN(0x30cb70,int(*)(void*,void*))(bot,0);
  bots[count]=bot;ids[count]=id;positions[count]=position(transform(bot));
  eligible[count]=bot_owned_v29(bot)&&!BYTE(bot,0x80)&&FN(0x252430,_Bool(*)(void*,int,int,V3,void*))(rules,id,INT(bot,0x28),impact,0);count++;
 }return count;
}
EXPORT void bots_team_v29(void* team){
 void* rules=rooted(rules_root);if(!team||!bot_host_v29()||!bot_live_v29(rules)||serve_flight_team>=0)return;
 void* sides=PTR(rules,0x60);int side=sides&&PTR(sides,0x20)==team?0:sides&&PTR(sides,0x28)==team?1:-1;if(side<0)return;
 if(rooted(bots_refine_rules_v29)!=rules){for(int i=0;i<2;i++)bot_team_clear_v29(i);root_set(&bots_refine_rules_v29,rules);}
 BotTeamV29* state=&bot_team_v29[side];void* ball=v19_ball();if(!alive(ball)){bot_team_clear_v29(side);return;}
 V3 impact;float seconds,height=FLT(team,0x20);if(height<.5f||height>3)height=1.25f;
 if(!bot_predict_v29(position(transform(ball)),*(V3*)((char*)ball+0x8c),height,&impact,&seconds)||
    (side==0?impact.z>=-.12f:impact.z<=.12f)){bot_team_clear_v29(side);return;}
 state->impact=impact;state->valid=1;
 int touches=INT(rules,0x7c)==side?INT(rules,0x9c):0;
 /* Quartet's established setter / attack_receiver already includes humans,
  * double-touch legality and rotation. Keep it and only shade supporting bots. */
 if(quartet_enabled&&touches>0){root_set(&state->owner,0);return;}
 void* bots[4];int ids[4],eligible[4];V3 positions[4];int count=bot_snapshot_v29(team,bots,ids,positions,eligible,rules,impact);if(!count)return;
 void* humans[4];int human_ids[4],hn=celebration_humans_v24(rules,side,humans,human_ids),human_near=0;
 for(int i=0;i<hn;i++)if(FN(0x31aae0,_Bool(*)(void*,V3,void*))(humans[i],impact,0)&&
  FN(0x252430,_Bool(*)(void*,int,int,V3,void*))(rules,human_ids[i],side,impact,0))human_near=1;
 float now=bot_now_v29();int previous=-1;
 int same_touch=state->last_id==INT(rules,0x98)&&state->last_team==INT(rules,0x7c)&&state->last_count==INT(rules,0x9c);
 for(int i=0;i<count;i++)if(bots[i]==rooted(state->owner)&&eligible[i]&&same_touch&&now<state->until)previous=ids[i];
 int winner=bot_choose_v29(ids,positions,eligible,count,impact,human_near,previous);
 for(int i=0;i<count;i++)if(bot_owned_v29(bots[i]))BYTE(bots[i],0x70)=i==winner;
 void* selected=winner>=0?bots[winner]:0;
 if(selected!=rooted(state->owner)||!same_touch){root_set(&state->owner,selected);state->until=now+.45f;bot_cover_decisions_v29++;}
 state->last_id=INT(rules,0x98);state->last_team=INT(rules,0x7c);state->last_count=INT(rules,0x9c);
}
static void bot_emit_v29(BotRefineV29* s,int call,float now){
 if(!s||now<s->next_call)return;
 s->call=call;s->until=now+.85f;s->next_call=now+2.1f;bot_calls_v29++;bot_call_audio_v29(s,call);
}
EXPORT void bots_assess_v29(void* bot){
 void* rules=rooted(rules_root);if(!bot||!bot_owned_v29(bot)||!bot_live_v29(rules)||serve_flight_team>=0)return;
 int side=INT(bot,0x28);if(side<0||side>1)return;
 BotTeamV29* team=&bot_team_v29[side];if(!team->valid||rooted(bots_refine_rules_v29)!=rules)return;
 BotRefineV29* s=bot_slot_v29(bot,1);if(!s)return;
 if(BYTE(bot,0x70)){
  int touches=INT(rules,0x7c)==side?INT(rules,0x9c):0;
  if(s->last_team!=INT(rules,0x7c)||s->last_touch!=INT(rules,0x9c)){
   bot_emit_v29(s,touches==1?2:1,bot_now_v29());s->last_team=INT(rules,0x7c);s->last_touch=INT(rules,0x9c);
  }
 }else if(!BYTE(bot,0x80)){
  /* Native AssessSituation still supplies tactics for the elected receiver.
   * Supporters keep no attack tactic and walk to separated coverage lanes. */
  INT(bot,0xa4)=0;
 }
}
EXPORT void bots_before_body_v29(void* bot){
 void* rules=rooted(rules_root);if(!bot||!bot_owned_v29(bot)||!bot_live_v29(rules)||serve_flight_team>=0||BYTE(bot,0x80)||BYTE(bot,0x70))return;
 int side=INT(bot,0x28),role=member_role(bot);if(side<0||side>1||role<0)return;
 BotTeamV29* state=&bot_team_v29[side];if(!state->valid||rooted(bots_refine_rules_v29)!=rules)return;
 void* humans[4];int ids[4],n=celebration_humans_v24(rules,side,humans,ids);V3 h=n?player_court_position(humans[0]):(V3){0,0,0};
 V3 goal=bot_cover_goal_v29(side,role,state->impact,h,n>0);
 /* In doubles the only supporting bot fills the half opposite its human. */
 if(doubles_enabled&&n){goal.x=h.x>=0?-2.2f:2.2f;goal.z=(side?1.f:-1.f)*(h.z*(side?1.f:-1.f)<4.5f?6.1f:3.3f);}
 V3 p=position(transform(bot));if(!finitev(p))return;goal.y=p.y;
 *(V3*)((char*)bot+0xa8)=goal;
}
EXPORT void bots_point_v29(void* rules,int winner){
 if(!bot_regular_v29(rules)||winner<0||winner>1)return;
 root_set(&bots_refine_rules_v29,rules);bots_refine_winner_v29=winner;bots_refine_point_v29=bot_now_v29();
 for(int i=0;i<2;i++)bot_team_clear_v29(i);
 for(int i=0;i<8;i++){bot_call_hide_v29(&bots_refine_v29[i]);bots_refine_v29[i].last_team=bots_refine_v29[i].last_touch=-1;}
}
static int bot_bind_visual_v29(BotRefineV29* s,void* bot){
 if(s->bound)return alive(rooted(s->head));
 void* reach=PTR(bot,0xb8),*ik=reach?PTR(reach,0x28):0,*look=reach?PTR(reach,0x38):0;
 void* solver=look?PTR(look,0x38):0,*headbone=solver?PTR(solver,0x68):0,*head=headbone?PTR(headbone,0x10):0;
 if(!alive(ik)||!alive(look)||!alive(head))return 0;
 root_set(&s->ik,ik);root_set(&s->look,look);root_set(&s->head,head);
 root_set(&s->mine,find_child(transform(bot),"CC_CallMine_v29"));root_set(&s->set,find_child(transform(bot),"CC_CallSet_v29"));
 s->bound=1;return 1;
}
EXPORT void bots_visual_v29(void* bot){
 if(!alive(bot))return;BotRefineV29* s=bot_slot_v29(bot,1);void* rules=rooted(rules_root);
 if(!s)return;
 if(!bot_regular_v29(rules)||!bot_bind_visual_v29(s,bot)){bot_call_hide_v29(s);return;}
 float now=bot_now_v29();
 /* All peers can reproduce short calls from their replicated ball/rules and
  * this bot's ordinary walk goal. This never elects/moves anything remotely. */
 if(bot_live_v29(rules)&&serve_flight_team<0&&!bot_host_v29()){
  void* ball=v19_ball();V3 p=ball?position(transform(ball)):(V3){0,0,0},goal=*(V3*)((char*)bot+0xa8);
  int side=INT(bot,0x28),touch=INT(rules,0x9c),team=INT(rules,0x7c);
  if(ball&&finitev(goal)&&finitev(p)&&bot_distance_v29(goal,p)<1.0f&&(s->last_team!=team||s->last_touch!=touch)){
   bot_emit_v29(s,team==side&&touch==1?2:1,now);s->last_team=team;s->last_touch=touch;
  }
 }
 if(!bot_live_v29(rules)||now>=s->until||now<s->until-1.0f){bot_call_hide_v29(s);}
 if(s->call){
  void* visual=rooted(s->call==2?s->set:s->mine),*other=rooted(s->call==2?s->mine:s->set);
  if(alive(visual)){
   if(s->visible!=s->call){visual_active_v21(other,0);visual_active_v21(visual,1);s->visible=s->call;}
   V3 p=position(rooted(s->head));p.y+=.37f;position_set(visual,p);
   void* player=local_avatar_player();V3 toward=player?sub(celebration_gaze_v24(player),p):(V3){0,0,1};toward.y=0;
   float len=sqroot(dot(toward,toward));if(len>.001f){toward=mul(toward,1/len);float w=sqroot((1+toward.z)*.5f),y=w>.0001f?toward.x/(2*w):1;bone_rotation_set_v22(visual,(Q4){0,y,0,w},0);}
  }
 }
 /* Point-local reactions expire even if no whistle arrives. No repeated emote
  * loop, jump, whole-body turn, or competition with winning thumbs-up. */
 if(s->point_time!=bots_refine_point_v29&&bots_refine_winner_v29>=0&&rooted(bots_refine_rules_v29)==rules){
  s->point_time=bots_refine_point_v29;s->reaction=bots_refine_point_v29+.22f+(s->style%3)*.08f;s->result=INT(bot,0x28)==bots_refine_winner_v29?1:-1;bot_reactions_v29++;
 }
 if(now>s->reaction+1.15f||BYTE(rules,0x79))s->reaction=0;
}
EXPORT void bots_ik_before_v29(void* ik){
 for(int i=0;i<8;i++){BotRefineV29* s=&bots_refine_v29[i];if(rooted(s->ik)==ik||rooted(s->look)==ik)bot_pose_restore_v29(s);}
}
EXPORT void bots_ik_after_v29(void* ik){
 float now=bot_now_v29();void* rules=rooted(rules_root);if(!bot_regular_v29(rules)||BYTE(rules,0x79))return;
 for(int i=0;i<8;i++){
  BotRefineV29* s=&bots_refine_v29[i];if((rooted(s->ik)!=ik&&rooted(s->look)!=ik)||s->reaction<=0)continue;
  float t=(now-s->reaction)/1.15f;if(t<0||t>1)continue;
  void* bot=rooted(s->bot);int thumb=0;
  for(int j=0;j<8;j++)if(rooted(bot_celebrations_v21[j].bot)==bot&&bot_celebrations_v21[j].shown)thumb=1;
  if(thumb)continue;
  void* head=rooted(s->head);if(!alive(head))continue;
  bot_pose_restore_v29(s);s->saved=bone_rotation_v22(head,1);s->posed=1;
  /* Nine small signatures: measured nod, double nod, thoughtful tilt,
   * relaxed tilt, warm nod, slow nod, chin lift, side tilt, tiny bow.
   * Quaternion vector magnitudes are <0.045 (about five degrees total). */
  float wave=4*t*(1-t),second=t<.5f?8*t*(1-2*t):8*(t-.5f)*(2-2*t);
  static const float pitch[9]={.028f,.023f,0,.008f,.035f,.024f,-.023f,.009f,.038f};
  static const float roll[9]={0,.009f,.033f,-.028f,.008f,-.012f,.006f,.030f,0};
  int style=s->style>=0&&s->style<9?s->style:0;float p=pitch[style]*(style==1?second:wave),r=roll[style]*wave;
  if(s->result<0)p=(p<0?-p:p)*.7f;Q4 delta=normalized((Q4){p,0,r,1});
  Q4 a=s->saved,b=delta;Q4 q={a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x,a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w,a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z};
  bone_rotation_set_v22(head,q,1);
 }
}
