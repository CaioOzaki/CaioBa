"""Compile the exact skin cache function against delayed/replaced materials.

This exercises both the shipped v19 source and the parent's corrected v20 source,
without executing or modifying the installed game or rebuilding the main DLL.
"""
from pathlib import Path
import ctypes, hashlib, json, os, subprocess
R=Path(__file__).resolve().parent
F=R/'tools/u20skin';F.mkdir(parents=True,exist_ok=True)
TEMPLATE=r"""
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
typedef struct{float x,y;}V2;typedef struct{float x,y,z,w;}Q4;
static char body[512],player[64],renderer[2],material[4];
static void* handles[128];static unsigned next_handle;
static int material_alive[4],available[2],active_mat[2],desired_skin;
EXPORT int observed[24];
static void* rooted(unsigned h){return h?handles[h]:0;}
static void root_set(unsigned* h,void* p){if(!p){*h=0;return;}if(!*h)*h=++next_handle;handles[*h]=p;}
static int alive(void* p){if(p==body)return 1;for(int i=0;i<4;i++)if(p==&material[i])return material_alive[i];return 0;}
static void* transform(void*p){return p;}
static void* str(const char*p){return (void*)p;}
static void* find_child(void*p,const char*path){(void)p;int i=path[9]=='H'?0:1;return available[i]?&renderer[i]:0;}
static void* gameobject(void*p){return p;}
static int player_skin(void*p){(void)p;return desired_skin;}
static void* component(void*p,void*n,void*m){(void)n;(void)m;return p;}
static void* getmat(void*p,void*m){(void)m;int i=p==&renderer[0]?0:1;return available[i]?&material[active_mat[i]]:0;}
static void offset(void*p,V2 uv,void*m){(void)m;observed[0]++;int i=(int)((char*)p-material);observed[4+i]=(int)(uv.x*300.01f);observed[8+i]=(int)(uv.y*300.01f);}
static void color(void*p,Q4 c,void*m){(void)p;(void)m;observed[1]++;if(c.x!=1||c.y!=1||c.z!=1||c.w!=1)observed[2]++;}
static void* mock(unsigned r){if(r==0x94f410)return component;if(r==0xa1ae90)return getmat;if(r==0x9566d0)return offset;if(r==0x956610)return color;return 0;}
#define FN(r,t) ((t)mock(r))
FUNCTION
static void reset(void){
 for(int i=0;i<24;i++)observed[i]=0;
 for(int i=0;i<128;i++)handles[i]=0;next_handle=0;
 for(int i=0;i<8;i++){skins[i].body=skins[i].materials[0]=skins[i].materials[1]=0;skins[i].skin=-1;}
 for(int i=0;i<4;i++)material_alive[i]=1;
 available[0]=available[1]=0;active_mat[0]=0;active_mat[1]=1;desired_skin=18;PTR(body,0x168)=player;
}
EXPORT int run_test(int which){
 reset();int result=0;
 if(which==0){
  skin_body(body);observed[12]=observed[0];
  available[0]=available[1]=1;skin_body(body);observed[13]=observed[0];
  if(observed[12]==0&&observed[13]==2)result|=1;
  desired_skin=4+9*7;skin_body(body);observed[14]=observed[0];
  if(observed[14]==4&&observed[4]==100&&observed[8]==100&&observed[5]==100&&observed[9]==0)result|=2;
  skin_body(body);observed[15]=observed[0];if(observed[15]==4)result|=4;
  material_alive[0]=0;active_mat[0]=2;skin_body(body);observed[16]=observed[0];
  if(observed[16]==6&&observed[6]==100&&observed[10]==100)result|=8;
 }else{
  available[0]=1;skin_body(body);observed[12]=observed[0];
  available[1]=1;skin_body(body);observed[13]=observed[0];
  if(observed[12]==1&&observed[13]==3)result|=1;
  skin_body(body);observed[14]=observed[0];if(observed[14]==3)result|=2;
 }
 if(observed[0]==observed[1]&&!observed[2])result|=16;
 return result;
}
EXPORT int DllMain(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 1;}
"""
def extract(path):
 text=path.read_text();return text[text.index('typedef struct {unsigned body,materials[2];int skin;} AvatarSkin;'):text.index('typedef struct {unsigned root;Q4 saved,open;} Finger;')]
def main():
 report={}
 for label,source in [('v19',R/'versions/cloudcourt-v19-antes-v20/fontes/comfort_v14.c'),('v20',R/'comfort_v14.c')]:
  c=F/(label+'.c');dll=F/(label+'.dll');c.write_text(TEMPLATE.replace('FUNCTION',extract(source)))
  env=dict(os.environ);env.update(ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache-skin20'),ZIG_LOCAL_CACHE_DIR=str(R/'tools/zig-cache-skin20'))
  subprocess.run([str(R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'),'cc','-target','x86_64-windows-msvc','-shared','-O2','-ffreestanding','-fno-stack-protector','-nostdlib',str(c),'-o',str(dll),'-Wl,--entry=DllMain'],env=env,check=True,capture_output=True)
  native=ctypes.CDLL(str(dll));native.run_test.argtypes=[ctypes.c_int];native.run_test.restype=ctypes.c_int
  cases=[]
  for which in (0,1):
   value=native.run_test(which);state=list((ctypes.c_int*24).in_dll(native,'observed'));cases.append(dict(mask=value,observed=state))
  report[label]=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),cases=cases)
 assert report['v19']['cases'][0]['mask']!=31 and report['v19']['cases'][1]['mask']!=19,'Old cache did not reproduce the defect.'
 assert report['v20']['cases'][0]['mask']==31,report['v20']
 assert report['v20']['cases'][1]['mask']==19,report['v20']
 report.update(passed=True,old_failure_proven=True,delayed_materials_retry=True,partial_materials_retry=True,replaced_materials_reapply=True,stable_materials_cached=True,independent_face_outfit_uvs=True,actual_source_compiled=True,scope='Native Windows x64 execution of exact skin_body source with delayed/destroyed renderer/material mocks; not a VR or multiplayer session.')
 (R/'analysis/v20-skin-cache-regression.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('v19','v20')},indent=2))
if __name__=='__main__':main()
