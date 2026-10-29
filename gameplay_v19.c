/* Real Bot.Update jump path and fixed best-of-three venue rules.
 * The set trajectory/target in comfort_v14.c is deliberately untouched. */
TRAMP(void,bot_update,(void* bot,void* m))
EXPORT float v19_bot_jump_height=2.0f;
static void v19_adjust_jump(void* bot){
 float speed=sqroot(19.62f*v19_bot_jump_height);
 FLT(bot,0x98)=speed;FLT(bot,0xa0)=2*speed/9.81f;
}
static void* v19_ball(void){
 void* klass=PTR((void*)base(),0x15426f0);void* stat=klass?PTR(klass,0xb8):0;
 return stat?PTR(stat,0):0;
}
static int v19_third_touch(void* bot){
 void* rules=rooted(rules_root);
 if(!rules||(!doubles_enabled&&!quartet_enabled)||BYTE(rules,0x68)||!BYTE(rules,0x78)||BYTE(rules,0x79))return 0;
 int team=INT(bot,0x28);
 return team>=0&&team<2&&serve_flight_team<0&&INT(rules,0x7c)==team&&INT(rules,0x9c)==2&&BYTE(bot,0x70);
}
/* A descending set gives a predictable contact time. Start the jump before
 * the old distance-only check, provided the bot has reached the attack lane.
 * This changes the attacker, never the ball's trajectory or attack target. */
static int v19_attack_jump_due(void* bot,void* ball){
 if(!ball||!v19_third_touch(bot))return 0;
 void* rules=rooted(rules_root);
 if(FN(0x30cb70,int(*)(void*,void*))(bot,0)==INT(rules,0x98))return 0;
 V3 p=position(transform(ball)),v=*(V3*)((char*)ball+0x8c),b=position(transform(bot));
 if(!finitev(p)||!finitev(v)||!finitev(b)||v.y>=-.05f)return 0;
 void* collider=PTR(bot,0x78);if(!collider)return 0;
 V3 top=FN(0xec0c30,V3(*)(void*,V3,void*))(collider,(V3){b.x,b.y+10,b.z},0);
 if(!finitev(top))return 0;
 float contact=top.y+1.45f;
 if(contact<3.1f)contact=3.1f;if(contact>4.3f)contact=4.3f;
 if(p.y<contact)return 0;
 float discriminant=v.y*v.y+19.62f*(p.y-contact);
 if(discriminant<0||!__builtin_isfinite(discriminant))return 0;
 float t=(v.y+sqroot(discriminant))/9.81f;
 if(t<0||t>.45f)return 0;
 float dx=p.x+v.x*t-b.x,dz=p.z+v.z*t-b.z;
 return dx*dx+dz*dz<=.55f*.55f;
}
EXPORT void bot_update_hook(void* bot,void* m){
 if(!bot)return;
 int regular=doubles_enabled||quartet_enabled,was_jumping=BYTE(bot,0x80),owns=0;
 if(regular){void* view=FN(0x6054c0,void*(*)(void*,void*))(bot,0);owns=view&&FN(0xe6e000,_Bool(*)(void*,void*))(view,0);}
 void* ball=owns?v19_ball():0;
 if(owns&&!was_jumping&&v19_attack_jump_due(bot,ball)){
  FN(0x270020,void(*)(void*,void*))(bot,0);v19_adjust_jump(bot);
 }
 bot_update_trampoline(bot,m);
 if(owns&&!was_jumping&&BYTE(bot,0x80)){
  /* Bot.Update inlines Jump instead of calling the separately hooked method.
   * A nearby rising set must not trigger a jump a second before it returns. */
  V3 velocity=ball?*(V3*)((char*)ball+0x8c):(V3){0,0,0};
  if(v19_third_touch(bot)&&finitev(velocity)&&velocity.y>.05f){BYTE(bot,0x80)=0;FLT(bot,0x84)=0;}
  else v19_adjust_jump(bot);
 }
}
static int v19_word(void* text,const char* word){
 if(!text)return 0;int n=INT(text,0x10),length=0;for(;word[length];length++);
 if(n<length||n>512)return 0;
 for(int i=0;i<=n-length;i++){
  int match=1;for(int j=0;j<length;j++)if(*(unsigned short*)((char*)text+0x14+2*(i+j))!=(unsigned char)word[j]){match=0;break;}
  if(match)return 1;
 }return 0;
}
EXPORT int points_per_set_hook(void* m){
 void* klass=PTR((void*)base(),0x15422a0);void* stat=klass?PTR(klass,0xb8):0;void* environment=stat?PTR(stat,0):0;
 return environment&&v19_word(PTR(environment,0x18),"Indoor")?25:21;
}
/* Original Settings.sets is the wins required, not the maximum sets played. */
EXPORT int sets_to_win_hook(void* m){return 2;}

static void landing_bomb_v28(void* ball,V3 p,int outside){
 landing_prepare_v20(ball,p);landing_pending_out_v20=outside;
}
