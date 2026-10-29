/* Host-owned online court selection. Include after the v19 preferences helper.
 * RoomOptions.CustomRoomProperties is offset 0x20; RoomInfo properties is 0x18.
 * The day beach scene in this build is named "Scene", not "DayScene".
 * Only the two online call sites are redirected, preserving solo scene flow.
 */
static void* map_new_properties_v19(void){
 void* domain=FN(0x14a920,void*(*)(void))();
 void* assembly=FN(0x14a910,void*(*)(void*,const char*))(domain,"Photon3Unity3D");
 if(!assembly)return 0;
 void* image=FN(0x14a530,void*(*)(void*))(assembly);
 void* klass=FN(0x14a5a0,void*(*)(void*,const char*,const char*))(image,"ExitGames.Client.Photon","Hashtable");
 if(!klass)return 0;
 void* table=FN(0x14af40,void*(*)(void*))(klass);if(!table)return 0;
 FN(0x7b3430,void(*)(void*,void*))(table,0);
 return table;
}
EXPORT _Bool create_room_map_hook(void* name,void* options,void* lobby,void* expected_users,void* m){
 ensure_preferences_v19();
 if(options){
  BYTE(options,0x12)=online_format==2?4:8;
  void* properties=PTR(options,0x20);
  if(!properties){properties=map_new_properties_v19();if(properties)managed_field(options,0x20,properties);}
  if(properties)FN(0x7b3520,void(*)(void*,void*,void*,void*))(properties,str("Cloudcourt.Map"),str(preferred_map==1?"Scene":"IndoorArenaScene"),0);
 }
 return FN(0x60b4c0,_Bool(*)(void*,void*,void*,void*,void*))(name,options,lobby,expected_users,m);
}
EXPORT int online_room_map_v19(void){
 void* room=FN(0x61ed80,void*(*)(void*))(0);
 void* properties=room?PTR(room,0x18):0;if(!properties)return 0;
 void* key=str("Cloudcourt.Map");
 void* value=FN(0x7b34c0,void*(*)(void*,void*,void*))(properties,key,0);
 /* Ignore malformed/mismatched room properties before reading string fields. */
 if(!value||PTR(value,0)!=PTR(key,0))return 0;
 return text_equals(value,"Scene")||text_equals(value,"NightScene")||text_equals(value,"Beach")||text_equals(value,"DayScene");
}
EXPORT void* online_environment_map_hook(void* system,void* original,void* on_finished,void* m){
 (void)original;
 void* environment=str(online_room_map_v19()?"Scene":"IndoorArenaScene");
 return FN(0x251940,void*(*)(void*,void*,void*,void*))(system,environment,on_finished,m);
}
