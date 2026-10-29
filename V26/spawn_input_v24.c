/* Spawn must read the trigger separately from the native grip/trigger OR.
 * v25: some VR backends report trigger pressure without a digital press.
 * Keep the same tested .60/.35 analog hysteresis used by the menu. */
typedef struct {unsigned controller;unsigned char held;} SpawnTriggerV25;
static SpawnTriggerV25 spawn_triggers_v25[2];
static int spawn_metadata_v25;
TRAMP(_Bool,hand_input_v25,(void* hand,void* m))
static int spawn_trigger_v24(void* hand){
 if(!hand)return 0;
 /* Preserve WantsToGrab's original one-time metadata initialization before
  * reading its TypeInfo globals, including the first lobby polling frame.
  * Leave the original flag to its own code; initialization is idempotent. */
 if(!spawn_metadata_v25){
  if(!BYTE((void*)base(),0x150060e))FN(0x1c21b0,void(*)(unsigned))(INT((void*)base(),0x12a144c));
  spawn_metadata_v25=1;
 }
 int side=BYTE(hand,0x24)?1:0;SpawnTriggerV25* state=&spawn_triggers_v25[side];
 void* klass=PTR((void*)base(),0x1542b48),*stat=klass?PTR(klass,0xb8):0;
 void* input=stat?PTR(stat,0):0,*vr=input?PTR(input,0x40):0;
 void* system=PTR((void*)base(),0x1541dc0),*type=PTR((void*)base(),0x1541d98);
 void* controller=vr&&system&&type?FN(0xa2710,void*(*)(int,void*,void*))(side?6:5,system,vr):0;
 if(rooted(state->controller)!=controller){root_set(&state->controller,controller);state->held=0;}
 if(!controller){state->held=0;return 0;}
 int digital=FN(0xa2710,_Bool(*)(int,void*,void*))(4,type,controller);
 float analog=FN(0xa2710,float(*)(int,void*,void*))(5,type,controller);
 if(!__builtin_isfinite(analog))analog=0;
 if(digital||analog>=.60f)state->held=1;
 else if(analog<=.35f)state->held=0;
 /* GetGrip is deliberately absent from spawn intent. */
 return digital||state->held;
}
EXPORT _Bool hand_input_v25_hook(void* hand,void* m){
 if(!hand)return 0;
 if(!offline()&&!network_physics())return hand_input_v25_trampoline(hand,m);
 if(network_physics()){
  void* player=online_local_player(),*body=player?PTR(player,0x80):0;
  void* ht=transform(hand),*bt=body?transform(body):0;
  if(!ht||!bt||!FN(12008720,_Bool(*)(void*,void*,void*))(ht,bt,0))
   return hand_input_v25_trampoline(hand,m);
 }
 int trigger=spawn_trigger_v24(hand);
 /* A missing controller must not enter the original null-throwing reader. */
 if(!rooted(spawn_triggers_v25[BYTE(hand,0x24)?1:0].controller))return 0;
 /* Native Hand.Update uses this predicate twice, and WantsToRelease negates
  * it. Analog input must reach this path as well as the spawn gate, otherwise
  * Hand.Update never asks to attach the waiting/practice ball. Existing grip
  * holding/release and the native interaction/throw methods are retained. */
 return hand_input_v25_trampoline(hand,m)||trigger;
}
