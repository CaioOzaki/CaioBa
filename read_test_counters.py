import sys,pathlib,json,ctypes,struct,time
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import pefile
record=json.loads((R/'analysis/runtime-module.json').read_text())
p=pefile.PE(str(R/'tools/spin-native.dll'))
exports={e.name.decode():e.address+0x194f000 for e in p.DIRECTORY_ENTRY_EXPORT.symbols}
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
k.ReadProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
k.CloseHandle.argtypes=[ctypes.c_void_p]
handle=k.OpenProcess(0x410,False,record['id'])
if not handle:raise ctypes.WinError(ctypes.get_last_error())
def read():
    out={}
    for name in ['frame_callbacks','physics_steps']:
        value=ctypes.c_ulonglong();count=ctypes.c_size_t()
        if not k.ReadProcessMemory(handle,record['base']+exports[name],ctypes.byref(value),8,ctypes.byref(count)):raise ctypes.WinError(ctypes.get_last_error())
        out[name]=value.value
    return out
try:
    a=read();start=time.perf_counter();time.sleep(2);b=read();elapsed=time.perf_counter()-start
    result={'first':a,'last':b,'seconds':elapsed,'callback_rate':(b['frame_callbacks']-a['frame_callbacks'])/elapsed,'scope':'Headless initialization; no GPU rendering or hand contacts. Callback rate is NOT headset FPS.'}
    (R/'analysis/runtime-v2-counters.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:k.CloseHandle(handle)
