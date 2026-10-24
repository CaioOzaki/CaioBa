/* Symmetric net clearance measured from tracked head, with root fallback. */
TRAMP(void,net_clamp,(void* player,void* method))
EXPORT void net_clamp_hook(void* player,void* method){
 void* t=transform(player);if(!t)return;
 V3 p=position(t);if(!finitev(p))return;
 void* body=PTR(player,0x80);
 float offset=0;
 if(body){V3 h=*(V3*)((char*)body+0xe8);if(finitev(h)&&h.y>.2f)offset=h.z-p.z;}
 if(p.x< -5.5f)p.x=-5.5f;if(p.x>5.5f)p.x=5.5f;
 int team=INT(player,0x28);
 if(team==0){if(p.z< -10)p.z=-10;if(p.z>-.12f-offset)p.z=-.12f-offset;}
 if(team==1){if(p.z>10)p.z=10;if(p.z<.12f-offset)p.z=.12f-offset;}
 FN(0xb756b0,SetVec)(t,p,0);
}

/* Reuse the original buffered per-player RPC. v16 has its own room namespace.
 * A request never changes team membership during a rally. The host applies it
 * between points, validates capacity, and broadcasts the original assignments.
 */
TRAMP(void,riot_choose,(void* player,int value,void* method))
TRAMP(void,riot_menu,(void* page,void* method))
typedef struct {unsigned player;int skin,pending;} RiotPlayer;
static RiotPlayer riot_players[8];
static unsigned riot_buttons[2],riot_page;
static int riot_pressed[2];
static void riot_label(void* button,const char* text);
static RiotPlayer* riot_slot(void* player){
 for(int i=0;i<8;i++)if(rooted(riot_players[i].player)==player)return &riot_players[i];
 for(int i=0;i<8;i++)if(!alive(rooted(riot_players[i].player))){
  RiotPlayer* s=&riot_players[i];root_set(&s->player,player);s->skin=-1;s->pending=-1;return s;
 }return 0;
}
static int riot_skin(void* player){
 for(int i=0;i<8;i++)if(rooted(riot_players[i].player)==player)return riot_players[i].skin;
 return -1;
}
EXPORT void riot_choose_hook(void* player,int value,void* method){
 if(network_physics()&&(value&0xfffffff0)==0x5610){
  RiotPlayer* s=riot_slot(player);if(s&&(value&15)<4)s->skin=value&15;return;
 }
 if(network_physics()&&(value&0xfffffffe)==0x5620){
  RiotPlayer* s=riot_slot(player);if(s)s->pending=value&1;return;
 }
 if(network_physics()&&value==0x5630){
  if(player==online_local_player()&&alive(rooted(riot_buttons[0])))riot_label(rooted(riot_buttons[0]),"TIME LOTADO");return;
 }
 riot_choose_trampoline(player,value,method);
 if(network_physics()&&player==online_local_player()&&alive(rooted(riot_buttons[0])))riot_label(rooted(riot_buttons[0]),"CHANGE TEAMS");
}
static void riot_end_point(void* rules){
 if(!rules||!network_physics()||!FN(0x61f230,_Bool(*)(void*))(0))return;
 int changed=0,cap=online_format==2?2:4;
 void* list=online_players();void* a=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
 if(!a||n<1||n>8)return;
 for(int i=0;i<8;i++){
  RiotPlayer* s=&riot_players[i];void* p=rooted(s->player);int team=s->pending;s->pending=-1;
  if(!alive(p)||team<0||team>1||INT(p,0x28)==team)continue;
  int count=0;for(int j=0;j<n;j++){void* q=PTR(a,0x20+j*8);if(q&&q!=p&&INT(q,0x28)==team)count++;}
  if(count>=cap){choose_team_trampoline(p,0x5630,0);continue;}
  choose_team_trampoline(p,team,0);changed=1;
 }
 if(changed){
  /* Team.Clear only clears lists. Remove the old host-owned bots first. */
  unsigned old_bots[8]={0};int used=0;void* teams=PTR(rules,0x60);
  for(int team=0;team<2;team++){
   void* side=teams?PTR(teams,0x20+team*8):0;void* bots=side?PTR(side,0x30):0;
   void* items=bots?PTR(bots,0x10):0;int n=bots?INT(bots,0x18):0;
   if(items&&n>=0&&n<=4)for(int j=0;j<n&&used<8;j++){void* bot=PTR(items,0x20+j*8);if(bot)root_set(&old_bots[used++],bot);}
  }
  for(int j=0;j<used;j++){void* bot=rooted(old_bots[j]);if(alive(bot))FN(0x60cb40,void(*)(void*,void*))(gameobject(bot),0);root_set(&old_bots[j],0);}
  FN(0x2527d0,void(*)(void*,void*))(rules,0);FN(0x254a00,void(*)(void*,void*))(rules,0);
 }
}
static void riot_label(void* button,const char* text){
 void* t=transform(button);if(!t)return;
 if(FN(0xb74800,int(*)(void*,void*))(t,0)<1)return;
 void* child=FN(0xb73930,void*(*)(void*,int,void*))(t,0,0);
 void* label_component=child?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(child),str("Text"),0):0;
 label(label_component,text);
}
EXPORT void riot_menu_hook(void* page,void* method){
 riot_menu_trampoline(page,method);
 for(int i=0;i<2;i++){void* b=rooted(riot_buttons[i]);if(alive(b))FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(b),network_physics()!=0,0);}
 if(!network_physics())return;
 if(rooted(riot_page)!=page||!alive(rooted(riot_buttons[0]))){
  void* original=PTR(page,0x30);if(!original)return;
  void* parent=FN(0xb739d0,void*(*)(void*,void*))(transform(original),0);
  for(int i=0;i<2;i++){
   void* button=FN(0xa0b160,void*(*)(void*,void*))(original,0);if(!button)return;
   void* old_event=PTR(button,0xf0);
   if(old_event){void* event=FN(0x1c22e0,void*(*)(void*))(PTR(old_event,0));if(!event)return;FN(0x40dea0,void(*)(void*,void*))(event,0);managed_field(button,0xf0,event);}
   root_set(&riot_buttons[i],button);void* t=transform(button);
   FN(0xb74340,void(*)(void*,void*,_Bool,void*))(t,parent,0,0);
   FN(0xa16c60,void(*)(void*,V2,void*))(t,(V2){0,-55.f-i*38},0);
   riot_label(button,i?"SKIN: PROXIMA":"CHANGE TEAMS");riot_pressed[i]=0;
  }root_set(&riot_page,page);
 }
 void* player=online_local_player();if(!player)return;
 for(int i=0;i<2;i++){
  void* b=rooted(riot_buttons[i]);int pressed=b&&FN(0x83c810,_Bool(*)(void*,void*))(b,0);
  if(pressed&&!riot_pressed[i]){
   if(i){int skin=(player_skin(player)+1)&3;choose_team_trampoline(player,0x5610|skin,0);const char* names[4]={"SKIN 1/4: COOL","SKIN 2/4: NERD","SKIN 3/4: CHILL","SKIN 4/4: WILD"};riot_label(b,names[skin]);}
   else if(INT(player,0x28)>=0&&INT(player,0x28)<2){choose_team_trampoline(player,0x5620|(1-INT(player,0x28)),0);riot_label(b,"TROCA AGENDADA");}
  }riot_pressed[i]=pressed;
 }
}

