"""Production elbow helper + delivered two-bone IK in an isolated emulator.

Builds only tools/e27elbow. Never changes any working or installed DLL/assets.
"""
from test_elbow_solver_v27 import *
import os,subprocess
T=R/'tools/e27elbow';T.mkdir(exist_ok=True)
source=r'''
#define EXPORT __declspec(dllexport)
#define TRAMP(ret,name,args) EXPORT __attribute__((naked)) ret name##_trampoline args {__asm__(".rept 32; int3; .endr");}
#define PTR(p,o) (*(void**)((char*)(p)+(o)))
typedef struct {float x,y,z;} V3;
typedef struct {float x,y,z,w;} Q4;
static V3 add(V3 a,V3 b){return (V3){a.x+b.x,a.y+b.y,a.z+b.z};}
static V3 sub(V3 a,V3 b){return (V3){a.x-b.x,a.y-b.y,a.z-b.z};}
static V3 mul(V3 a,float f){return (V3){a.x*f,a.y*f,a.z*f};}
static float dot(V3 a,V3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static V3 cross(V3 a,V3 b){return (V3){a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
static int finitev(V3 v){return v.x==v.x&&v.y==v.y&&v.z==v.z&&v.x<1e20f&&v.x> -1e20f&&v.y<1e20f&&v.y> -1e20f&&v.z<1e20f&&v.z> -1e20f;}
#include "../../elbow_v27.c"
EXPORT V3* guard_probe(V3* result,V3* normal,V3* direction,Q4* chest){*result=elbow_outward_v27(*normal,*direction,*chest);return result;}
int DllMain(void*a,unsigned b,void*c){return 1;}
'''
(T/'e.c').write_text(source)
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(T/'g'),ZIG_LOCAL_CACHE_DIR=str(T/'l'))
subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(T/'e.c'),'-o',str(T/'e.dll'),'-Wl,--entry=DllMain'],check=True,env=env,capture_output=True)

def install(e):
 p=pefile.PE(str(T/'e.dll'));hb=e.b+0x2000000;u=e.u
 u.mem_map(hb,(p.OPTIONAL_HEADER.SizeOfImage+4095)//4096*4096);u.mem_write(hb,p.get_memory_mapped_image())
 for block in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]):
  for r in block.entries:
   if r.type==10:e.ptr(hb+r.rva,e.q(hb+r.rva)+hb-p.OPTIONAL_HEADER.ImageBase)
 ex={x.name.decode():hb+x.address for x in p.DIRECTORY_ENTRY_EXPORT.symbols}
 tr=ex['elbow_bend_v27_trampoline'];hook=ex['elbow_bend_v27_hook'];original=e.b+0xeeabe0;n=7
 u.mem_write(tr,bytes(u.mem_read(original,n))+b'\xe9'+struct.pack('<i',original+n-(tr+n+5)))
 u.mem_write(original,b'\xe9'+struct.pack('<i',hook-(original+5))+b'\x90'*(n-5))
 return ex

if __name__=='__main__':
 rows=[];checks=0;yaw_checks=0;guard_checks=0;unchanged_left=0;changed_left=0
 for base in [0x180000000,0x190000000]:
  a,b=Solver(base),Solver(base);ex=install(b)
  for left in [True,False]:
   for pose,target in [('standing',[.22,1.05,.16]),('raised',[.22,1.95,.16]),('crossbody',[-.18,1.4,.3]),('straight',[.16,1.46,.56])]:
    for angle in [-180,-135,-90,-45,0,45,90,135,180]:
     wrist=np.r_[np.array([0,1,0])*math.sin(angle*math.pi/360),math.cos(angle*math.pi/360)]
     target=np.array(target);target[0]=abs(target[0])*(1 if left==False else -1) if pose!='crossbody' else (.18 if left else -.18)
     old=a.update(left,target,wrist);new=b.update(left,target,wrist)
     assert old['wrist']==new['wrist'] and np.allclose(new['wrist'],target,atol=1e-6)
     assert np.isfinite(list(new.values())).all()
     for k in ['upper','lower']:
      expected=(np.array(new['shoulder' if k=='upper' else 'wrist'])+new['elbow'])/2
      assert np.allclose(new[k],expected,atol=2e-7)
     if not left:assert old==new
     if left:
      if old==new:unchanged_left+=1
      else:changed_left+=1
     shoulder=np.array(new['shoulder']);direction=target-shoulder;mid=(target+shoulder)/2
     pole=np.array([-1.,0,0])-direction*np.dot([-1.,0,0],direction)/np.dot(direction,direction)
     if left:assert np.dot(np.array(new['elbow'])-mid,pole)>-2e-7
     if np.linalg.norm(direction)<.5999:
      assert abs(np.linalg.norm(np.array(new['elbow'])-shoulder)-.3)<2e-6
      assert abs(np.linalg.norm(np.array(new['elbow'])-target)-.3)<2e-6
     if base==0x180000000 and angle in [-90,0] and left:rows.append(dict(side='anatomical_left_viewer_right',pose=pose,wrist_yaw=angle,before=old,after=new))
     checks+=1
  for chest_yaw in [-135,-90,45,90,180]:
   chest=np.r_[np.array([0,1,0])*math.sin(chest_yaw*math.pi/360),math.cos(chest_yaw*math.pi/360)]
   for left in [True,False]:
    for angle in [-90,0,90]:
     wrist=np.r_[np.array([0,1,0])*math.sin(angle*math.pi/360),math.cos(angle*math.pi/360)]
     target=np.array([-.22 if left else .22,1.05,.16]);old=b.update(left,target,wrist)
     new=b.update(left,qr(chest,target),qm(chest,wrist),chest)
     for k in old:assert np.allclose(new[k],qr(chest,old[k]),atol=3e-6),(chest_yaw,left,angle,k,new[k],qr(chest,old[k]))
     yaw_checks+=1
  for normal,direction,chest in [([0,0,1],[0,0,0],[0,0,0,1]),([0,0,0],[0,-1,0],[0,0,0,1]),([0,0,1],[1,0,0],[0,0,0,1]),([0,0,1],[0,-1,0],[0,0,0,0]),([0,0,1],[0,-1,0],[0,0,0,2]),([0,0,float('nan')],[0,-1,0],[0,0,0,1]),([0,0,1],[0,float('inf'),0],[0,0,0,1]),([0,0,1],[0,-1,0],[0,0,0,float('nan')])]:
   out,n,d,q=[b.h+0x4000+i*0x20 for i in range(4)];b.vec(n,normal);b.vec(d,direction);b.vec(q,chest)
   b.call(ex['guard_probe']-b.b,[out,n,d,q]);assert bytes(b.u.mem_read(out,12))==bytes(b.u.mem_read(n,12));guard_checks+=1
 report=dict(passed=True,cases=checks,torso_yaw_cases=yaw_checks,guard_cases=guard_checks,unchanged_left_cases=unchanged_left,corrected_left_cases=changed_left,ASLR_bases=2,checks=['delivered native GetBendNormal+GetDirectionToBendPoint+UpdateArm executed','production helper machine code','standing raised crossbody straight targets','nine wrist yaws','right arm byte-identical readbacks','already outward left bit-identical','exact tracked wrist positions','original .3m segment lengths','collider midpoints match solved segments','finite poses and outward left bend','torso-yaw covariance','zero parallel invalid quaternion and nonfinite guards'],samples=rows,scope='CPU emulation of production code with Unity math and transform API fixtures; not Quest or two-PC VR playtesting')
 (R/'analysis/elbow-v27-results.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
