/* Include after comfort_v14.c, before identity_v16.c. Keep avatar UV style and
 * hand tone independent: all existing face/outfit indices stay in [0,80]. */
static int preferred_hand_tone_v21;
static const char* hand_tone_names_v21[6]={"Porcelain","Sand","Honey","Caramel","Cocoa","Ebony"};
static const Q4 hand_tone_colors_v21[6]={
 {1.f,.85f,.74f,1},{.91f,.69f,.49f,1},{.76f,.49f,.29f,1},
 {.58f,.32f,.17f,1},{.36f,.18f,.10f,1},{.19f,.085f,.05f,1}};
static int local_pose_v21;
EXPORT int local_hand_pose_v21(void){return local_pose_v21;}
typedef struct {unsigned player;int tone,pose;} HandToneChoiceV21;
static HandToneChoiceV21 hand_tones_v21[8];
EXPORT int appearance_pack_pose_v21(int team,int style,int change,int tone,int pose){
 if(team<0||team>1||style<0||style>=81||tone<0||tone>=6||pose<0||pose>4)return -1;
 return 0x5c210000|team|((style%9)<<1)|((style/9)<<5)|(change?0x200:0)|(tone<<10)|(pose<<13);
}
EXPORT int appearance_pack_v21(int team,int style,int change,int tone){return appearance_pack_pose_v21(team,style,change,tone,0);}
EXPORT int appearance_pose_v21(int value){return (value>>13)&7;}
EXPORT int appearance_decode_v21(int value,int* team,int* style,int* change,int* tone){
 if(((unsigned)value&0xffff0000u)!=0x5c210000u)return 0;
 int f=(value>>1)&15,o=(value>>5)&15,t=(value>>10)&7;
 if(f>=9||o>=9||t>=6||appearance_pose_v21(value)>4)return -1;
 *team=value&1;*style=f+9*o;*change=(value&0x200)!=0;*tone=t;return 1;
}
static void remember_hand_tone_v21(void* player,int tone){
 if(!player||tone<0||tone>=6)return;
 for(int i=0;i<8;i++)if(rooted(hand_tones_v21[i].player)==player||!alive(rooted(hand_tones_v21[i].player))){
  if(rooted(hand_tones_v21[i].player)!=player)hand_tones_v21[i].pose=0;
  root_set(&hand_tones_v21[i].player,player);hand_tones_v21[i].tone=tone;return;
 }
}
static void remember_hand_pose_v21(void* player,int pose){
 if(!player||pose<0||pose>4)return;
 for(int i=0;i<8;i++)if(rooted(hand_tones_v21[i].player)==player){hand_tones_v21[i].pose=pose;return;}
}
static int player_hand_pose_v21(void* player){
 if(player==local_avatar_player())return local_pose_v21;
 for(int i=0;i<8;i++)if(rooted(hand_tones_v21[i].player)==player)return hand_tones_v21[i].pose;
 return 0;
}
static int player_hand_tone_v21(void* player){
 if(!network_physics()||player==online_local_player())return preferred_hand_tone_v21;
 for(int i=0;i<8;i++)if(rooted(hand_tones_v21[i].player)==player)return hand_tones_v21[i].tone;
 return 0;
}
EXPORT int hand_pose_v21(int left,int right,int ready,int side){
 return ((side?right:left)!=0)?(left&&right&&ready?1:2):0;
}
