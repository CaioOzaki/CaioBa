/* The original Hand.WantsToGrab ORs trigger with grip. Spawn intent must not
 * inherit that combined input: GRAB is reserved for the hand gestures. */
static int spawn_trigger_v24(void* hand){
 if(!hand)return 0;
 void* klass=PTR((void*)base(),0x1542b48),*stat=klass?PTR(klass,0xb8):0;
 void* input=stat?PTR(stat,0):0,*vr=input?PTR(input,0x40):0;
 void* system=PTR((void*)base(),0x1541dc0),*type=PTR((void*)base(),0x1541d98);
 if(!vr||!system||!type)return 0;
 void* controller=FN(0xa2710,void*(*)(int,void*,void*))(BYTE(hand,0x24)?6:5,system,vr);
 /* IController slot 4 = GetTrigger. Slot 1 = GetGrip is never consulted. */
 return controller&&FN(0xa2710,_Bool(*)(int,void*,void*))(4,type,controller);
}
