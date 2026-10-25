"""Execute the shared map hooks as x64 with controlled IL2CPP/Photon calls.

Compiles a separate harness, never writes GameAssembly.dll or working assets.
The tested C module is the exact map_v19.c included by the production helper.
"""
from pathlib import Path
import json
import os
import struct
import subprocess
import sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/python'))
import capstone
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
from fix_map_v19 import patch_map_calls_v19,MAP_CALLS_V19

HARNESS=r'''
typedef unsigned long long U64;
#define EXPORT __declspec(dllexport)
#define PTR(o,n) (*(void**)((char*)(o)+(n)))
#define INT(o,n) (*(int*)((char*)(o)+(n)))
#define BYTE(o,n) (*(unsigned char*)((char*)(o)+(n)))
static U64 original_base;
static U64 base(void){return original_base;}
#define FN(r,t) ((t)(base()+(r)))
static int preferred_map,online_format;
EXPORT int preference_calls;
static void ensure_preferences_v19(void){preference_calls++;}
static void* str(const char* s){return FN(0x14b790,void*(*)(const char*))(s);}
static void managed_field(void* obj,int offset,void* value){FN(0x14ac30,void(*)(void*,void**,void*))(obj,(void**)((char*)obj+offset),value);}
static int text_equals(void* s,const char* word){
 if(!s)return 0;int n=INT(s,0x10),i=0;
 for(;word[i];i++)if(i>=n||*(unsigned short*)((char*)s+0x14+i*2)!=(unsigned char)word[i])return 0;
 return i==n;
}
#include "../map_v19.c"
EXPORT void configure(U64 b,int preference,int format){original_base=b;preferred_map=preference;online_format=format;}
EXPORT int DllMain(void* m,unsigned why,void* reserved){return 1;}
'''


def compile_harness():
    # Keep temporary basenames short: Zig's Windows object-cache path is bounded.
    source=R/'tools/m19.c';source.write_text(HARNESS,encoding='utf-8')
    output=R/'tools/m19.dll'
    zig=R/'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'
    env=dict(os.environ);cache=str(R/'tools/zig-cache-v13')
    env.update(ZIG_GLOBAL_CACHE_DIR=cache,ZIG_LOCAL_CACHE_DIR=cache)
    subprocess.run([str(zig),'cc','-target','x86_64-windows-msvc','-shared','-O2',
                    '-ffreestanding','-fno-stack-protector','-nostdlib',str(source),'-o',str(output),
                    '-Wl,--entry=DllMain'],check=True,env=env,capture_output=True)
    return pefile.PE(str(output))


