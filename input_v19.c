/* v19 UI input and feedback. Include after the common Unity/GC helpers.
 * CurvedUI accepts held state and computes its own down/release edges.
 * InterfaceFuncInvoker0 at 0xa2710 tail-jumps to the resolved method, so a
 * float-returning slot preserves XMM0 (verified against the original x64).
 */
static unsigned ui_v19_controller[2];
static unsigned char ui_v19_analog_held[2];
static unsigned ui_v19_click_source,ui_v19_click_clip,ui_v19_button_name;
static void (*ui_v23_ignore_listener_pause)(void*,_Bool);
static int ui_v23_pause_api_checked;

static void ui_audio_pause_safe_v23(void* source){
 /* Headset focus can pause AudioListener independently of Time.timeScale.
  * Keep only interface feedback audible; never unpause the global listener.
  * The managed setter is stripped in this build, but its Unity icall remains. */
 if(!ui_v23_pause_api_checked){
  ui_v23_ignore_listener_pause=(void(*)(void*,_Bool))
   FN(0x14b030,void*(*)(const char*))("UnityEngine.AudioSource::set_ignoreListenerPause");
  ui_v23_pause_api_checked=1;
 }
 if(ui_v23_ignore_listener_pause)ui_v23_ignore_listener_pause(source,1);
}

static int ui_input_v19(int original_value){
 int pressed=original_value||FN(0x452d40,_Bool(*)(int,int,void*))(1,2,0);
 void* klass=PTR((void*)base(),0x1542b48),*stat=klass?PTR(klass,0xb8):0;
 void* input=stat?PTR(stat,0):0,*vr=input?PTR(input,0x40):0;
 void* system=PTR((void*)base(),0x1541dc0),*controller_type=PTR((void*)base(),0x1541d98);
 for(int side=0;side<2;side++){
  void* controller=vr&&system&&controller_type?FN(0xa2710,void*(*)(int,void*,void*))(side+5,system,vr):0;
  if(rooted(ui_v19_controller[side])!=controller){
   root_set(&ui_v19_controller[side],controller);ui_v19_analog_held[side]=0;
  }
  if(!controller){ui_v19_analog_held[side]=0;continue;}
  int digital=FN(0xa2710,_Bool(*)(int,void*,void*))(4,controller_type,controller);
  float analog=FN(0xa2710,float(*)(int,void*,void*))(5,controller_type,controller);
  if(!__builtin_isfinite(analog))analog=0;
  if(digital||analog>=.60f)ui_v19_analog_held[side]=1;
  else if(analog<=.35f)ui_v19_analog_held[side]=0;
  pressed|=digital||ui_v19_analog_held[side];
  /* Retain the existing SteamVR A fallback in addition to OVRInput.Get. */
  if(side==1&&PTR(controller,0)==PTR((void*)base(),0x15412b0)){
   void* device=PTR(controller,0x10);
   if(device)pressed|=FN(0x40d5a0,_Bool(*)(void*,int,void*))(device,7,0);
  }
 }
 return pressed!=0;
}

static int ui_button_valid_v19(void* button){
 return button&&FN(0x478bf0,_Bool(*)(void*,void*))(button,0)
              &&FN(0x83c7f0,_Bool(*)(void*,void*))(button,0);
}

static void ui_click_v19(void* button){
 if(!ui_button_valid_v19(button))return;
 if(!alive(rooted(ui_v19_click_source))){
  void* input_class=PTR((void*)base(),0x1542b48),*stat=input_class?PTR(input_class,0xb8):0;
  void* input=stat?PTR(stat,0):0,*owner=input?input:button;
  void* domain=FN(0x14a920,void*(*)(void))();
  void* assembly=domain?FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.AudioModule"):0;
  void* image=assembly?FN(0x14a530,void*(*)(void*))(assembly):0;
  void* klass=image?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","AudioSource"):0;
  if(!klass)return;
  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass));
  void* source=type?FN(0x94f240,void*(*)(void*,void*,void*))(gameobject(owner),type,0):0;
  if(!source)return;
  FN(0xebc590,void(*)(void*,float,void*))(source,0,0); /* 2D: no distance attenuation. */
  FN(0xebc760,void(*)(void*,float,void*))(source,.55f,0);
  FN(0xebc370,void(*)(void*,_Bool,void*))(source,0,0);
  FN(0xebc500,void(*)(void*,_Bool,void*))(source,0,0);
  FN(0xebc460,void(*)(void*,_Bool,void*))(source,0,0);
  ui_audio_pause_safe_v23(source);
  root_set(&ui_v19_click_source,source);
 }
 if(!alive(rooted(ui_v19_click_clip))){
  void* clip=FN(0xeba090,void*(*)(void*,int,int,int,_Bool,void*))(str("Cloudcourt_UI_Click"),1764,1,22050,0,0);
  if(!clip)return;
  void* corlib=FN(0x14acb0,void*(*)(void))();
  void* single=corlib?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(corlib,"System","Single"):0;
  void* samples=single?FN(0x14a4f0,void*(*)(void*,U64))(single,1764):0;
  if(!samples)return;
  unsigned seed=0x43435549;float phase=0;
  for(int i=0;i<1764;i++){
   seed=seed*1664525u+1013904223u;
   float noise=((seed>>8)&65535)/32768.f-1.f;
   phase+=.0522f;if(phase>=1)phase-=1;
   float triangle=phase<.5f?4*phase-1:3-4*phase;
   float e=1-i/1764.f;e*=e;e*=e;
   float attack=i<66?i/66.f:1.f;
   FLT(samples,0x20+i*4)=(triangle*.45f+noise*.16f)*e*attack;
  }
  if(!FN(0xeba5f0,_Bool(*)(void*,void*,int,void*))(clip,samples,0,0))return;
  root_set(&ui_v19_click_clip,clip);
 }
 void* source=rooted(ui_v19_click_source);
 FN(0xebc2d0,void(*)(void*,void*,void*))(source,rooted(ui_v19_click_clip),0);
 FN(0xebbe30,void(*)(void*,void*))(source,0);
}

static int ui_pointer_over_button_v19(void){
 /* Reading the cached instance avoids get_Instance creating a new module. */
 void* klass=PTR((void*)base(),0x1542440),*stat=klass?PTR(klass,0xb8):0;
 void* module=stat?PTR(stat,8):0,*go=module?PTR(module,0xf8):0;
 if(!alive(go))return 0;
 if(!rooted(ui_v19_button_name))root_set(&ui_v19_button_name,str("Button"));
 for(int depth=0;go&&depth<8;depth++){
  void* button=FN(0x94f410,void*(*)(void*,void*,void*))(go,rooted(ui_v19_button_name),0);
  /* A locked button still represents UI intent, not a practice-ball request. */
  if(alive(button))return 1;
  void* t=FN(0x94fb00,void*(*)(void*,void*))(go,0);
  void* parent=t?FN(0xb739d0,void*(*)(void*,void*))(t,0):0;
  go=parent?gameobject(parent):0;
 }
 return 0;
}
