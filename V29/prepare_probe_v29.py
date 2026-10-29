from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'probe_release_v28.py').read_text()
s=s.replace("F = R / 'tools/u28-custom'","F = R / 'tools/u29-release'").replace("B = R / 'versions/cloudcourt-v27-antes-v28'","B = R / 'versions/cloudcourt-v28-antes-v29'")
s=s.replace("for old in (B / 'fontes').glob('*.c'):","if args.asset:\n    for old in args.asset.parent.iterdir():\n        if old.name in {p.name for p in B.iterdir() if p.is_file()}:shutil.copyfile(old,W/'VolleyballFever_Data'/old.name)\nfor old in (B / 'fontes').glob('*.c'):")
extra=r'''
 if(probe_command>=60&&probe_command<=67&&start){
  int command=probe_command;probe_command=0;
  if(command==60){
   void* page=rooted(page_root);probe_ui[0]=(U64)page;
   if(page){online_selector=0;solo_stage=2;layout(page);probe_ui[1]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(PTR(page,0x58)),0);
    solo_stage=4;layout(page);probe_ui[2]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(PTR(page,0x58)),0);
    solo_stage=0;layout(page);probe_ui[3]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(PTR(page,0x58)),0);probe_ui[4]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(PTR(page,0x50)),0);
   }
  }
  else{
   int which=command==61||command==62?0:command==63||command==64?1:2;
   void* panel=refinement_panel_v29(which);
   const char* path=command==61?"CC_TrainEasy":command==62?"CC_TrainBack":command==63?"CC_StatsDone":command==64?"CC_StatsDone":command==65?"CC_RewardOutfitNext":command==66?"CC_RewardFaceNext":"CC_RewardsDone";
   if(command==65){rewards_progress_v29(5,5);rewards_refresh_v29(panel);}
   void* t=find_child(panel,path);probe_ui[0]=(U64)panel;probe_ui[1]=(U64)t;
   if(t){
    V3 center=position(t);typedef struct{V3 o,d;} RayV29;RayV29 ray={{center.x,center.y,-8.4f},{0,0,1}};
    void* menu=menu_transform_v19();void* caster=FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(menu),str("CurvedUIRaycaster"),0);
    void* hits=caster?FN(0x27c4a0,void*(*)(void*,RayV29,void*))(caster,ray,0):0;
    int count=hits?INT(hits,0x18):0;void* a=hits?PTR(hits,0x10):0;void* first=count&&a?PTR(a,0x20):0;
    probe_ui[2]=count;probe_ui[3]=first==gameobject(t);
    void* b=first?FN(0x94f410,void*(*)(void*,void*,void*))(first,str("Button"),0):0;
    if(b){button_press_hook(b,0);probe_ui[4]=1;}else probe_ui[4]=0;
    probe_ui[5]=FN(0x94f9a0,_Bool(*)(void*,void*))(gameobject(panel),0);
    probe_ui[6]=training_difficulty_v29;probe_ui[7]=rewards_packet_v29();probe_ui[8]=rewards_save_fn_v29!=0;
    if(command>=65){rewards_mirror_v29(customization_panel_v19());probe_ui[9]=(U64)rooted(rewards_mirror_state_v29.textures[0]);probe_ui[10]=(U64)rooted(rewards_mirror_state_v29.textures[1]);}
   }
  }
 }
'''
s=s.replace("source = source.replace(' probe_ticks++;', debug + '\\n probe_ticks++;')", "source = source.replace(' probe_ticks++;', debug + '\\n probe_ticks++;')")
anchor="source = source.replace(' probe_ticks++;', debug + '\\n probe_ticks++;')"
assert anchor in s
s=s.replace(anchor,'debug += '+repr(extra)+'\n'+anchor)
persistent=r'''
EXPORT extern int probe_command;EXPORT extern U64 probe_ui[256];
static unsigned probe_ball_v29;static int probe_practice_v29;
static void probe_persistent_v29(void){
 int cmd=probe_command;
 if(cmd>=80&&cmd<=82){probe_command=0;refinement_open_v29(cmd-80);return;}
 if(cmd==11){probe(rooted(probe_saved_start_v29));return;}
 if(cmd==59){probe_command=0;solo_entry_hook(rooted(probe_saved_start_v29),0);return;}
 if(cmd>=60&&cmd<=67){probe(rooted(probe_saved_start_v29));return;}
 if(cmd<70||cmd>79)return;probe_command=0;
 if(cmd==70){
  refinement_close_v29();customization_close_v19();graphics_close_v24();settings_close_v28();
  void* page=rooted(page_root);probe_ui[0]=(U64)page;
  if(page&&training_request_v29(2)){solo_stage=2;solo_start_hook(page,str("IndoorArenaScene"),0,0);}
  return;
 }
 void* rules=rooted(rules_root);void* player=local_avatar_player();void* body=player?PTR(player,0x80):0;
 probe_ui[0]=training_active_v29();probe_ui[1]=(U64)rules;probe_ui[2]=(U64)player;probe_ui[3]=(U64)body;
 void* teams=rules?PTR(rules,0x60):0;
 for(int i=0;i<2;i++){void* team=teams?PTR(teams,0x20+i*8):0;void* bots=team?PTR(team,0x30):0;probe_ui[4+i]=bots?INT(bots,0x18):999;}
 if(cmd==71){
  probe_ui[6]=training_start_attempt_v29(0);void* ball=rooted(training_ball_root_v29);root_set(&probe_ball_v29,ball);probe_ui[7]=(U64)ball;
 }
 if(cmd==72){
  void* ball=rooted(training_ball_root_v29);probe_ui[6]=rooted(probe_ball_v29)==ball;
  if(ball){V3 p=position(transform(ball));probe_ui[7]=(U64)((p.y+100)*1000);probe_ui[8]=(U64)((p.z+100)*1000);probe_ui[9]=(U64)PTR(ball,0x38);probe_ui[10]=(U64)PTR(ball,0x40);}
  probe_ui[11]=training_phase_v29;probe_ui[12]=stats_active_v29;
 }
 if(cmd==73){
  training_drill_v29=4;training_cooldown_v29=0;training_start_attempt_v29(0);
  void* ball=rooted(training_ball_root_v29);
  if(ball){training_motion_v29(ball,(V3){0,3,-1},(V3){0,-2,9},1,0,0,0);position_set(transform(ball),training_target_v29);bomb_ground_v28_hook(rules,ball,0);}
  refinement_tick_v29();probe_ui[6]=training_attempts_v29;probe_ui[7]=training_hits_v29;probe_ui[8]=rooted(probe_ball_v29)==ball;probe_ui[9]=rewards_counts_v29[5];
 }
 if(cmd==74){
  rewards_load_v29();rewards_choices_v29[0]=rewards_choices_v29[1]=1;
  if(body){skin_body(body);avatar_sleeves_v24(body);avatar_cosmetics_v28(body);rewards_body_v29(player,body,player_skin(player));}
  int n=0;for(int i=0;i<8;i++)if(rooted(rewards_bodies_v29[i].owner)==body){n=i+1;probe_ui[7]=(U64)rooted(rewards_bodies_v29[i].textures[0]);probe_ui[8]=(U64)rooted(rewards_bodies_v29[i].textures[1]);for(int j=0;j<2;j++){void* mat=rooted(rewards_bodies_v29[i].surfaces[j].material);probe_ui[11+j]=mat&&FN(0x9564b0,void*(*)(void*,void*))(mat,0)==rooted(rewards_bodies_v29[i].textures[j]);}}
  probe_ui[6]=n;probe_ui[9]=rewards_save_fn_v29!=0;
 }
 if(cmd==75){
  /* Follow the native Leave button, including its fade/disconnect task. */
  void* t=find_child(menu_transform_v19(),"Pages/InGame");
  void* controller=t?FN(0x94f410,void*(*)(void*,void*,void*))(gameobject(t),str("InGamePageController"),0):0;
  probe_ui[0]=(U64)controller;
  if(controller)FN(0x3142b0,void*(*)(void*,void*))(controller,0);
 }
 if(cmd==78){solo_entry_hook(rooted(probe_saved_start_v29),0);return;}
 if(cmd==79){void* page=rooted(page_root);if(page){solo_stage=2;solo_start_hook(page,str("Scene"),0,0);}return;}
 if(cmd==76){
  int known=0,plaques=0;for(int i=0;i<8;i++){BotRefineV29* b=&bots_refine_v29[i];if(alive(rooted(b->bot)))known++;if(alive(rooted(b->mine))&&alive(rooted(b->set)))plaques++;}
  probe_ui[6]=known;probe_ui[7]=plaques;probe_ui[8]=stats_active_v29;
 }
}
'''
# Add forward declaration/callback only inside disposable debug source.
anchor="(F / 'mode_2v2.c').write_text(source)"
s=s.replace(anchor,"source=source.replace('static void probe(void* start){','static void probe(void* start){if(start&&!rooted(probe_saved_start_v29))root_set(&probe_saved_start_v29,start);')\n"+anchor+"\nrsource=(F/'refinement_v29.c').read_text(encoding='utf-8-sig')\nrsource='static unsigned probe_saved_start_v29;static void probe(void*);static void probe_persistent_v29(void);\\n'+rsource.replace('static void refinement_tick_v29(void){','static void refinement_tick_v29(void){probe_persistent_v29();')\nrsource += "+repr(persistent)+"\n(F/'refinement_v29.c').write_text(rsource,encoding='utf8')")
# Extra real click tests run after legacy menu regression.
anchor="    result=dict(passed=False,settings=settings,visits=rows,"
idx=s.index(anchor)
pythonextra='''    newmenus=[]
    put(59);time.sleep(.8);put(60);time.sleep(.4);selector=list(snapshot()[:5]);assert selector[0] and selector[1:]==[0,0,1,1],selector
    for command in range(61,68):
        which=0 if command<=62 else 1 if command<=64 else 2
        put(80+which);time.sleep(.5)
        if command in (61,63,65):
            put(11);time.sleep(.5);shutil.copyfile(shot,shot.with_name('v29-release-'+['training','stats','rewards'][which]+'.png'))
        put(command);time.sleep(.4);a=list(snapshot()[:13]);newmenus.append(dict(command=command,state=a))
        assert a[0] and a[1] and a[2] and a[3] and a[4],('v29 actual modal click failed',command,a)
        if command in (62,63,64,67):assert a[5]==0,('v29 Done did not close',command,a)
        if command>=65:assert a[8],('PlayerPrefs Save icall missing',a)
    put(70);time.sleep(9);put(77);time.sleep(.5);practice=list(snapshot()[:14]);assert practice[0] and practice[1] and practice[2] and practice[3] and practice[4:6]==[0,0],practice
    put(71);time.sleep(.4);feed=list(snapshot()[:14]);assert feed[6] and feed[7],feed
    time.sleep(.4);put(72);time.sleep(.4);flight=list(snapshot()[:14]);assert flight[6] and flight[9] and flight[10] and not flight[12],flight
    put(73);time.sleep(.4);target=list(snapshot()[:14]);assert target[6:9]==[1,1,1],target
    put(74);time.sleep(.4);wear=list(snapshot()[:14]);assert wear[6] and wear[7] and wear[8] and wear[9] and wear[11:13]==[1,1],wear
    (R/'analysis/v29-probe-progress.json').write_text(json.dumps(dict(selector=selector,newmenus=newmenus,practice=practice,feed=feed,flight=flight,target=target,wear=wear),indent=2),encoding='utf8')
    put(75);time.sleep(4);put(78);time.sleep(.8);put(79);time.sleep(8);put(76);time.sleep(.4);ordinary=list(snapshot()[:14]);assert not ordinary[0] and ordinary[4]+ordinary[5]>0 and ordinary[6] and ordinary[7] and ordinary[8],ordinary
    persisted=pref_values();assert any(k.startswith('Cloudcourt.AccurateServes.v29') and v[0]>=5 for k,v in persisted.items()),'New skill progress was not saved to disk'
    v29=dict(skill_progress_saved_to_disk=True,actual_body_reward_textures=True,selector=selector,newmenus=newmenus,practice=practice,feed=feed,flight=flight,target=target,wear=wear,ordinary=ordinary)
'''
s=s[:idx]+pythonextra+s[idx:]
s=s.replace('result=dict(passed=False,settings=settings,visits=rows,','result=dict(passed=False,v29=v29,settings=settings,visits=rows,')
s=s.replace('v28-customization-unity-','v29-refinement-unity-').replace("'v28-'+args.tag","'v29-'+args.tag")
(R/'probe_release_v29.py').write_text(s,encoding='utf8')
print('v29 probe prepared')
