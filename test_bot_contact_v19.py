"""Ballistic contact window using unchanged native set and real Bot.Update.

The final overlap check models a 2m body plus ball radius, not Unity collision.
"""
from pathlib import Path
scope={'__file__':str(Path(__file__).with_name('test_gameplay_v19.py'))}
exec(Path(scope['__file__']).read_text().split('\nchecks=[]')[0],scope)
GameplayEngine=scope['GameplayEngine'];R=scope['R'];json=scope['json']
cases=[]
for base,fmt,online,team in ((0x180000000,2,False,0),(0x190000000,4,True,1)):
 e=GameplayEngine(base);e.settings(fmt,online);e.team_setup(team);e.used(team,2)
 start=(0,1.5,e.side*4);target=(0,2.65,e.side*1.15)
 out=e.alloc();a=e.alloc();b=e.alloc();e.vec(a,start);e.vec(b,target)
 e.call('setting_arc',out,a,b);velocity=e.vec(out);contact=None
 for frame in range(1,220):
  t=frame*e.dt;p=(0,start[1]+velocity[1]*t-4.905*t*t,start[2]+velocity[2]*t)
  e.pos[e.transforms[e.ball]]=p;e.vec(e.ball+0x8c,(velocity[0],velocity[1]-9.81*t,velocity[2]));e.update()
  bot=e.pos[e.transforms[e.bot]]
  if abs(p[2]-bot[2])<.55 and bot[1]-.1<=p[1]<=bot[1]+2.1:
   contact={'time':t,'ball_height':p[1],'bot_jump_height':bot[1]};break
 assert contact and contact['ball_height']>3.0 and contact['bot_jump_height']>.5,contact
 cases.append({'format':fmt,'online':online,'team':team,'velocity':velocity,'contact':contact})
report={'passed':True,'cases':cases,'scope':'Native unmodified set arc and Bot.Update with a simplified overlap volume; does not replace Unity/Quest collider validation.'}
(R/'analysis/v19-bot-contact-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
