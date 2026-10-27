/* Height adaptation, point explanations and local high-five feedback. */
TRAMP(void,bot_jump,(void* bot,void* m))
EXPORT void bot_jump_hook(void* bot,void* m){
 bot_jump_trampoline(bot,m);
 if(doubles_enabled||quartet_enabled){
  float v=FLT(bot,0x98);FLT(bot,0x98)=sqroot(v*v+2*9.81f*.7f);
  FLT(bot,0xa0)=2*FLT(bot,0x98)/9.81f;
 }
}
EXPORT void four_point_hook(void* rules,int winner,void* m){point_reason=1;FN(0x2533a0,void(*)(void*,int,void*))(rules,winner,m);}
EXPORT void double_point_hook(void* rules,int winner,void* m){point_reason=2;FN(0x2533a0,void(*)(void*,int,void*))(rules,winner,m);}
EXPORT void ground_point_hook(void* rules,int winner,void* m){
 point_reason=3;
 void* k=*(void**)(base()+0x15426f0);void* s=k?PTR(k,0xb8):0;void* ball=s?PTR(s,0):0;
 if(ball){V3 p=position(transform(ball));landing_prepare_v20(ball,p);if(!(p.x> -4.5f&&p.x<4.5f&&p.z> -9.f&&p.z<9.f))point_reason=4;}
 if(serve_flight_team>=0)point_reason=6;
 FN(0x2533a0,void(*)(void*,int,void*))(rules,winner,m);
}
EXPORT void* score_box_hook(void* klass,void* value){
 int team=*(int*)value;
 int packed=team;
 if(team>=0&&team<=1&&(offline()||network_physics()))packed=0x4300|team|((point_reason?point_reason:3)<<1)|landing_wire_flags_v20()|celebration_wire_v24(rooted(rules_root),team);
 return FN(0x14ba70,void*(*)(void*,void*))(klass,&packed);
}
static void point_message(void* rules,int team,int reason){
 static const char* causes[2][8]={
  {"","Four touches by red team","Double touch by red team","Ball down on red side","Out: last touch by red team","Red team served inside the court","Service fault by red team","Serve blocked by red team"},
  {"","Four touches by blue team","Double touch by blue team","Ball down on blue side","Out: last touch by blue team","Blue team served inside the court","Service fault by blue team","Serve blocked by blue team"}
 };
 if(!rules||team<0||team>1||reason<1||reason>7)return;
 void* text=PTR(rules,0x28);if(!text)return;
 const char* parts[4]={team?"<size=70%><color=#FF7278>RED +1</color></size>\n<size=42%>":"<size=70%><color=#75CFFF>BLUE +1</color></size>\n<size=42%>",causes[team][reason],"</size>",0};
 char message[240];int n=0;
 for(int p=0;parts[p];p++)for(int i=0;parts[p][i]&&n<239;i++)message[n++]=parts[p][i];message[n]=0;
 FN(0x2405f0,void(*)(void*,void*,void*))(text,str(message),0);
 score_outline_tmp_force_v21(text);
}
static unsigned clap_clip,clap_source,clap_body;
static unsigned hold_hand[2];static V3 hold_position;static float hold_time,clap_cooldown;
typedef struct {unsigned body;float distance[4];V3 relative[4];unsigned char armed[4],known[4];} ClapPeer;
static ClapPeer clap_peers[8];
static void* hand_target(void* body,int right){
 void* arm=body?PTR(body,right?0x48:0x40):0;
 void* hand=arm?PTR(arm,0x28):0;
 return hand?transform(hand):(arm?PTR(arm,0x10):0);
}
static void play_clap(void* body){
 if(!alive(rooted(clap_source))||rooted(clap_body)!=body){
  void* domain=FN(0x14a920,void*(*)(void))();
  void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.AudioModule");
  if(!assembly)return;void* img=FN(0x14a530,void*(*)(void*))(assembly);
  void* klass=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine","AudioSource");if(!klass)return;
  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
  void* source=FN(0x94f240,void*(*)(void*,void*,void*))(gameobject(body),type,0);if(!source)return;
  root_set(&clap_source,source);root_set(&clap_body,body);
  FN(0xebc590,void(*)(void*,float,void*))(source,1,0);FN(0xebc760,void(*)(void*,float,void*))(source,.65f,0);
 }
 if(!alive(rooted(clap_clip))){
  void* clip=FN(0xeba090,void*(*)(void*,int,int,int,_Bool,void*))(str("Cloudcourt_Clap"),4410,1,22050,0,0);if(!clip)return;
  root_set(&clap_clip,clip);
  void* corlib=FN(0x14acb0,void*(*)(void))();void* single=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(corlib,"System","Single");
  void* samples=FN(0x14a4f0,void*(*)(void*,U64))(single,4410);if(!samples)return;
  unsigned seed=0x4341494f;float last=0;
  for(int i=0;i<4410;i++){seed=seed*1664525u+1013904223u;float noise=((seed>>8)&65535)/32768.0f-1;
   float e=1-i/4410.0f;e=e*e*e;e*=e;FLT(samples,0x20+i*4)=(noise-last*.55f)*e*.55f;last=noise;}
  if(!FN(0xeba5f0,_Bool(*)(void*,void*,int,void*))(clip,samples,0,0))return;
 }
 void* source=rooted(clap_source);FN(0xebc2d0,void(*)(void*,void*,void*))(source,rooted(clap_clip),0);FN(0xebbe30,void(*)(void*,void*))(source,0);
}
static void apply_high_five(void){
 if(hold_time<=0)return;
 for(int i=0;i<2;i++){void* t=rooted(hold_hand[i]);if(alive(t))FN(0xb756b0,SetVec)(t,hold_position,0);}
}
EXPORT void high_five_update(void* body){
 if(!network_physics())return;
 if(PTR(body,0x168)!=online_local_player()){apply_high_five();return;}
 float dt=FN(0xb72b10,float(*)(void*))(0);if(dt<=0||dt>.25f)return;
 hold_time-=dt;clap_cooldown-=dt;

 void* list=online_players();void* array=list?PTR(list,0x10):0;int count=list?INT(list,0x18):0;
 if(!array||count<1||count>8)return;
 for(int i=0;i<count;i++){
  void* other=PTR(array,0x20+i*8);void* remote=other?PTR(other,0x80):0;if(!remote||remote==body)continue;
  ClapPeer* peer=&clap_peers[i];if(rooted(peer->body)!=remote){root_set(&peer->body,remote);for(int j=0;j<4;j++){peer->known[j]=0;peer->armed[j]=0;}}
  for(int left=0;left<2;left++)for(int right=0;right<2;right++){
   void* a=hand_target(body,left);void* b=hand_target(remote,right);if(!a||!b)continue;
   V3 p=position(a),q=position(b),diff=sub(p,q);float d=sqroot(dot(diff,diff));int j=left*2+right;
   if(d>.32f)peer->armed[j]=1;
   V3 travel=sub(diff,peer->relative[j]);float length=dot(travel,travel),t=length>1e-8f?-dot(peer->relative[j],travel)/length:0;
   if(t<0)t=0;if(t>1)t=1;V3 closest=add(peer->relative[j],mul(travel,t));
   int touching=d<.22f||(peer->known[j]&&dot(closest,closest)<.0225f);
   if(peer->known[j]&&peer->armed[j]&&touching&&clap_cooldown<=0){
    hold_position=mul(add(p,q),.5f);hold_time=.16f;clap_cooldown=.7f;peer->armed[j]=0;
    root_set(&hold_hand[0],a);root_set(&hold_hand[1],b);play_clap(body);
   }
   peer->known[j]=1;peer->distance[j]=d;peer->relative[j]=diff;
  }
 }
 apply_high_five();
}
