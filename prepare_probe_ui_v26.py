"""Use an isolated current-build Unity copy to inspect preview cache lifetimes."""
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'probe_ui_v22.py').read_text()
s=s.replace('tools/u22-ui','tools/u26-ui').replace('versions/cloudcourt-v21-antes-v22','versions/cloudcourt-v25-antes-v26')
s=s.replace("for name in ('customization_v19.c','avatar_style_v21.c','score_outline_v20.c'):","for name in [p.name for p in R.glob('*.c')]:")
s=s.replace("source=source.replace('#include \\\"identity_v16.c\\\"','#include \\\"avatar_style_v21.c\\\"\\n#include \\\"identity_v16.c\\\"')",'')
s=s.replace("builder = (B / 'fontes/build_patch.py').read_text()","builder = (R / 'build_patch.py').read_text()")
s=s.replace("probe_ui[96]","probe_ui[256]").replace("struct.unpack('<96Q',read(base+ex['probe_ui'],768))","struct.unpack('<256Q',read(base+ex['probe_ui'],2048))")
s=s.replace("ex['probe_page_ready']","ex['probe_ticks']").replace('range(160)','range(600)')
s=s.replace('    put(10)\n','    time.sleep(6)  # Wait for startup Indoor scene load before creating a debug camera.\n    put(10)\n')
start=s.index("source = source.replace(' probe_ticks++;'")
extra=r'''
debug += r"""
 if(probe_command==20&&start){
  probe_command=0;customization_close_v19();
  /* Run the real page-entry hook between visits, as the menu transition does. */
  main_menu_hook(start,0,0);
  void* panel=customization_panel_v19();
  if(panel){customization_refresh_v19();FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);}
 }
 if(probe_command==21&&start){
  probe_command=0;void* panel=customization_panel_v19();
  for(int i=0;i<2;i++){
   void* t=find_child(panel,i?"CC_OutfitPreview":"CC_FacePreview");
   void* raw=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("RawImage"),0):0;
   void* fx=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("CurvedUIVertexEffect"),0):0;
   int k=100+i*20;probe_ui[k]=(U64)raw;probe_ui[k+1]=(U64)fx;
   if(raw){Q4 uv=*(Q4*)((char*)raw+0xd0);probe_ui[k+2]=(U64)(uv.x*10000);probe_ui[k+3]=(U64)(uv.y*10000);}
   if(fx){probe_ui[k+4]=BYTE(fx,0x58);probe_ui[k+5]=BYTE(fx,0x59);probe_ui[k+6]=(U64)PTR(fx,0x160);probe_ui[k+7]=(U64)PTR(fx,0x168);}
  }
 }
 if(probe_command==30&&start){
  probe_command=0;customization_close_v19();
  void* domain=FN(0x14a920,void*(*)(void))();
  void* core=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");
  void* ci=FN(0x14a530,void*(*)(void*))(core);
  void* gc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(ci,"UnityEngine","GameObject");
  void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"Unity.TextMeshPro");
  void* image=assembly?FN(0x14a530,void*(*)(void*))(assembly):0;
  void* cls=image?FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"TMPro","TextMeshPro"):0;
  probe_ui[155]=(U64)assembly;probe_ui[156]=(U64)image;probe_ui[157]=(U64)cls;
  if(cls){
   void* go=FN(0x1c22e0,void*(*)(void*))(gc);FN(0x94f8d0,void(*)(void*,void*,void*))(go,str("Cloudcourt Point Popup Probe"),0);
   void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(cls));
   void* text=FN(0x94f240,void*(*)(void*,void*,void*))(go,type,0);probe_ui[150]=(U64)text;
   if(text){
    style_tmp(text);FN(0x23f9d0,void(*)(void*,float,void*))(text,48,0);
    void* rt=FN(0x94f410,void*(*)(void*,void*,void*))(go,str("RectTransform"),0);
    if(rt)FN(0xa17260,void(*)(void*,V2,void*))(rt,(V2){600,200},0);
    position_set(transform(text),(V3){-1.6f,1.9f,-6.f});FN(0xb75750,void(*)(void*,Q4,void*))(transform(text),(Q4){0,0,0,1},0);
    FN(0xb75560,void(*)(void*,V3,void*))(transform(text),(V3){.006f,.006f,.006f},0);
    FN(0x2405f0,void(*)(void*,void*,void*))(text,str("<color=#75CFFF>BLUE +1</color>\n<size=60%>Four touches by red team</size>"),0);
    void* mat=FN(0x23e790,void*(*)(void*,void*))(text,0);probe_ui[151]=(U64)mat;
    probe_ui[152]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("OUTLINE_ON"),0):0;
    score_outline_tmp_force_v21(text);
    probe_ui[153]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("OUTLINE_ON"),0):0;
    probe_ui[154]=(U64)(FN(0x23eba0,float(*)(void*,void*))(text,0)*10000);
   }
  }
 }
 if(probe_command==31&&start){
  probe_command=0;probe_ui[160]=graphics_running_v26;probe_ui[161]=FN(0xa12bc0,int(*)(void*))(0);
  const char* buttons[4]={"CC_GraphicsLow","CC_GraphicsMedium","CC_GraphicsHigh","CC_GraphicsUltra"};
  int selected=(graphics_running_v26+1)%4;void* t=find_child(graphics_panel_v24(),buttons[selected]);
  void* button=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("Button"),0):0;
  if(button)graphics_button_v24(button);
  probe_ui[162]=graphics_selected_v24;probe_ui[163]=graphics_running_v26;probe_ui[164]=FN(0xa12bc0,int(*)(void*))(0);
  probe_ui[165]=FN(0xa12690,int(*)(void*,int,void*))(str("Cloudcourt.Graphics.v24"),-1,0);
 }
 if(probe_command==32&&start){
  probe_command=0;void* text=(void*)probe_ui[150];
  if(text){
   score_outline_tmp_force_v21(text);
   void* mat=FN(0x23e790,void*(*)(void*,void*))(text,0);probe_ui[172]=(U64)mat;
   probe_ui[153]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("OUTLINE_ON"),0):0;
   probe_ui[171]=mat?FN(0x955630,_Bool(*)(void*,void*,void*))(mat,str("_OutlineWidth"),0):0;
   void* shader=mat?FN(0x9565d0,void*(*)(void*,void*))(mat,0):0;
   probe_ui[170]=shader?(U64)FN(0xa0bdd0,void*(*)(void*,void*))(shader,0):0;
  }
 }
"""
'''
s=s[:start]+extra+s[start:]
start=s.index('    put(11);time.sleep(2)')
end=s.index('\nfinally:',start)
s=s[:start]+'''    assert snapshot[9], 'Main-thread probe was not initialized'
    rows=[]
    for visit in range(2):
        if visit:put(20);time.sleep(1)
        put(11);time.sleep(1)
        before=shot.with_name('v26-'+args.tag+'-visit'+str(visit)+'-before.png');shutil.copyfile(shot,before)
        put(21);time.sleep(.4);a=struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
        put(12);time.sleep(.5);put(13);time.sleep(.5)
        put(21);time.sleep(.4);b=struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
        put(11);time.sleep(1)
        after=shot.with_name('v26-'+args.tag+'-visit'+str(visit)+'-after.png');shutil.copyfile(shot,after)
        rows.append(dict(visit=visit,before=str(before),after=str(after),before_cache=list(a[100:140]),after_cache=list(b[100:140]),face_click=list(b[16:28]),outfit_click=list(b[28:40])))
    put(30);time.sleep(1);put(32);time.sleep(.5);put(11);time.sleep(1)
    popup_shot=shot.with_name('v26-'+args.tag+'-popup.png');shutil.copyfile(shot,popup_shot)
    put(31);time.sleep(.5);snapshot=struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
    shader_name=read(snapshot[170]+0x14,struct.unpack('<i',read(snapshot[170]+0x10,4))[0]*2).decode('utf-16-le') if snapshot[170] else None
    result=dict(passed=True,visits=rows,popup=list(snapshot[150:160]),popup_material=list(snapshot[170:174]),shader_name=shader_name,popup_screenshot=str(popup_shot),graphics=list(snapshot[160:166]),working_or_live_modified=False,preferences_restored=True,real_menu_hook_between_visits=True)
    (R/('analysis/v26-ui-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
    assert snapshot[150] and snapshot[153] and 1700<=snapshot[154]<=1900,'Actual TMP outline variant not enabled'
    assert snapshot[160]==snapshot[163] and snapshot[161]==snapshot[164] and snapshot[162]==snapshot[165] and snapshot[162]!=snapshot[160],'Live graphics mutated or preference not saved'
    (R/('analysis/v26-ui-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
''' +s[end:]
(R/'probe_ui_v26.py').write_text(s,encoding='utf-8')
print('Prepared',R/'probe_ui_v26.py')
