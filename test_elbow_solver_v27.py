"""Execute delivered PhysicalBody IK machine code with Unity math/transform stubs."""
from pathlib import Path
import sys,struct,math,json
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R),str(R/'tools/python')]
import numpy as np,pefile,capstone
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
def unit(v):
 v=np.array(v,dtype=float);n=np.linalg.norm(v);return v/n if n>1e-8 else v*0
def qm(a,b):
 a,b=np.array(a),np.array(b);return np.r_[a[3]*b[:3]+b[3]*a[:3]+np.cross(a[:3],b[:3]),a[3]*b[3]-np.dot(a[:3],b[:3])]
def qr(q,v):
 q=np.array(q);v=np.array(v);return v+2*np.cross(q[:3],np.cross(q[:3],v)+q[3]*v)
def ft(a,b):
 a,b=unit(a),unit(b);q=np.r_[np.cross(a,b),1+np.dot(a,b)]
 if np.linalg.norm(q)<1e-7:q=np.r_[unit(np.cross(a,[1,0,0] if abs(a[0])<.8 else [0,1,0])),0]
 return q/np.linalg.norm(q)
def look(f,u):
 f=unit(f);r=unit(np.cross(u,f));u=np.cross(f,r)
 # Compose shortest forward aim then the roll that aligns its up vector.
 q=ft([0,0,1],f);return qm(ft(qr(q,[0,1,0]),u),q)

