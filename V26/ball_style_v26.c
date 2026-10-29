/* One instance material per live ball; no Photon ownership is needed for art.
 * Both peers use their loaded Environment identity, including the practice room.
 * The authored mesh uses the left half of the dual atlas. */
typedef struct {unsigned ball,material,environment,renderer,shared;int beach,retry;} BallStyleV26;
static BallStyleV26 ball_styles_v26[8];
static void ball_style_release_v26(BallStyleV26* s){
 void* material=rooted(s->material);
 void* renderer=rooted(s->renderer);void* shared=rooted(s->shared);
 if(alive(renderer)&&alive(shared))FN(0xa1b0e0,void(*)(void*,void*,void*))(renderer,shared,0);
 if(alive(material))FN(0xa0ab40,void(*)(void*,void*))(material,0);
 root_set(&s->material,0);root_set(&s->ball,0);root_set(&s->environment,0);
 root_set(&s->renderer,0);root_set(&s->shared,0);
 s->beach=-1;s->retry=0;
}
static void ball_style_reset_v26(void){for(int i=0;i<8;i++)ball_style_release_v26(&ball_styles_v26[i]);}
EXPORT void ball_appearance_v26(void* ball){
 if(!ball)return;
 void* klass=PTR((void*)base(),0x15422a0);void* stat=klass?PTR(klass,0xb8):0;
 void* environment=stat?PTR(stat,0):0;if(!alive(environment))return;
 int beach=!v19_word(PTR(environment,0x18),"Indoor");
 BallStyleV26* s=0;
 for(int i=0;i<8;i++)if(rooted(ball_styles_v26[i].ball)==ball){s=&ball_styles_v26[i];break;}
 if(!s)for(int i=0;i<8;i++)if(!alive(rooted(ball_styles_v26[i].ball))){
  s=&ball_styles_v26[i];ball_style_release_v26(s);root_set(&s->ball,ball);break;
 }
 if(!s)return;
 if(s->retry>0){s->retry--;return;}
 if(!alive(rooted(s->material))){
  void* root=transform(ball);void* t=find_child(root,"VisualVolleyball/RegularMesh/DavidVolleyball");
  void* renderer=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;
  void* shared=renderer?FN(0xa1af10,void*(*)(void*,void*))(renderer,0):0;
  if(rooted(s->renderer)==renderer&&alive(rooted(s->shared))){
   /* Recover if a scene unload destroyed an instance before the ball itself. */
   shared=rooted(s->shared);FN(0xa1b0e0,void(*)(void*,void*,void*))(renderer,shared,0);
  }
  void* material=renderer?FN(0xa1ae90,void*(*)(void*,void*))(renderer,0):0;
  if(!material){s->retry=29;return;}
  root_set(&s->material,material);root_set(&s->renderer,renderer);root_set(&s->shared,shared);s->beach=-1;
  /* The original low-detail renderer shares the parent GO. Keep that parent
   * alive, showing only our dedicated child, without touching ball colliders. */
  FN(0xa1b2f0,void(*)(void*,_Bool,void*))(renderer,1,0);
  void* regular=find_child(root,"VisualVolleyball/RegularMesh");
  void* fallback=regular?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(regular),str("MeshRenderer"),0):0;
  if(fallback)FN(0xa1b2f0,void(*)(void*,_Bool,void*))(fallback,0,0);
 }
 if(s->beach==beach&&rooted(s->environment)==environment)return;
 FN(0x9566d0,void(*)(void*,V2,void*))(rooted(s->material),(V2){beach?.5f:0,0},0);
 root_set(&s->environment,environment);s->beach=beach;
}