TRAMP(void,riot_score,(void* rules,void* method))
EXPORT int riot_score_updates=0,riot_wall_ready=0;
static unsigned wall_score[2],wall_rules;
static int riot_copy(char* out,int n,const char* text){for(int i=0;text[i]&&n<190;i++)out[n++]=text[i];return n;}
static int riot_number(char* out,int n,int value){
 if(value<0)value=0;char digits[10];int count=0;
 do{digits[count++]=(char)('0'+value%10);value/=10;}while(value&&count<10);
 while(count)out[n++]=digits[--count];return n;
}
static void* riot_type(const char* assembly_name,const char* name){
 void* domain=FN(0x14a920,void*(*)(void))();
 void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,assembly_name);if(!assembly)return 0;
 void* image=FN(0x14a530,void*(*)(void*))(assembly);
 void* klass=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine",name);if(!klass)return 0;
 return FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
}
EXPORT void riot_score_hook(void* rules,void* method){
 riot_score_updates++;
 riot_score_trampoline(rules,method);
 void* original=PTR(rules,0x30);if(!original)return;
 void* points=PTR(rules,0xa8);
 if(points&&INT(points,0x18)>=2){
  char text[200];int n=riot_copy(text,0,"<color=#E74750>");n=riot_number(text,n,INT(points,0x20));
  n=riot_copy(text,n,"</color>  -  <color=#2468DF>");n=riot_number(text,n,INT(points,0x24));n=riot_copy(text,n,"</color>");text[n]=0;
  FN(0x2405f0,void(*)(void*,void*,void*))(original,str(text),0);
 }
 if(!FN(0x94f3d0,void*(*)(void*,void*))(str("Volley Riot scoreboard backing"),0))return;
 if(rooted(wall_rules)!=rules||!alive(rooted(wall_score[0]))){
  void* type=riot_type("UnityEngine.UIModule","Canvas");if(!type)return;
  for(int i=0;i<2;i++){
   void* score=FN(0xa0b160,void*(*)(void*,void*))(original,0);if(!score)return;
   void* canvas=FN(0x94f240,void*(*)(void*,void*,void*))(gameobject(score),type,0);if(!canvas)return;
   FN(0xece020,void(*)(void*,int,void*))(canvas,2,0);
   void* t=transform(score);FN(0xb74340,void(*)(void*,void*,_Bool,void*))(t,transform(rules),0,0);
   FN(0xb75560,SetVec)(t,(V3){.02f,.02f,.02f},0);
   FN(0xb756b0,SetVec)(t,(V3){0,4.6f,i?12.35f:-12.35f},0);
   FN(0xb75750,void(*)(void*,Q4,void*))(t,i?(Q4){0,0,0,1}:(Q4){0,1,0,0},0);
   root_set(&wall_score[i],score);
  }root_set(&wall_rules,rules);riot_wall_ready=1;
 }
 for(int i=0;i<2;i++){void* score=rooted(wall_score[i]);if(alive(score))FN(0x2405f0,void(*)(void*,void*,void*))(score,PTR(original,0xc8),0);}
}
