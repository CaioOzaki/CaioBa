import ctypes,pathlib,json,sys,time,struct
R=pathlib.Path(__file__).resolve().parent
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
k.ReadProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
k.WriteProcessMemory.argtypes=k.ReadProcessMemory.argtypes;k.CloseHandle.argtypes=[ctypes.c_void_p]
record=json.loads((R/'analysis/runtime-module.json').read_text(encoding='utf-8-sig'));ex=json.loads((R/'analysis/native-patch-manifest.json').read_text())['exports']
h=k.OpenProcess(0x438,False,record['id'])
if not h:raise ctypes.WinError(ctypes.get_last_error())
def get(name):
 v=ctypes.c_int();n=ctypes.c_size_t()
 if not k.ReadProcessMemory(h,record['base']+ex[name],ctypes.byref(v),4,ctypes.byref(n)):raise ctypes.WinError(ctypes.get_last_error())
 return v.value
def put(n):
 v=ctypes.c_int(n);count=ctypes.c_size_t()
 if not k.WriteProcessMemory(h,record['base']+ex['probe_command'],ctypes.byref(v),4,ctypes.byref(count)):raise ctypes.WinError(ctypes.get_last_error())
try:
 mode=sys.argv[1] if len(sys.argv)>1 else 'read'
 if mode!='read':put(int(mode))
 out={name:get(name) for name in ['probe_command','probe_page_ready','probe_ticks','solo_stage','doubles_requested','doubles_enabled','doubles_spawned','doubles_team_counts']}
 v=ctypes.c_int();count=ctypes.c_size_t();k.ReadProcessMemory(h,record['base']+ex['doubles_team_counts']+4,ctypes.byref(v),4,ctypes.byref(count));out['opponent_count']=v.value
 print(json.dumps(out))
 (R/'analysis/probe-last-status.json').write_text(json.dumps(out,indent=2))
finally:k.CloseHandle(h)
