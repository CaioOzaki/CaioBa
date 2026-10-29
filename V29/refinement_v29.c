/* v29 modal navigation: existing native Solo Start owns scene/session creation. */
static unsigned refinement_panels_v29[3];
static int refinement_training_hits_v29,refinement_training_drill_v29;
static void* refinement_panel_v29(int which){
 if(which<0||which>2)return 0;
 void* panel=rooted(refinement_panels_v29[which]);
 if(!alive(panel)){const char* paths[3]={"CC_Training","CC_Stats","CC_Rewards"};panel=find_child(menu_transform_v19(),paths[which]);root_set(&refinement_panels_v29[which],panel);}
 return panel;
}
static void refinement_close_v29(void){
 for(int i=0;i<3;i++){void* panel=rooted(refinement_panels_v29[i]);if(alive(panel))FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),0,0);}
}
static void refinement_training_labels_v29(void){
 void* panel=refinement_panel_v29(0);if(!panel)return;
 child_label_v19(panel,"CC_TrainingState","Four skills. One ball. Fast, measured practice.");
 child_label_v19(panel,"CC_TrainingHint","Pick a drill. In court, release and press TRIGGER to repeat.\nGRAB controls the hand pose. Use the gold target to aim.");
 child_label_v19(panel,"CC_TrainDifficultyState",training_difficulty_v29==0?"EASY - wide targets":training_difficulty_v29==2?"CHALLENGE - tight targets":"STANDARD - balanced targets");
}
static void refinement_open_v29(int which){
 refinement_close_v29();customization_close_v19();graphics_close_v24();settings_close_v28();
 void* panel=refinement_panel_v29(which);if(!panel)return;
 if(which==0)refinement_training_labels_v29();
 if(which==1)stats_open_v29(menu_transform_v19());
 if(which==2)rewards_refresh_v29(panel);
 FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);
}
static int refinement_button_v29(void* button){
 void* page=rooted(page_root);
 if(page&&solo_stage==0&&!online_selector&&button==PTR(page,0x50)){refinement_open_v29(0);return 1;}
 if(named(button,"CC_StatsOpen")){refinement_open_v29(1);return 1;}
 if(named(button,"CC_RewardsOpen")){refinement_open_v29(2);return 1;}
 if(named(button,"CC_StatsDone")){refinement_close_v29();return 1;}
 if(named(button,"CC_RewardsDone")){
  refinement_close_v29();void* panel=customization_panel_v19();if(panel){customization_refresh_v19();FN(0x94f700,void(*)(void*,_Bool,void*))(gameobject(panel),1,0);}return 1;
 }
 if(named(button,"CC_TrainBack")){refinement_close_v29();return 1;}
 if(rewards_button_v29(button))return 1;
 if(training_button_v29(button)){refinement_training_labels_v29();return 1;}
 const char* names[4]={"CC_TrainServe","CC_TrainReceive","CC_TrainSet","CC_TrainSpike"};
 for(int i=0;i<4;i++)if(named(button,names[i])){
  if(page&&training_request_v29(i+1)){
   refinement_close_v29();solo_stage=2;
   solo_start_hook(page,str(preferred_map?"Scene":"IndoorArenaScene"),0,0);
  }return 1;
 }
 /* Other existing screens close the independent v29 overlay. */
 if(named(button,"CC_CustomizeOpen")||named(button,"CC_GraphicsOpen")||named(button,"CC_SettingsOpen"))refinement_close_v29();
 return 0;
}
static void refinement_tick_v29(void){
 training_tick_v29();stats_tick_v29();rewards_tick_v29();
 if(!training_active_v29()){refinement_training_hits_v29=0;refinement_training_drill_v29=0;return;}
 if(refinement_training_drill_v29!=training_drill_v29||training_hits_v29<refinement_training_hits_v29){refinement_training_hits_v29=0;refinement_training_drill_v29=training_drill_v29;}
 int earned=training_hits_v29-refinement_training_hits_v29;
 if(earned>0&&(training_drill_v29==1||training_drill_v29==4))rewards_progress_v29(training_drill_v29==1?5:6,earned);
 refinement_training_hits_v29=training_hits_v29;
}
static void refinement_menu_v29(void){refinement_close_v29();stats_menu_v29(menu_transform_v19());}
