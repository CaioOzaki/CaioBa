/* Local accepted-contact feedback. Included after comfort_v14.c.
 * Audio replaces the existing BallHit clip at its original one-shot call.
 * Haptics wrap only the two accepted-hit interface dispatch call sites; UI
 * and every other controller effect retain their original implementation. */
enum {HIT_WEAK_V29=0,HIT_RECEIVE_V29=1,HIT_SPIKE_V29=2};
typedef struct {
 void* body;void* ball;void* haptic_controller[2];
 V3 incoming,hand;int active,accepted,kind,audio_seen,haptic_count,assisted;
} HitContactV29;
static HitContactV29 hit_contact_v29;
static unsigned hit_clips_v29[3];
static int hit_clip_failed_v29[3];

static int hit_classify_v29(V3 incoming,V3 hand,V3 outgoing,int assisted){
 if(!finitev(incoming)||!finitev(hand)||!finitev(outgoing))return HIT_WEAK_V29;
 float i=dot(incoming,incoming),h=dot(hand,hand),o=dot(outgoing,outgoing);
 if(!__builtin_isfinite(i)||!__builtin_isfinite(h)||!__builtin_isfinite(o)||i>10000||h>2500||o>10000)return HIT_WEAK_V29;
 /* A fast incoming ball alone is a reception. A forceful intentional swing
  * plus a fast driven return is required for a spike. Overhead placement is
  * deliberately irrelevant, so a soft overhead set never earns spike feedback. */
 if(!assisted&&h>=3.2f*3.2f&&o>=8.5f*8.5f&&
    ((hand.y<-.75f&&outgoing.y<1.5f)||(h>=5.5f*5.5f&&o>=11.f*11.f&&outgoing.y<3.f)))return HIT_SPIKE_V29;
 if(assisted||(i>=3.f*3.f&&h<=2.6f*2.6f))return HIT_RECEIVE_V29;
 return HIT_WEAK_V29;
}
static void hit_feedback_end_v29(void){
 /* Borrowed pointers are valid only during the synchronous collision call. */
 hit_contact_v29=(HitContactV29){0};
}
static void hit_feedback_begin_v29(void* body,void* part,void* ball,void* collision){
 hit_feedback_end_v29();
 if(!body||!part||!ball||!collision)return;
 void* local=local_avatar_player();
 if(!local||PTR(body,0x168)!=local)return;
 int type=INT(part,0x18);if(type<1||type>4||!BYTE(ball,0x88))return;
 void* contacts=PTR(collision,0x40);if(!contacts)contacts=PTR(collision,0x48);
 if(!contacts||INT(collision,0x38)<1||*(U64*)((char*)contacts+0x18)<1)return;
 V3 p=*(V3*)((char*)contacts+0x20),v=*(V3*)((char*)ball+0x8c);
 if(!finitev(p)||!finitev(v))return;
 V3 hand=FN(0xeea0e0,V3(*)(void*,V3,void*))(part,p,0);
 if(!finitev(hand))return;
 hit_contact_v29.body=body;hit_contact_v29.ball=ball;
 hit_contact_v29.incoming=v;hit_contact_v29.hand=hand;
 hit_contact_v29.active=1;hit_contact_v29.assisted=setting_context;
}
static void hit_feedback_accept_v29(void* ball,V3 outgoing){
 HitContactV29* c=&hit_contact_v29;
 if(!c->active||c->ball!=ball||!finitev(outgoing)||c->accepted)return;
 c->kind=hit_classify_v29(c->incoming,c->hand,outgoing,c->assisted);c->accepted=1;
}
static int hit_ascii_v29(const char* a,const char* b){
 if(!a||!b)return 0;while(*a&&*a==*b){a++;b++;}return *a==*b;
}
static int hit_effect_name_v29(void* effect){
 void* s=effect?PTR(effect,0x10):0;if(!s||INT(s,0x10)!=7)return 0;
 const unsigned short* p=(const unsigned short*)((char*)s+0x14);
 const char* t="BallHit";for(int i=0;i<7;i++)if(p[i]!=(unsigned short)t[i])return 0;return 1;
}
static int hit_sample_count_v29(int kind){return kind==HIT_SPIKE_V29?3087:kind==HIT_RECEIVE_V29?2425:1654;}
static void hit_synthesize_v29(float* pcm,int count,int kind){
 /* Two damped membrane modes and a short filtered skin transient. Original
  * synthesis, deterministic, mono 22.05 kHz. No recording or external file. */
 float a=0,b=0,pa,pb,ca,cb,body=1,skin=1,low=0;
 float decay=kind==2?.9976f:kind==1?.9971f:.9963f;
 float skin_decay=kind==2?.9915f:kind==1?.988f:.982f;
 float gain=kind==2?.64f:kind==1?.40f:.24f;
 if(kind==2){ca=1.998520f;pa=.038456f;cb=1.934590f;pb=.253650f;}
 else if(kind==1){ca=1.997514f;pa=.049846f;cb=1.959211f;pb=.200932f;}
 else {ca=1.994927f;pa=.071178f;cb=1.936780f;pb=.249450f;}
 float aa=-pa,bb=-pb;unsigned noise=0x9e3779b9u+(unsigned)kind*0x450f3u;
 for(int n=0;n<count;n++){
  float na=ca*a-aa,nb=cb*b-bb;aa=a;a=na;bb=b;b=nb;
  noise^=noise<<13;noise^=noise>>17;noise^=noise<<5;
  float white=(int)(noise&65535)/32768.f-1.f;low+=(white-low)*.35f;
  float attack=n<18?n/18.f:1.f,tail=count-n<110?(count-n)/110.f:1.f;
  float sample=(a*.63f+b*.10f)*body+(white-low)*skin*.35f;
  pcm[n]=sample*attack*tail*gain;body*=decay;skin*=skin_decay;
 }
}
static void* hit_clip_v29(int kind){
 if(kind<0||kind>2)return 0;
 void* old=rooted(hit_clips_v29[kind]);if(alive(old))return old;
 if(hit_clip_failed_v29[kind])return 0; /* one failed creation attempt per kind */
 root_set(&hit_clips_v29[kind],0);
 int count=hit_sample_count_v29(kind);
 const char* names[3]={"Cloudcourt_Original_Weak_Touch_v29","Cloudcourt_Original_Controlled_Receive_v29","Cloudcourt_Original_Strong_Spike_v29"};
 void* clip=FN(0xeba090,void*(*)(void*,int,int,int,_Bool,void*))(str(names[kind]),count,1,22050,0,0);
 if(!clip){hit_clip_failed_v29[kind]=1;return 0;}
 root_set(&hit_clips_v29[kind],clip);
 void* corlib=FN(0x14acb0,void*(*)(void))();
 void* single=corlib?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(corlib,"System","Single"):0;
 void* samples=single?FN(0x14a4f0,void*(*)(void*,U64))(single,count):0;
 if(samples){
  unsigned sample_root=0;root_set(&sample_root,samples);
  hit_synthesize_v29((float*)((char*)samples+0x20),count,kind);
  int ok=FN(0xeba5f0,_Bool(*)(void*,void*,int,void*))(clip,samples,0,0);
  root_set(&sample_root,0);if(ok)return clip;
 }
 FN(0xa0ab40,void(*)(void*,void*))(clip,0);root_set(&hit_clips_v29[kind],0);
 hit_clip_failed_v29[kind]=1;return 0;
}
static void* hit_feedback_clip_v29(void* original,void* effect){
 HitContactV29* c=&hit_contact_v29;
 if(!c->active||!c->accepted||!hit_effect_name_v29(effect))return original;
 c->audio_seen=1;void* clip=hit_clip_v29(c->kind);return clip?clip:original;
}
static int hit_haptic_v29(void* controller,int kind){
 if(!controller||!PTR(controller,0))return 0;
 const char* name=FN(0x14a6a0,const char*(*)(void*))(PTR(controller,0));
 int oculus=hit_ascii_v29(name,"OculusVRController"),openvr=hit_ascii_v29(name,"OpenVRController");
 if(!oculus&&!openvr)return 0;
 int host_offset=oculus?0x20:0x48,handle_offset=oculus?0x28:0x58;
 void* host=PTR(controller,host_offset);if(!alive(host))return 0;
 const float amp[3]={.20f,.43f,.78f},duration[3]={.024f,.052f,.092f},frequency[3]={.45f,.65f,.85f};
 void* routine=oculus?
  FN(0x383bf0,void*(*)(void*,float,float,float,void*))(controller,frequency[kind],amp[kind],duration[kind],0):
  FN(0x384fd0,void*(*)(void*,float,float,void*))(controller,amp[kind],duration[kind],0);
 if(!routine)return 0;
 /* Preserve native single-coroutine ownership: cancel its previous pulse and
  * save the new Coroutine on exactly the original controller field. Native
  * coroutine completion ends the pulse: Oculus sets amplitude to zero; OpenVR
  * stops emitting its finite impulses. */
 void* prior=PTR(controller,handle_offset);
 if(prior)FN(0xa0a5e0,void(*)(void*,void*,void*))(host,prior,0);
 managed_field(controller,handle_offset,0);
 void* running=FN(0xa0a0c0,void*(*)(void*,void*,void*))(host,routine,0);
 if(!running)return 0;managed_field(controller,handle_offset,running);return 1;
}
EXPORT void hit_haptic_dispatch_v29(int slot,void* interface_type,void* controller,int effect){
 HitContactV29* c=&hit_contact_v29;
 if(c->active&&c->accepted&&slot==17&&effect==1&&controller){
  for(int i=0;i<c->haptic_count;i++)if(c->haptic_controller[i]==controller)return;
  if(c->haptic_count<2&&hit_haptic_v29(controller,c->kind)){
   c->haptic_controller[c->haptic_count++]=controller;return;
  }
 }
 FN(0xa3800,void(*)(int,void*,void*,int))(slot,interface_type,controller,effect);
}