HEAP=0x40000000;STACK=0x50000000;STOP=0x60000000
class Engine:
    def __init__(self,b,q):
        self.b=b;self.code=b+0x2000000;self.u=Uc(UC_ARCH_X86,UC_MODE_64)
        self.u.mem_map(b,0x1950000);self.u.mem_map(self.code,(q.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
        image=bytearray(q.get_memory_mapped_image())
        delta=self.code-q.OPTIONAL_HEADER.ImageBase
        for block in getattr(q,'DIRECTORY_ENTRY_BASERELOC',[]):
            for e in block.entries:
                if e.type==10:struct.pack_into('<Q',image,e.rva,struct.unpack_from('<Q',image,e.rva)[0]+delta)
                elif e.type:raise AssertionError(e.type)
        self.u.mem_write(self.code,bytes(image));self.u.mem_map(HEAP,0x400000)
        self.u.mem_map(STACK,0x10000);self.u.mem_map(STOP,0x1000)
        self.ex={e.name.decode():self.code+e.address for e in q.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
        self.next=HEAP+0x1000;self.tables={};self.current_room=0
        self.domain=self.alloc();self.assembly=self.alloc();self.image=self.alloc();self.klass=self.alloc();self.string_klass=self.alloc()
        self.class_available=True;self.allocation_ok=True;self.create_result=True
        self.creates=[];self.loads=[];self.constructed=[];self.assignments=[]
        self.u.hook_add(UC_HOOK_CODE,self.hook)
    def alloc(self,size=0x100):
        out=self.next;self.next+=(size+15)&~15;return out
    def put(self,address,value):self.u.mem_write(address,struct.pack('<Q',value))
    def get(self,address):return struct.unpack('<Q',self.u.mem_read(address,8))[0]
    def string(self,text):
        data=text.encode('utf-16le');p=self.alloc(len(data)+32)
        self.put(p,self.string_klass);self.u.mem_write(p+0x10,struct.pack('<I',len(text)))
        self.u.mem_write(p+0x14,data+b'\0\0');return p
    def text(self,address):
        n=struct.unpack('<I',self.u.mem_read(address+0x10,4))[0]
        return self.u.mem_read(address+0x14,n*2).decode('utf-16le')
    def ctext(self,address):
        out=bytearray()
        while True:
            c=self.u.mem_read(address+len(out),1)
            if c==b'\0':break
            out.extend(c)
        return out.decode('utf-8')
    def ret(self,value=0):
        sp=self.u.reg_read(UC_X86_REG_RSP)
        self.u.reg_write(UC_X86_REG_RAX,int(value));self.u.reg_write(UC_X86_REG_RIP,self.get(sp));self.u.reg_write(UC_X86_REG_RSP,sp+8)
    def call(self,name,*args):
        sp=STACK+0xff08;self.put(sp,STOP)
        for reg,arg in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),args):self.u.reg_write(reg,arg)
        for i,arg in enumerate(args[4:]):self.put(sp+0x28+i*8,arg)
        self.u.reg_write(UC_X86_REG_RSP,sp);self.u.emu_start(self.ex[name],STOP,count=200000)
        assert self.u.reg_read(UC_X86_REG_RIP)==STOP,name
        return self.u.reg_read(UC_X86_REG_RAX)
    def hook(self,u,addr,size,data):
        if addr>=self.code or addr==STOP:return
        r=addr-self.b;a,b,c,d=[u.reg_read(x) for x in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
        if r==0x14b790:self.ret(self.string(self.ctext(a)))
        elif r==0x14a920:self.ret(self.domain)
        elif r==0x14a910:
            assert a==self.domain and self.ctext(b)=='Photon3Unity3D';self.ret(self.assembly if self.class_available else 0)
        elif r==0x14a530:assert a==self.assembly;self.ret(self.image)
        elif r==0x14a5a0:
            assert a==self.image and self.ctext(b)=='ExitGames.Client.Photon' and self.ctext(c)=='Hashtable';self.ret(self.klass)
        elif r==0x14af40:
            assert a==self.klass
            if self.allocation_ok:
                table=self.alloc();self.tables[table]={};self.ret(table)
            else:self.ret(0)
        elif r==0x7b3430:assert a in self.tables;self.constructed.append(a);self.ret()
        elif r==0x14ac30:
            self.put(b,c);self.assignments.append((a,b,c));self.ret()
        elif r==0x7b3520:self.tables[a][self.text(b)]=c;self.ret()
        elif r==0x7b34c0:self.ret(self.tables[a].get(self.text(b),0))
        elif r==0x61ed80:self.ret(self.current_room)
        elif r==0x60b4c0:
            method=self.get(u.reg_read(UC_X86_REG_RSP)+0x28);self.creates.append((a,b,c,d,method));self.ret(self.create_result)
        elif r==0x251940:self.loads.append((a,self.text(b),c,d));self.ret(0x12345678)
        else:raise AssertionError(('Unexpected external native call',hex(r)))
    def room(self,value):
        table=self.alloc();self.tables[table]={'Other.Key':self.string('keep')}
        if value is not None:self.tables[table]['Cloudcourt.Map']=self.string(value) if isinstance(value,str) else value
        room=self.alloc();self.put(room+0x18,table);self.current_room=room
        return room,table


def run():
    q=compile_harness();cases=[]
    for base in (0x180000000,0x190000000):
        e=Engine(base,q)
        for fmt in (2,4):
            for preference in (0,1):
                e.call('configure',base,preference,fmt)
                options=e.alloc();name=e.string('code');lobby=e.alloc();users=e.alloc();method=e.alloc()
                assert e.call('create_room_map_hook',name,options,lobby,users,method)==1
                assert e.u.mem_read(options+0x12,1)==bytes([4 if fmt==2 else 8])
                props=e.get(options+0x20);assert e.text(e.tables[props]['Cloudcourt.Map'])==('Scene' if preference else 'IndoorArenaScene')
                assert e.creates[-1]==(name,options,lobby,users,method)
                assert e.constructed[-1]==props and e.assignments[-1]==(options,options+0x20,props)
                # Every client, including one with the opposite preference, uses the host property.
                room=e.alloc();e.put(room+0x18,props);e.current_room=room
                for local in (0,1):
                    e.call('configure',base,local,fmt)
                    system=e.alloc();original=e.string('IndoorArenaScene');finished=e.alloc();m=e.alloc()
                    assert e.call('online_environment_map_hook',system,original,finished,m)==0x12345678
                    assert e.loads[-1]==(system,'Scene' if preference else 'IndoorArenaScene',finished,m)
                cases.append(dict(base=hex(base),format=fmt,host_map=preference,clients=2))
        # Existing property maps retain unrelated keys, and failures forward unchanged.
        _,props=e.room('NightScene');options=e.alloc();e.put(options+0x20,props)
        e.call('configure',base,1,4);count=len(e.constructed)
        e.create_result=False
        assert e.call('create_room_map_hook',0,options,0,0,0)==0
        assert len(e.constructed)==count and e.text(e.tables[props]['Other.Key'])=='keep'
        assert e.text(e.tables[props]['Cloudcourt.Map'])=='Scene'
        assert e.call('create_room_map_hook',0,0,0,0,0)==0
        for fail in ('class_available','allocation_ok'):
            setattr(e,fail,False);options=e.alloc()
            assert e.call('create_room_map_hook',0,options,0,0,0)==0 and e.get(options+0x20)==0
            setattr(e,fail,True)
        # Legacy night/day labels canonicalize exactly; unknown or non-string data is safe.
        bad=e.alloc();e.put(bad,e.klass);e.u.mem_write(bad+0x10,b'\xff'*4)
        for value,expected in [('NightScene',1),('Scene',1),('Beach',1),('DayScene',1),
                               ('IndoorArenaScene',0),('Indoor',0),('BadNightScene',0),('',0),(None,0),(bad,0)]:
            e.room(value);assert e.call('online_room_map_v19')==expected,(value,expected)
        e.current_room=0;assert e.call('online_room_map_v19')==0
        assert struct.unpack('<I',e.u.mem_read(e.ex['preference_calls'],4))[0]>0
    # Prove exact code route patching against the preserved base build.
    original=R/'backup/GameAssembly.dll';p=pefile.PE(str(original));result=bytearray(original.read_bytes())
    exports={x.name.decode():x.address for x in q.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
    patches=[];patch_map_calls_v19(result,p,patches,exports,0x194f000)
    for _,site,_,export in MAP_CALLS_V19:
        raw=result[p.get_offset_from_rva(site):p.get_offset_from_rva(site)+5]
        assert raw[0]==0xe8 and site+5+struct.unpack('<i',raw[1:])[0]==exports[export]+0x194f000
    assert [x['rva'] for x in patches]==[0x319857,0x32a445]
    report={'passed':True,'host_client_cases':cases,
            'checks':['host map stored in room properties','new/existing Hashtable paths',
                      'room caps 4/8','client preference never overrides host',
                      'NightScene becomes day Scene','malformed property types rejected',
                      'missing map defaults to indoor','original arguments/callback/return preserved',
                      'managed write barrier for new room properties','two exact call-site routes','two ASLR bases'],
            'integration':{'include':'map_v19.c after ensure_preferences_v19 and preferred_map',
                           'helper':'patch_map_calls_v19(result,p,patches,exports,delta)',
                           'call_sites':[hex(x['rva']) for x in patches]},
            'scope':'Compiled x64 with controlled IL2CPP/Photon calls; live two-PC loading remains a playtest.'}
    (R/'analysis/v19-map-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':run()
