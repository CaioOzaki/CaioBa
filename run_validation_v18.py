from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent
jobs=[['test_physics.py'],['test_2v2.py'],['test_formation_serve.py'],['test_serve_delay.py'],['test_serve_rules.py'],['test_online_2v2.py'],['test_reception.py'],['test_comfort_v14.py'],['test_hooks.py'],['test_celebration_v15.py'],['test_motion_finite_v17.py'],['test_pause_v16.py'],['test_menu_raycast_v16.py'],['test_gloves_v16.py','--asset','working/VolleyballFever_Data/resources.assets'],['test_wall_boards_v17.py','--asset','working/VolleyballFever_Data/level3'],['test_cloudcourt_v16.py'],['test_identity_rpc_v16.py'],['test_setting_v18.py'],['test_lobby_v18.py'],['test_assets_v18.py']]
results=[]
for args in jobs:
 start=time.time();result=subprocess.run([sys.executable,*[str(R/args[0]),*args[1:]]],cwd=R,capture_output=True,text=True)
 (R/'analysis'/('v18-'+Path(args[0]).stem+'.log')).write_text(result.stdout+result.stderr)
 row={'test':args[0],'passed':result.returncode==0,'seconds':round(time.time()-start,2)};results.append(row);print(json.dumps(row),flush=True)
 if result.returncode:print((result.stdout+result.stderr)[-1800:],flush=True)
 (R/'analysis/v18-regressions.json').write_text(json.dumps({'passed':all(x['passed'] for x in results),'completed':len(results),'total':len(jobs),'results':results},indent=2))
assert all(x['passed'] for x in results)