class Solver:
 def __init__(self,base=0x180000000,image=None,manifest=None):
  self.b=base;self.p=pefile.PE(str(image or R/'versions/cloudcourt-v26-antes-v27/GameAssembly.dll'))
  self.u=Uc(UC_ARCH_X86,UC_MODE_64);self.u.mem_map(base,(self.p.OPTIONAL_HEADER.SizeOfImage+4095)//4096*4096);self.u.mem_write(base,self.p.get_memory_mapped_image())
  for block in self.p.DIRECTORY_ENTRY_BASERELOC:
   for e in block.entries:
    if e.type==10:self.ptr(base+e.rva,self.q(base+e.rva)+base-self.p.OPTIONAL_HEADER.ImageBase)
  self.h=0x300000000;self.s=0x400000000;self.stop=self.h+0xff000;self.u.mem_map(self.h,0x100000);self.u.mem_map(self.s,0x100000)
  md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64);md.detail=True
  for start,length in [(0xeeabe0,0x7d0),(0xeeea90,0x5e0)]:
   for ins in md.disasm(self.p.get_data(start,length),base+start):
    if ins.mnemonic=='mov' and ins.op_str.startswith('rcx, qword ptr [rip'):
     self.ptr(ins.address+ins.size+ins.operands[1].mem.disp,self.h+0x3000)
  self.body=self.h+0x100;self.arm=self.h+0x500;self.target=self.h+0x700;self.pos={};self.rot={};self.extra=None
  self.ptr(self.body+0x40,self.arm);self.ptr(self.arm+0x10,self.target)
  for i,o in enumerate([0x18,0x20,0x28,0x40,0x48,0x50]):self.ptr(self.arm+o,self.h+0x800+0x100*i)
  self.u.mem_write(self.arm+0x3c,struct.pack('<f',.6));self.u.hook_add(UC_HOOK_CODE,self.hook)
 def ptr(self,a,v):self.u.mem_write(a,struct.pack('<Q',v))
 def q(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
 def vec(self,a,v):self.u.mem_write(a,struct.pack('<'+'f'*len(v),*v))
 def rv(self,a,n=3):return np.array(struct.unpack('<'+'f'*n,self.u.mem_read(a,n*4)))
 def xf(self,i):return struct.unpack('<f',struct.pack('<I',self.u.reg_read(UC_X86_REG_XMM0+i)&0xffffffff))[0]
 def ret(self,v=None,f=None,double=False):
  if v is not None:self.u.reg_write(UC_X86_REG_RAX,int(v))
  if f is not None:self.u.reg_write(UC_X86_REG_XMM0,struct.unpack('<Q' if double else '<I',struct.pack('<d' if double else '<f',f))[0])
  sp=self.u.reg_read(UC_X86_REG_RSP);self.u.reg_write(UC_X86_REG_RIP,self.q(sp));self.u.reg_write(UC_X86_REG_RSP,sp+8)
 def hook(self,u,addr,size,user):
  r=addr-self.b;a,b,c,d=[u.reg_read(x) for x in [UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9]]
  if self.extra and self.extra(self,r,a,b,c,d):return
  if r in (0x1c21b0,0x14b040,0xeea350):self.ret();return
  if r==0x1c2320:raise AssertionError('native null reference')
  if r==0xb74fd0:self.vec(a,self.rot.get(b,[0,0,0,1]));self.ret(a);return
  if r==0xb756b0:self.pos[a]=self.rv(b);self.ret();return
  if r==0xb75750:self.rot[a]=self.rv(b,4);self.ret();return
  if r==0x94b620:self.ret(a);return
  const={0xb79d30:[0,1,0],0xb798c0:[0,-1,0],0xb79940:[0,0,1],0xb79840:[0,0,-1],0xb79db0:[0,0,0]}
  val=None
  if r in const:val=const[r]
  elif r==0xb79770:val=[self.xf(1),self.xf(2),self.xf(3)]
  elif r==0xa12d10:
   half=self.xf(1)*math.pi/360;val=np.r_[unit(self.rv(c))*math.sin(half),math.cos(half)]
  elif r==0xa14bb0:val=qm(self.rv(b,4),self.rv(c,4))
  elif r==0xa149c0:val=qr(self.rv(b,4),self.rv(c))
  elif r==0xa13810:val=self.rv(b,4)*[-1,-1,-1,1]
  elif r==0xa13330:val=ft(self.rv(b),self.rv(c))
  elif r==0xa13b80:val=look(self.rv(b),self.rv(c))
  elif r==0xb79ae0:val=unit(self.rv(b))
  elif r==0xb79a40:self.ret(f=np.linalg.norm(self.rv(a)));return
  elif r==0xb79e30:val=self.rv(b)+self.rv(c)
  elif r==0xb7a090:val=self.rv(b)-self.rv(c)
  elif r==0xb7a000:val=self.rv(b)*self.xf(2)
  elif r==0xb77e50:val=np.cross(self.rv(b),self.rv(c))
  elif r==0xb78180:val=self.rv(b)+(self.rv(c)-self.rv(b))*min(1,max(0,self.xf(3)))
  elif r==0x716d10:val=unit(self.rv(c)-self.rv(b))
  elif r==0xb79ed0:self.ret(np.linalg.norm(self.rv(a)-self.rv(b))<1e-5);return
  elif r==0x956d70:self.ret(f=min(self.xf(2),max(self.xf(1),self.xf(0))));return
  elif r==0x1cd9a0:
   x=struct.unpack('<d',struct.pack('<Q',u.reg_read(UC_X86_REG_XMM0)&0xffffffffffffffff))[0];self.ret(f=math.sqrt(x),double=True);return
  if val is not None:self.vec(a,val);self.ret(a)
 def call(self,r,args):
  sp=self.s+0x80008;self.u.reg_write(UC_X86_REG_RSP,sp);self.ptr(sp,self.stop)
  for reg,v in zip([UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9],args):self.u.reg_write(reg,v)
  for i,v in enumerate(list(args)[4:]+[0]*8):self.ptr(sp+0x28+8*i,v)
  try:self.u.emu_start(self.b+r,self.stop,count=100000)
  except Exception:
   print('RIP',hex(self.u.reg_read(UC_X86_REG_RIP)-self.b));raise
  assert self.u.reg_read(UC_X86_REG_RIP)==self.stop
 def update(self,left,hand,wrist=(0,0,0,1),chest=(0,0,0,1)):
  self.vec(self.arm+0x30,[-.16 if left else .16,-.14,-.04]);self.ptr(self.body+0x40,self.arm if left else self.h+0x780)
  hp,hq,np_,cq=self.h+0x2000,self.h+0x2020,self.h+0x2040,self.h+0x2060
  self.vec(hp,hand);self.vec(hq,wrist);self.vec(np_,[0,1.6,0]);self.vec(cq,chest);self.rot[self.target]=wrist
  self.call(0xeeea90,[self.body,self.arm,hp,hq,np_,cq,cq,0])
  return dict(shoulder=self.pos[self.q(self.arm+0x40)].tolist(),elbow=self.pos[self.q(self.arm+0x48)].tolist(),wrist=self.pos[self.q(self.arm+0x28)].tolist(),upper=self.pos[self.q(self.arm+0x18)].tolist(),lower=self.pos[self.q(self.arm+0x20)].tolist())

if __name__=='__main__':
 e=Solver();results=[]
 for left in (True,False):
  for name,hand in [('standing',[.28,1.05,.25]),('raised',[.28,1.95,.25]),('crossbody',[-.18,1.4,.3])]:
   hand[0]*=-1 if left else 1
   d=e.update(left,hand);results.append(dict(side='L' if left else 'R',pose=name,**d))
 print(json.dumps(results,indent=2));(R/'analysis/elbow-native-v26-readback.json').write_text(json.dumps(results,indent=2))
