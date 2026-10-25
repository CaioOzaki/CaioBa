/* Second-touch setting and deterministic original avatar skins. */
EXPORT void high_five_update(void* body);
TRAMP(void,avatar_update,(void* body,void* m))
typedef struct {float x,y;} V2;
typedef struct {float x,y,z,w;} Q4;
static unsigned setting_body;
static int setting_context;
static void* local_avatar_player(void){return network_physics()?online_local_player():rooted(local_player_root);}
EXPORT int both_grips(void){
 void* k=*(void**)(base()+0x1542b48);void* stat=k?PTR(k,0xb8):0;
 void* input=stat?PTR(stat,0):0;void* vr=input?PTR(input,0x40):0;
 void* system=*(void**)(base()+0x1541dc0);void* controller=*(void**)(base()+0x1541d98);
 if(!vr||!system||!controller)return 0;
 for(int i=5;i<=6;i++){
  void* hand=FN(0xa2710,void*(*)(int,void*,void*))(i,system,vr);
  if(!hand||!FN(0xa2710,_Bool(*)(int,void*,void*))(1,controller,hand))return 0;
 }return 1;
}
EXPORT int setting_ready(void* body){
 if(!body||(!doubles_enabled&&!quartet_enabled))return 0;
 void* player=PTR(body,0x168);if(!player||player!=local_avatar_player())return 0;
 int team=INT(player,0x28);if(team<0||team>1)return 0;
 if(network_physics())return net_rally_active&&net_serve_team<0&&net_touch_team==team&&net_touch_count==1;
 void* rules=rooted(rules_root);
 return rules&&BYTE(rules,0x78)&&!BYTE(rules,0x79)&&serve_flight_team<0&&INT(rules,0x7c)==team&&INT(rules,0x9c)==1;
}
static void set_begin(void* body,void* part){
 setting_context=part&&INT(part,0x18)==3&&setting_ready(body)&&both_grips();
 if(setting_context)root_set(&setting_body,body);
}
static void set_end(void){setting_context=0;root_set(&setting_body,0);}
EXPORT V3 setting_arc(V3 from,V3 target){
 float top=(from.y>target.y?from.y:target.y )+3.65f;
 float vy=sqroot(19.62f*(top-from.y));float t=vy/9.81f+sqroot(2*(top-target.y)/9.81f);
 return (V3){(target.x-from.x)/t,vy,(target.z-from.z)/t};
}
static int assisted_set(V3 from,V3* velocity){
 void* body=rooted(setting_body);
 /* The accepted-hit path may already have incremented GameRules touches. */
 if(!setting_context||!body||!both_grips())return 0;
 void* player=PTR(body,0x168);void* rules=rooted(rules_root);if(!rules)return 0;
 int team=INT(player,0x28);if(team<0||team>1||!finitev(from))return 0;
 /* Project the intended attacker onto the near-net attack strip. Keep their
  * lateral position instead of sending every set to a fixed wing. */
 void* receiver=0;float nearest=1.0e20f;V3 receiver_position=from;
 void* sides=PTR(rules,0x60);void* side=sides?PTR(sides,0x20+8*team):0;
 void* list=side?PTR(side,0x28):0;void* items=list?PTR(list,0x10):0;
 int n=list?INT(list,0x18):0;
 if(items&&n>0&&n<=4)for(int i=0;i<n;i++){
  void* candidate=PTR(items,0x20+8*i);if(!candidate||candidate==player||INT(candidate,0x28)!=team)continue;
  /* In quartet prefer the two attacking wings, if roles are available. */
  int role=member_role(candidate);if(quartet_enabled&&role>=0&&role!=1&&role!=3)continue;
  void* humans=side?PTR(side,0x38):0;void* ha=humans?PTR(humans,0x10):0;
  int hn=humans?INT(humans,0x18):0,is_human=0;
  if(ha&&hn>=0&&hn<=4)for(int j=0;j<hn;j++)if(PTR(ha,0x20+8*j)==candidate)is_human=1;
  V3 p=is_human?player_court_position(candidate):position(transform(candidate));if(!finitev(p))continue;
  float score=(p.x-from.x)*(p.x-from.x)+.2f*p.z*p.z;
  if(score<nearest){nearest=score;receiver=candidate;receiver_position=p;}
 }
 float x=receiver_position.x;if(x< -3.65f)x=-3.65f;if(x>3.65f)x=3.65f;
 V3 target={x,2.65f,team==0?-1.15f:1.15f};
 if(receiver&&quartet_enabled)root_set(&attack_receiver[team],receiver);
 *velocity=setting_arc(from,target);return 1;
}
static void* str(const char* text){return FN(0x14b790,void*(*)(const char*))(text);}
static void* find_child(void* parent,const char* path){return parent?FN(0xb73890,void*(*)(void*,void*,void*))(parent,str(path),0):0;}
static int alive(void* o){return o&&FN(0xa0bfb0,_Bool(*)(void*,void*))(o,0);}
static void* gameobject(void* component){return FN(0x94b570,void*(*)(void*,void*))(component,0);}
static int player_skin(void* player){
 int selected=chosen_skin(player);if(selected>=0)return selected;
 if(!network_physics()||player==online_local_player())return preferred_style();
 void* view=FN(0x6054c0,void*(*)(void*,void*))(player,0);
 if(!view)return 18;int owner=FN(0xe6e1b0,int(*)(void*,void*))(view,0),rank=0;
 void* list=online_players();void* array=list?PTR(list,0x10):0;int n=list?INT(list,0x18):0;
 if(!array||n<0||n>8)return 18+((owner>0?owner-1:0)&3);
 for(int i=0;i<n;i++){
  void* other=PTR(array,0x20+i*8);if(!other||other==player)continue;
  void* v=FN(0x6054c0,void*(*)(void*,void*))(other,0);
  if(v&&FN(0xe6e1b0,int(*)(void*,void*))(v,0)<owner)rank++;
 }return 18+(rank&3);
}
typedef struct {unsigned body,materials[2];int skin;} AvatarSkin;
static AvatarSkin skins[8];
static void skin_body(void* body){
 void* player=PTR(body,0x168);if(!player)return;
 AvatarSkin* slot=0;
 for(int i=0;i<8;i++)if(rooted(skins[i].body)==body){slot=&skins[i];break;}
 if(!slot)for(int i=0;i<8;i++)if(!alive(rooted(skins[i].body))){slot=&skins[i];break;}
 if(!slot)return;
 if(rooted(slot->body)!=body){
  root_set(&slot->body,body);slot->skin=-1;
  const char* paths[2]={"Physical Head/Visual Head Root/Head","Physical Torso/Scaler (1)/Body"};
  for(int i=0;i<2;i++){
   void* t=find_child(transform(body),paths[i]);void* renderer=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;
   root_set(&slot->materials[i],renderer?FN(0xa1ae90,void*(*)(void*,void*))(renderer,0):0);
  }
 }
 int skin=player_skin(player);if(slot->skin==skin)return;
 slot->skin=skin;
 for(int i=0;i<2;i++){void* mat=rooted(slot->materials[i]);if(mat){
  int index=i==0?skin%9:skin/9;
  FN(0x9566d0,void(*)(void*,V2,void*))(mat,(V2){(index%3)/3.f,(2-index/3)/3.f},0);
  FN(0x956610,void(*)(void*,Q4,void*))(mat,(Q4){1,1,1,1},0);
 }}
}
typedef struct {unsigned root;Q4 saved,open;} Finger;
static Finger fingers[30];static int finger_count,feedback_active;static unsigned feedback_body;
static Q4 normalized(Q4 q){float r=sqroot(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w);return (Q4){q.x/r,q.y/r,q.z/r,q.w/r};}
static void restore_fingers(void){
 for(int i=0;i<finger_count;i++){void* t=rooted(fingers[i].root);if(alive(t))FN(0xb754c0,void(*)(void*,Q4,void*))(t,fingers[i].saved,0);root_set(&fingers[i].root,0);}
 finger_count=0;feedback_active=0;root_set(&feedback_body,0);
}
static void setting_feedback(void* body){
 if(PTR(body,0x168)!=local_avatar_player()||!setting_ready(body)||!both_grips())return;
 const char* paths[2]={"Hand Root L","Hand Root R"};
 for(int side=0;side<2;side++){
  void* root=find_child(transform(body),paths[side]);void* open=find_child(root,"Open"),*closed=find_child(root,"Closed");
  if(open)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(open),1,0);
  if(closed)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(closed),0,0);
 }
}
EXPORT void avatar_update_hook(void* body,void* m){
 avatar_update_trampoline(body,m);skin_body(body);setting_feedback(body);high_five_update(body);cloudcourt_avatar_tick(body);
}
