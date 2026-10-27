"""Derive the existing isolated CurvedUI probe, replacing only its experiment."""
from pathlib import Path
R=Path(__file__).resolve().parent
base=(R/'probe_ui_v22.py').read_text()
base=base.replace("tools/u22-ui","tools/u24-graphics").replace("versions/cloudcourt-v21-antes-v22","versions/cloudcourt-v23-antes-v24")
base=base.replace("for name in ('customization_v19.c','avatar_style_v21.c','score_outline_v20.c'):","for name in ('graphics_v24.c',):")
base=base.replace("source = (F / 'mode_2v2.c').read_text()",'''source = (F / 'mode_2v2.c').read_text()
source=source.replace('static int customization_button_v19(void* button);','static int customization_button_v19(void* button);\\nstatic int graphics_button_v24(void* button);\\nstatic void graphics_start_v24(void);\\nstatic void graphics_close_v24(void);')
source=source.replace('#include "customization_v19.c"','#include "customization_v19.c"\\n#include "graphics_v24.c"')
identity=(F/'identity_v16.c').read_text().replace('if(customization_button_v19(button))return;','if(graphics_button_v24(button))return;\\n if(customization_button_v19(button))return;')
(F/'identity_v16.c').write_text(identity)
''')
start=base.index("debug = r'''");end=base.index("source = source.replace(' probe_ticks++;'",start)
original=(R/'probe_ui_v22.py').read_text()
camera=original[original.index('  void* domain=FN',original.index('debug = r')):original.index('\n }\n if(probe_command==11',original.index('debug = r'))]
shot=original[original.index(' if(probe_command==11'):original.index("'''\ndebug = debug.replace")]
debug=r'''
EXPORT int probe_graphics_ready;
'''
debug=r'''
 if(probe_command==10&&start){
  probe_command=0;
  void* menu=menu_transform_v19();
  const char* hide[9]={"Pages/Start/Daily Challenge","Pages/Start/Splash","Pages/Start/Online Button","Pages/Start/Settings Button","Pages/Start/Solo Button","Pages/Start/Quit Button","Pages/Start/Cloudcourt CLOUDCOURT VR","Pages/Start/Cloudcourt Big rallies. Good company.","Pages/Start/CC_CustomizeOpen"};
  for(int i=0;i<9;i++){void* t=find_child(menu,hide[i]);if(t)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(t),0,0);}
  void* page=0;
  page=find_child(menu,"Pages/Settings");if(page)FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(page),1,0);
  graphics_start_v24();
CAMERA
 }
SHOT
 if(probe_command>=12&&probe_command<=17&&start){
  int command=probe_command;probe_command=0;
  void* menu=menu_transform_v19();void* panel=graphics_panel_v24();
  const char* paths[6]={"Pages/Settings/CC_GraphicsOpen","CC_GraphicsLow","CC_GraphicsMedium","CC_GraphicsHigh","CC_GraphicsUltra","CC_GraphicsBack"};
  int slot=16+(command-12)*12;
  void* t=find_child(command==12?menu:panel,paths[command-12]);V3 center=position(t);
  typedef struct{V3 o,d;} TestRay;TestRay ray={{center.x,center.y,-8.4f},{0,0,1}};
  void* caster=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu),str("CurvedUIRaycaster"),0);
  void* hits=caster?FN(0x27c4a0,void*(*)(void*,TestRay,void*))(caster,ray,0):0;
  int count=hits?INT(hits,0x18):0;void* arr=hits?PTR(hits,0x10):0;void* first=count&&arr?PTR(arr,0x20):0;
  probe_ui[slot]=count;probe_ui[slot+1]=first==gameobject(t);probe_ui[slot+2]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);
  probe_ui[slot+3]=graphics_selected_v24;
  if(first){
   void* button=FN(0x94f410,void*(*)(void*,void*,void*))(first,str("Button"),0);
   if(button){
    void* domain=FN(0x14a920,void*(*)(void))();void* asm_=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.UI");
    void* img=FN(0x14a530,void*(*)(void*))(asm_);void* cls=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(img,"UnityEngine.EventSystems","PointerEventData");
    void* ev=FN(0x1c22e0,void*(*)(void*))(cls);FN(0x471c70,void(*)(void*,void*,void*))(ev,0,0);
    FN(0x472090,void(*)(void*,int,void*))(ev,0,0);FN(0x461da0,void(*)(void*,void*,void*))(button,ev,0);probe_ui[slot+5]=1;
   }
  }
  probe_ui[slot+6]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);probe_ui[slot+7]=graphics_selected_v24;
  if(command>=13&&command<=16){
   int p=88+(command-13)*16;
   const char* names[8]={"get_masterTextureLimit","get_anisotropicFiltering","get_shadows","get_shadowResolution","get_softParticles","get_realtimeReflectionProbes","get_shadowDistance","get_lodBias"};
   for(int j=0;j<8;j++){
    char buffer[128]="UnityEngine.QualitySettings::";int n=29,k=0;while(names[j][k])buffer[n++]=names[j][k++];buffer[n]=0;
    void* fn=FN(0x14b030,void*(*)(const char*))(buffer);probe_ui[p+j]=fn?(j<4?((int(*)(void))fn)():j<6?((_Bool(*)(void))fn)():(U64)(((float(*)(void))fn)()*1000.f)):0xffffffff;
   }
   probe_ui[p+8]=FN(0xa12bc0,int(*)(void*))(0);
   probe_ui[p+9]=(U64)(FN(0xed8c00,float(*)(void*))(0)*1000.f);
   probe_ui[p+10]=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),-1,0);
   probe_ui[p+11]=rooted(ui_v19_click_source)!=0;
  }
 }
'''.replace('CAMERA',camera).replace('SHOT',shot)
base=base[:start]+"debug = r'''"+debug+"'''\ndebug=debug.replace('SCREENSHOT_PATH',json.dumps(str(shot)))\n"+base[end:]
base=base.replace('probe_ui[96]','probe_ui[160]').replace("struct.unpack('<96Q',read(base+ex['probe_ui'],768))","struct.unpack('<160Q',read(base+ex['probe_ui'],1280))")
base=base.replace('range(160)','range(500)').replace('range(80)','range(300)')
base=base.replace("ex['probe_page_ready']","ex['probe_ticks']")
base=base.replace('    put(11);time.sleep(2)',"    assert snapshot[9], 'Graphics probe initialization not consumed by menu Update'\n    put(11);time.sleep(2)")
start=base.index('    rows=[]');end=base.index('\nfinally:',start)
base=base[:start]+'''    rows=[]
    for cmd,name in zip(range(12,18),('Open','LOW','MEDIUM','HIGH','ULTRA','Done')):
        slot=16+(cmd-12)*12;v=snapshot[slot:slot+9]
        rows.append(dict(control=name,hit_count=v[0],top_hit_is_target=bool(v[1]),panel_before=bool(v[2]),preset_before=v[3],unity_pointer_click_invoked=bool(v[5]),panel_after=bool(v[6]),preset_after=v[7]))
    values=[]
    for i in range(4):
        v=snapshot[88+i*16:100+i*16]
        values.append(dict(preset=i,texture_limit=v[0],aniso=v[1],shadows=v[2],shadow_resolution=v[3],soft_particles=v[4],reflections=v[5],shadow_distance=v[6]/1000,lod=v[7]/1000,aa=v[8],scale=v[9]/1000,saved_pref=v[10],click_audio_source=bool(v[11])))
    result=dict(rows=rows,values=values,actual_CurvedUI_GetObjectsHitByRay=True,unity_Button_OnPointerClick=True,direct_button_press_hook=False,working_or_live_modified=False,preferences_restored=True)
    (R/'analysis/v24-graphics-unity.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    assert all(row['top_hit_is_target'] and row['unity_pointer_click_invoked'] for row in rows)
    assert [row['preset_after'] for row in rows[1:5]]==list(range(4))
    assert rows[-1]['panel_after']==False
    assert [x['aa'] for x in values]==[0,2,4,4]
    assert [x['scale'] for x in values]==[.7,.85,.95,1.]
    assert [x['shadows'] for x in values]==[0,1,2,2]
    assert [x['saved_pref'] for x in values]==list(range(4))
''' +base[end:]
(R/'probe_graphics_v24.py').write_text(base)
print('Prepared probe_graphics_v24.py')
