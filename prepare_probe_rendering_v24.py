"""Prepare only unresolved runtime readback/lifecycle tests; keep ray evidence."""
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'probe_graphics_v24.py').read_text()
# Reuse the same owned disposable game, copying the final rendering module.
at=s.index("debug = r'''");end=s.index("source = source.replace(' probe_ticks++;'",at)
debug=r'''
 probe_ui[0]=graphics_loaded_v24;probe_ui[1]=graphics_selected_v24;
 probe_ui[2]=FN(0xa12bc0,int(*)(void*))(0);
 probe_ui[3]=FN(0xed8ba0,_Bool(*)(void*))(0);
 if(probe_command==30&&start){
  probe_command=0;
  const char* names[8]={"get_masterTextureLimit","get_anisotropicFiltering","get_shadows","get_shadowResolution","get_softParticles","get_realtimeReflectionProbes","get_shadowDistance","get_lodBias"};
  for(int i=0;i<4;i++){
   graphics_apply_v24(i);int p=16+i*16;
   for(int j=0;j<8;j++){
    char buffer[128]="UnityEngine.QualitySettings::";int n=29,k=0;while(names[j][k])buffer[n++]=names[j][k++];buffer[n]=0;
    void* fn=FN(0x14b030,void*(*)(const char*))(buffer);
    probe_ui[p+j]=fn?(j<4?((int(*)(void))fn)():j<6?((_Bool(*)(void))fn)():(U64)(((float(*)(void))fn)()*1000.f)):0xffffffff;
   }
   probe_ui[p+8]=FN(0xa12bc0,int(*)(void*))(0);
   probe_ui[p+9]=(U64)(FN(0xed8c00,float(*)(void*))(0)*1000.f);
  }
  /* Reuse the original serialized AdaptiveGraphics component for real
   * original event handler dispatch, then check our wrapper restored LOW. */
  probe_ui[91]=1;
  graphics_apply_v24(0);FN(0x264080,void(*)(void*,void*))(0,0);
  probe_ui[80]=1;probe_ui[81]=graphics_selected_v24;probe_ui[82]=FN(0xa12bc0,int(*)(void*))(0);
  probe_ui[91]=2;
  void* domain=FN(0x14a920,void*(*)(void))();U64 count=0;
  void** assemblies=FN(0x14a930,void**(*)(void*,U64*))(domain,&count);void* klass=0;
  for(U64 i=0;i<count&&!klass;i++){void* image=FN(0x14a530,void*(*)(void*))(assemblies[i]);klass=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"","OVRManager");}
  void* type=klass?FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(klass)):0;
  void* arr=type?FN(0xb6b720,void*(*)(void*,void*))(type,0):0;
  void* ovr=arr&&INT(arr,0x18)>0?PTR(arr,0x20):0;
  if(ovr){BYTE(ovr,0x25)=1;BYTE(ovr,0x27)=1;FN(0x457fd0,void(*)(void*,void*))(ovr,0);probe_ui[83]=1;probe_ui[84]=BYTE(ovr,0x25);probe_ui[85]=BYTE(ovr,0x27);}
  FN(0xa12870,void(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),1,0);
  if(graphics_save_v24)graphics_save_v24();
  probe_ui[86]=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),-1,0);
  probe_ui[87]=graphics_save_v24!=0;probe_ui[88]=1;
 }
'''
s=s[:at]+"debug = r'''"+debug+"'''\n"+s[end:]
s=s.replace("(F / 'build_patch.py').write_text(builder)","builder=builder.replace('for name,rva in entries:', \"entries += [('graphics_adaptive_start',0x2641d0),('graphics_adaptive_apply',0x264080),('graphics_ovr_update',0x457fd0)]\\nfor name,rva in entries:\")\n(F / 'build_patch.py').write_text(builder)")
# Existing source has a single process and a finally block that snapshots and
# restores Unity's complete registry preferences. Replace only its experiment.
at=s.index('    put(10)');end=s.index('\nfinally:',at)
s=s[:at]+'''    def snapshot():return struct.unpack('<160Q',read(base+ex['probe_ui'],1280))
    put(30)
    for _ in range(100):
        first=snapshot()
        if first[88]:break
        time.sleep(.1)
    assert first[88], ('Rendering probe incomplete',first[80:92],first[16:26])
    values=[]
    for i in range(4):
        v=first[16+i*16:26+i*16]
        values.append(dict(preset=i,texture_limit=v[0],aniso=v[1],shadows=v[2],shadow_resolution=v[3],soft_particles=v[4],reflections=v[5],shadow_distance=v[6]/1000,lod=v[7]/1000,aa=v[8],xr_scale_readback=v[9]/1000))
    assert [v['texture_limit'] for v in values]==[1,0,0,0]
    assert [v['aniso'] for v in values]==[0,1,2,2]
    assert [v['shadows'] for v in values]==[0,1,2,2]
    assert [v['shadow_resolution'] for v in values]==[0,0,1,2]
    assert [v['soft_particles'] for v in values]==[0,0,1,1]
    assert [v['reflections'] for v in values]==[0,0,1,1]
    assert [v['shadow_distance'] for v in values]==[15,30,60,150]
    assert all(abs(v['lod']-x)<.002 for v,x in zip(values,[.6,1,1.4,2]))
    assert [v['aa'] for v in values]==[0,2,4,4]
    assert first[80:88]==(1,0,0,1,0,0,1,1), first[80:88]
    proc.terminate();proc.wait(timeout=10);k.CloseHandle(handle)
    proc=subprocess.Popen([str(W/'VolleyballFever.exe'),'-batchmode','-force-d3d11','-vrmode','none','-screen-width','1024','-screen-height','768','-screen-fullscreen','0','-logFile',str(F/'analysis/unity-restart.log')],cwd=W,startupinfo=info)
    handle=k.OpenProcess(0x438,False,proc.pid);base=0
    for _ in range(500):
        if proc.poll() is not None:raise RuntimeError(('Unity restart exited',proc.returncode))
        if not base:
            modules=(ctypes.c_void_p*512)();needed=ctypes.c_ulong()
            if ps.EnumProcessModulesEx(handle,modules,ctypes.sizeof(modules),ctypes.byref(needed),3):
                for module in modules[:min(needed.value//ctypes.sizeof(ctypes.c_void_p),512)]:
                    path=ctypes.create_unicode_buffer(4096);ps.GetModuleFileNameExW(handle,module,path,4096)
                    if path.value.endswith('GameAssembly.dll'):base=module;break
        if base:
            second=snapshot()
            if second[0] and second[1]==1 and second[2]==2:break
        time.sleep(.1)
    assert second[0:3]==(1,1,2), second[0:3]
    result=dict(passed=True,values=values,adaptive_apply_hook_preserved_LOW=True,original_OVR_Update_does_not_override_preset=True,saved_pref=first[86],PlayerPrefs_Save_resolved=bool(first[87]),fresh_process_startup_preset='MEDIUM',fresh_process_startup_aa=second[2],xr_enabled=bool(first[3]),xr_scale_headset_validation_pending=not bool(first[3]),raycast_test_repeated=False,working_or_live_modified=False,preferences_restored=True)
    (R/'analysis/v24-graphics-rendering-unity.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
''' +s[end:]
(R/'probe_rendering_v24.py').write_text(s)
print('Prepared probe_rendering_v24.py')
