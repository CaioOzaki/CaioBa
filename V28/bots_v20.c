/* Host chooses nine possible identities without replacement for up to 8 slots.
 * Character indices travel in the existing Client_AssignBotToTeam RPC. Clients
 * never reroll them, so rotations and human team swaps retain the same model.
 * Include after the shared rooting/string helpers. See fix_bot_v20.py.
 */
static const int bot_database_indices_v20[9]={39,12,30,21,15,18,0,45,6};
static unsigned bot_roster_rules_v20;
EXPORT unsigned bot_roster_mask_v20;
static int bot_spawn_context_v20;
EXPORT void bots_roster_reset_v20(void* rules){
 root_set(&bot_roster_rules_v20,rules);bot_roster_mask_v20=0;bot_spawn_context_v20=0;
}
EXPORT void bots_spawn_begin_v20(void* rules,int team,int slot){
 bot_spawn_context_v20=0;
 if(!rules||team<0||team>1||slot<0||slot>3)return;
 if(rooted(bot_roster_rules_v20)!=rules)bots_roster_reset_v20(rules);
 bot_spawn_context_v20=1;
}
EXPORT void bots_spawn_end_v20(void){bot_spawn_context_v20=0;}
EXPORT void* bot_character_box_hook(void* klass,void* value){
 if(!bot_spawn_context_v20||!value)return FN(0x14ba70,void*(*)(void*,void*))(klass,value);
 int requested=*(int*)value,start=requested<0?0:requested%9;
 for(int step=0;step<9;step++){
  int identity=(start+step)%9;
  if(!(bot_roster_mask_v20&(1u<<identity))){
   int selected=bot_database_indices_v20[identity];bot_roster_mask_v20|=1u<<identity;
   return FN(0x14ba70,void*(*)(void*,void*))(klass,&selected);
  }
 }
 /* More than nine simultaneous spawns is outside the 2x4 court contract.
  * Leave an unexpected external caller's value intact rather than write OOB. */
 return FN(0x14ba70,void*(*)(void*,void*))(klass,value);
}
