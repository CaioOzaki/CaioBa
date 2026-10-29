"""Prepare the ball-only disposable Unity probe from the v27 checkpoint.

The reused process runner owns only its launched process and restores PlayerPrefs.
No working DLL or assets are patched. Run generated probe_ball_spawn_v28.py.
"""
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'probe_ui_v26.py').read_text()
s=s.replace("F = R / 'tools/u26-ui'","F = R / 'tools/u28-ball'")
s=s.replace("B = R / 'versions/cloudcourt-v25-antes-v26'","B = R / 'versions/cloudcourt-v27-antes-v28'")
s=s.replace("for name in [p.name for p in R.glob('*.c')]:\n    shutil.copyfile(R/name,F/name)","shutil.copyfile(R/'ball_style_v26.c',F/'ball_style_v26.c')")
s=s.replace("builder = (R / 'build_patch.py').read_text()","builder = (B / 'fontes/build_patch.py').read_text()")
a=s.index("debug = r'''");b=s.index("source = source.replace(' probe_ticks++;'",a)
debug=r'''
 if(probe_command==40&&start){
  probe_command=0;
  void* domain=FN(0x14a920,void*(*)(void))();
  void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");
  void* image=FN(0x14a530,void*(*)(void*))(assembly);
  void* gc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","GameObject");
  void* cc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","Camera");
  void* cameraGo=FN(0x1c22e0,void*(*)(void*))(gc);FN(0x94f8d0,void(*)(void*,void*,void*))(cameraGo,str("BallSpawnProbeCamera"),0);
  void* type=FN(0x14b9c0,void*(*)(void*))(FN(0x14a710,void*(*)(void*))(cc));
  void* cam=FN(0x94f240,void*(*)(void*,void*,void*))(cameraGo,type,0);probe_ui[100]=(U64)cam;
  position_set(transform(cam),(V3){0,1.4f,-6.65f});FN(0xb75750,void(*)(void*,Q4,void*))(transform(cam),(Q4){0,0,0,1},0);
  FN(0x949a60,void(*)(void*,float,void*))(cam,999,0);FN(0x949b00,void(*)(void*,float,void*))(cam,35,0);
  FN(0x9499a0,void(*)(void*,int,void*))(cam,2,0);FN(0x9499e0,void(*)(void*,int,void*))(cam,-1,0);
  for(int i=0;i<2;i++){
   void* prefab=FN(0xb6b7b0,void*(*)(void*,void*))(str(i?"VolleyballBomb":"Volleyball"),0);
   void* go=prefab?FN(0xa0b7a0,void*(*)(void*,V3,Q4,void*))(prefab,(V3){i?.4f:-.4f,1.4f,-5.f},(Q4){0,0,0,1},0):0;
   void* ball=go?FN(0x94f410,void*(*)(void*,void*,void*))(go,str("Volleyball"),0):0;
   probe_ui[i*40]=(U64)ball;
   if(ball){
    FN(0x77e220,void(*)(void*,void*))(ball,0);
    void* local=PTR(ball,0x30);if(local)FN(0xec5e00,void(*)(void*,_Bool,void*))(local,1,0);
   }
  }
 }
 if(probe_command>=41&&probe_command<=44&&start){
  int command=probe_command;probe_command=0;
  for(int i=0;i<2;i++){
   int k=i*40;void* ball=(void*)probe_ui[k];if(!ball)continue;
   if(command==42)FN(0x77ee60,void(*)(void*,void*))(ball,0);
   if(command==43)FN(0x77ee30,void(*)(void*,void*))(ball,0);
   if(command==44){
    void* visual=PTR(ball,0x38);void* regular=find_child(visual,"RegularMesh");
    void* fallback=regular?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(regular),str("MeshRenderer"),0):0;
    if(fallback)FN(0xa1b2f0,void(*)(void*,_Bool,void*))(fallback,1,0);
   }
   void* visual=PTR(ball,0x38);void* native=PTR(ball,0x40);
   void* old=find_child(transform(ball),"VisualVolleyball/RegularMesh/DavidVolleyball");
   void* t=find_child(visual,"RegularMesh/DavidVolleyball");
   void* renderer=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshRenderer"),0):0;
   void* mf=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("MeshFilter"),0):0;
   void* mesh=mf?FN(0xa062c0,void*(*)(void*,void*))(mf,0):0;
   void* mat=renderer?FN(0xa1af10,void*(*)(void*,void*))(renderer,0):0;
   probe_ui[k+1]=(U64)visual;probe_ui[k+2]=(U64)old;probe_ui[k+3]=(U64)t;
   probe_ui[k+4]=(U64)renderer;probe_ui[k+5]=renderer?FN(0xa1b1e0,_Bool(*)(void*,void*))(renderer,0):0;
   probe_ui[k+6]=(U64)native;probe_ui[k+7]=native?FN(0xa1b1e0,_Bool(*)(void*,void*))(native,0):0;
   probe_ui[k+8]=(U64)mat;probe_ui[k+9]=mesh?FN(0xa09680,int(*)(void*,void*))(mesh,0):0;
   probe_ui[k+10]=mat?(U64)(FN(0x955350,int(*)(void*,void*,void*))(mat,str("_Mode"),0)*1000):0;
   probe_ui[k+11]=(U64)PTR(ball,0x60);probe_ui[k+12]=(U64)PTR(ball,0x80);
   probe_ui[k+13]=mat?FN(0x9556c0,_Bool(*)(void*,void*,void*))(mat,str("_ALPHAPREMULTIPLY_ON"),0):0;
  }
 }
 if(probe_command==47&&start){
  probe_command=0;void* cam=(void*)probe_ui[100];
  void* domain=FN(0x14a920,void*(*)(void))();void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"UnityEngine.CoreModule");
  void* image=FN(0x14a530,void*(*)(void*))(assembly);
  void* rc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","RenderTexture");
  void* tc=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"UnityEngine","Texture2D");
  void* rt=FN(0x1c22e0,void*(*)(void*))(rc);FN(0xa1a6f0,void(*)(void*,int,int,int,void*))(rt,1024,768,24,0);FN(0xa19430,_Bool(*)(void*,void*))(rt,0);
  FN(0x949e00,void(*)(void*,void*,void*))(cam,rt,0);FN(0x948b30,void(*)(void*,void*))(cam,0);FN(0xa19c20,void(*)(void*,void*))(rt,0);
  void* tex=FN(0x1c22e0,void*(*)(void*))(tc);FN(0xb71570,void(*)(void*,int,int,int,_Bool,void*))(tex,1024,768,3,0,0);
  FN(0xb70cb0,void(*)(void*,Q4,int,int,_Bool,void*))(tex,(Q4){0,0,1024,768},0,0,0,0);FN(0xb702b0,void(*)(void*,_Bool,_Bool,void*))(tex,0,0,0);
  void* png=FN(0xedbea0,void*(*)(void*,void*))(tex,0);if(png)FN(0x5cf690,void(*)(void*,void*,void*))(str(BALL_SHOT),png,0);
  FN(0xa19c20,void(*)(void*,void*))(0,0);FN(0x949e00,void(*)(void*,void*,void*))(cam,0,0);
  FN(0xa0ab40,void(*)(void*,void*))(tex,0);FN(0xa0ab40,void(*)(void*,void*))(rt,0);
 }
'''
debug=debug.replace('BALL_SHOT','SCREENSHOT_PATH')
# Keep the fixed ball module optional so the same runner proves the old failure.
s=s[:a]+"debug = "+repr(debug)+"\ndebug=debug.replace('SCREENSHOT_PATH',json.dumps(str(shot)))\n"+s[b:]
s=s.replace("parser.add_argument('--tag', default='before')","parser.add_argument('--tag', default='after')\nparser.add_argument('--before', action='store_true')")
s=s.replace("shutil.copyfile(R/'ball_style_v26.c',F/'ball_style_v26.c')","\nif not args.before:shutil.copyfile(R/'ball_style_v26.c',F/'ball_style_v26.c')")
a=s.index('    put(10)');b=s.index('\nfinally:',a)
s=s[:a]+'''    put(40);time.sleep(2)
    rows=[]
    for command in (41,42,41,43,41,44,41):
        put(command);time.sleep(.4)
        snapshot=struct.unpack('<256Q',read(base+ex['probe_ui'],2048))
        rows.append(dict(command=command,balls=[list(snapshot[:14]),list(snapshot[40:54])]))
    put(47);time.sleep(.7)
    render=shot.with_name('v28-ball-'+args.tag+'.png');shutil.copyfile(shot,render)
    result=dict(passed=True,before=args.before,rows=rows,scope='Actual Unity object Instantiate and native Awake, both resource prefabs, native transparent/solid changes, fallback re-enable',working_or_live_modified=False,preferences_restored=True)
    (R/('analysis/v28-ball-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
    assert all(row['balls'][i][0] and row['balls'][i][1] and not row['balls'][i][2] and row['balls'][i][3] for row in rows for i in range(2)), 'Awake hierarchy detachment mismatch'
    if not args.before:
        for row in rows:
            for ball in row['balls']:
                assert ball[5] and ball[9]==6144, ('authored renderer missing',row)
        assert all(not ball[7] for ball in rows[-1]['balls']), 'Fallback re-enable was not repaired'
        assert all(ball[10]==3000 and ball[13] for ball in rows[2]['balls']), 'Transparent material state not mirrored'
        assert all(ball[10]==0 and not ball[13] for ball in rows[4]['balls']), 'Solid material state not restored'
    result['screenshot']=str(render)
    (R/('analysis/v28-ball-unity-'+args.tag+'.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
''' +s[b:]
s=s.replace('ZIG_LOCAL_CACHE_DIR=str(R / \'tools/zig-cache-ui22\')','ZIG_LOCAL_CACHE_DIR=str(R / \'tools/zig-cache-ball28\')').replace('ZIG_GLOBAL_CACHE_DIR=str(R / \'tools/zig-cache-ui22\')','ZIG_GLOBAL_CACHE_DIR=str(R / \'tools/zig-cache-ball28\')')
(R/'probe_ball_spawn_v28.py').write_text(s)
print('Prepared probe_ball_spawn_v28.py')
