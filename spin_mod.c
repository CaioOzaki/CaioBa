/* Build-specific experimental patch. No external imports or network calls.
 * Unity 2019.4.5f1, Volleyball Fever Steam build 9216628 only.
 * Windows x64 ABI and IL2CPP field layouts verified against local metadata.
 */
typedef unsigned long long U64;
typedef struct {float x,y,z;} V3;
int DllMain(void* module,unsigned reason,void* reserved){return 1;}
extern char __ImageBase;
#ifndef PATCH_DELTA
#define PATCH_DELTA 0
#endif
#define EXPORT __declspec(dllexport)
EXPORT __attribute__((naked)) void collision_trampoline(void* a,void* b,void* c,void* d,void* e){__asm__(".rept 32; int3; .endr");}
EXPORT __attribute__((naked)) void random_trampoline(void* a,void* b){__asm__(".rept 32; int3; .endr");}
EXPORT __attribute__((naked)) void late_trampoline(void* a,void* b){__asm__(".rept 32; int3; .endr");}
EXPORT float spin_transfer=0.60f;
EXPORT float spin_limit=60.0f;
EXPORT float magnus_coefficient=0.005f;
EXPORT float magnus_acceleration_limit=8.0f;
EXPORT float physics_interval=1.0f/30.0f;
EXPORT U64 frame_callbacks=0;
EXPORT U64 physics_steps=0;
static float pending_time;
static void* pending_ball;
static V3 pending_spin;
static void* spinning_ball;
static int pending_valid;
static U64 base(void){return (U64)&__ImageBase-PATCH_DELTA;}
#define FN(rva,type) ((type)(base()+(rva)))
static V3 add(V3 a,V3 b){return (V3){a.x+b.x,a.y+b.y,a.z+b.z};}
static V3 mul(V3 a,float s){return (V3){a.x*s,a.y*s,a.z*s};}
static V3 sub(V3 a,V3 b){return add(a,mul(b,-1));}
static float dot(V3 a,V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static V3 cross(V3 a,V3 b){return (V3){a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
static float sqroot(float x){return __builtin_sqrtf(x);}
static V3 clampv(V3 a,float max){float d=dot(a,a);return d>max*max?mul(a,max/sqroot(d)):a;}
static int finitev(V3 a){return __builtin_isfinite(a.x)&&__builtin_isfinite(a.y)&&__builtin_isfinite(a.z);}
EXPORT V3 compute_spin(V3 r,V3 hand,V3 velocity,V3 omega,float transfer,float limit){
    float r2=dot(r,r);if(r2<0.0001f||!finitev(r)||!finitev(hand)||!finitev(velocity)||!finitev(omega))return (V3){0,0,0};
    V3 relative=sub(hand,add(velocity,cross(omega,r)));
    /* r x relative automatically discards its normal component. Thin shell
       inertia gives 0.60 for a sticking tangential impulse against a hand. */
    return clampv(add(omega,mul(cross(r,relative),transfer/r2)),limit);
}
EXPORT V3 compute_magnus(V3 omega,V3 velocity,float coefficient,float max){
    if(!finitev(omega)||!finitev(velocity))return (V3){0,0,0};
    return clampv(mul(cross(omega,velocity),coefficient),max);
}
typedef V3 (*GetVec)(void*,void*);
typedef void (*SetVec)(void*,V3,void*);
typedef void (*SetFloat)(void*,float,void*);
typedef _Bool (*GetBool)(void*,void*);
static int offline(void){return FN(0x61fbf0,_Bool(*)(void*))(0);}
static int network_physics(void);
static void reception_begin(void* body);
static void reception_end(void);
static void set_begin(void* body,void* part);
static void set_end(void);
static int assisted_set(V3 position,V3* velocity);
static void setspin(void* ball,V3 spin){
    void* rb=*(void**)((char*)ball+0x98);
    void* local=*(void**)((char*)ball+0x30);
    if(rb){FN(0xec5ea0,SetFloat)(rb,spin_limit,0);FN(0xec5cd0,SetVec)(rb,spin,0);}
    if(local&&local!=rb){FN(0xec5ea0,SetFloat)(local,spin_limit,0);FN(0xec5cd0,SetVec)(local,spin,0);}
}
EXPORT void collision_hook(void* body,void* part,void* ball,void* collision,void* method){
    /* Keep original hit validation, scoring, normal bounce and ownership. */
    reception_begin(body);
    set_begin(body,part);
    pending_valid=0;
    if(part&&ball&&collision&&(offline()||network_physics())&&*(int*)((char*)part+0x18)==3&&*((unsigned char*)ball+0x88)){
        void* rb=*(void**)((char*)ball+0x98);
        void* contacts=*(void**)((char*)collision+0x40);
        if(!contacts)contacts=*(void**)((char*)collision+0x48);
        if(rb&&contacts&&*(int*)((char*)collision+0x38)>0&&*(U64*)((char*)contacts+0x18)>0){
            V3 point=*(V3*)((char*)contacts+0x20);
            V3 position=FN(0xec5a10,GetVec)(rb,0);
            V3 r=sub(point,position);
            float radius=FN(0x77fe10,float(*)(void*,void*))(ball,0);
            float r2=dot(r,r);
            if(radius>0.02f&&radius<0.5f&&r2>0.0001f){
                r=mul(r,radius/sqroot(r2));
                V3 hand=FN(0xeea0e0,V3(*)(void*,V3,void*))(part,point,0);
                V3 velocity=*(V3*)((char*)ball+0x8c);
                V3 omega=FN(0xec5870,GetVec)(rb,0);
                pending_spin=compute_spin(r,hand,velocity,omega,spin_transfer,spin_limit);
                pending_ball=ball;pending_valid=1;
            }
        }
    }
    collision_trampoline(body,part,ball,collision,method);
    reception_end();
    set_end();
    pending_valid=0;pending_ball=0;
}
EXPORT void random_hook(void* ball,void* method){
    if(pending_valid&&pending_ball==ball&&(offline()||network_physics())){
        setspin(ball,pending_spin);spinning_ball=ball;pending_time=0;return;
    }
    random_trampoline(ball,method);
    if(spinning_ball==ball)spinning_ball=0;
}
/* Local-player hits skip SetRandomAngularVelocity. This wrapper replaces only
 * the confirmed accepted-hit call site inside PhysicalBody.Handle... . */
/* Spin is packed atomically into the reliable hit RPC context. */
EXPORT int encode_spin(V3 spin,int context){
 spin=clampv(spin,60);float v[3]={spin.x,spin.y,spin.z};unsigned packed=0x50000000u|(context&7);
 for(int i=0;i<3;i++){float f=v[i]*(127.0f/60.0f);int q=(int)(f+(f>=0?.5f:-.5f));packed|=((unsigned)q&255u)<<(3+i*8);}return (int)packed;
}
EXPORT V3 decode_spin(int packed){
 V3 spin;float* v=&spin.x;for(int i=0;i<3;i++){int q=((unsigned)packed>>(3+i*8))&255;if(q>=128)q-=256;v[i]=q*(60.0f/127.0f);}return spin;
}
static void activate_spin(void* ball,V3 spin){setspin(ball,spin);spinning_ball=ball;pending_time=0;}
EXPORT void motion_hook(void* ball,V3 position,V3 velocity,_Bool hit,_Bool isThrow,int touchId,int team,int context,void* method){
 int has_spin=hit&&pending_valid&&pending_ball==ball;V3 spin=pending_spin;
 if(hit&&assisted_set(position,&velocity)){has_spin=1;spin=(V3){0,0,0};pending_spin=spin;}
 if(has_spin&&network_physics()){context=encode_spin(spin,context);spin=decode_spin(context);pending_spin=spin;}
 FN(0x77e5c0,void(*)(void*,V3,V3,_Bool,_Bool,int,int,int,void*))(ball,position,velocity,hit,isThrow,touchId,team,context,method);
 if(has_spin&&(offline()||network_physics()))activate_spin(ball,spin);
}
static void integrate_spin(void* rb,float dt){
 if(!rb||FN(0xec5940,GetBool)(rb,0))return;
 V3 omega=FN(0xec5870,GetVec)(rb,0);if(dot(omega,omega)<0.0625f)return;
 V3 velocity=FN(0xec5b90,GetVec)(rb,0);if(dot(velocity,velocity)<0.01f)return;
 V3 acceleration=compute_magnus(omega,velocity,magnus_coefficient,magnus_acceleration_limit);
 int n=(int)(dt/0.033334f)+1;if(n>8)n=8;float h=dt/n;
 for(int i=0;i<n;i++){V3 mid=add(velocity,mul(acceleration,h*.5f));velocity=add(velocity,mul(compute_magnus(omega,mid,magnus_coefficient,magnus_acceleration_limit),h));acceleration=compute_magnus(omega,velocity,magnus_coefficient,magnus_acceleration_limit);}
 FN(0xec60d0,SetVec)(rb,velocity,0);
}
EXPORT void late_hook(void* ball,void* method){
    late_trampoline(ball,method);
    frame_callbacks++;
    if(ball!=spinning_ball)return;
    if(*((unsigned char*)ball+0xd0)){spinning_ball=0;pending_time=0;return;}
    float dt=FN(0xb72960,float(*)(void*))(0);
    if(!(dt>0&&dt<=0.25f))return;
    pending_time+=dt;
    if(pending_time+0.000001f<physics_interval)return;
    dt=pending_time;pending_time=0;
    int online=network_physics();
    if(!offline()&&!online){spinning_ball=0;return;}
    void* rb=*(void**)((char*)ball+0x98);
    physics_steps++;integrate_spin(rb,dt);
    void* local=*(void**)((char*)ball+0x30);
    if(online&&local!=rb)integrate_spin(local,dt);
}
#include "mode_2v2.c"
