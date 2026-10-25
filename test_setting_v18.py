"""Execute shipped setting code across both teams, formats and network paths."""
from pathlib import Path
__file__=str(Path(__file__).with_name('test_comfort_v14.py'))
exec(Path(__file__).read_text().split('\nchecks=0')[0])
import math
cases=0
for base in (0x180000000,0x190000000):
 for fmt in (2,4):
  for online in (False,True):
   for team in (0,1):
    for x in (-5.,-2.1,-.45,1.2,3.3,5.):
     e=SettingEngine(base);e.flag('doubles_enabled',fmt==2);e.flag('quartet_enabled',fmt==4);e.flag('online_format',fmt);e.flag('online_version_ready',online);e.online=online
     e.integer(e.player+0x28,team);receiver=e.members[team][3];e.integer(receiver+0x28,team);e.ptr(receiver+0x20,e.areas[team][1]);e.pos[e.transforms[receiver]]=(x,0,(-1 if team==0 else 1)*5)
     # Actual team list, one receiving bot, and an invalid opponent decoy.
     lst=e.q(e.teams[team]+0x28);arr=e.q(lst+0x10);e.integer(lst+0x18,3);e.ptr(arr+0x20,e.player);e.ptr(arr+0x28,receiver);e.ptr(arr+0x30,e.members[1-team][0]);e.integer(e.members[1-team][0]+0x28,1-team)
     if online:e.call('net_new_rally_hook',e.game,1-team);e.receive(1-team);e.receive(team)
     e.used(team,1);sign=-1 if team==0 else 1;e.vec(e.pv,(2.8,1.5,sign*4))
     v=e.hit();assert v[1]>7
     t=(v[1]+math.sqrt(v[1]**2-19.62*1.15))/9.81
     target=(2.8+v[0]*t,1.5+v[1]*t-4.905*t*t,sign*4+v[2]*t)
     assert abs(target[0]-max(-3.65,min(3.65,x)))<1e-4,(fmt,online,team,x,target)
     assert abs(target[1]-2.65)<1e-4 and abs(target[2]-sign*1.15)<1e-4,target
     e.grips=[False,True];e.used(team,1);assert e.hit()==(0,1,8)
     cases+=1
report={'passed':True,'cases':cases,'formats':[2,4],'teams':[0,1],'online_and_solo':True,'ASLR_bases':2,'checks':['receiver lateral alignment','no forced fixed wing','near net on own side','inside sidelines','opponent excluded','both GRAB required']}
(R/'analysis/v18-setting-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
