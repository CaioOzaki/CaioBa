"""Final v20 native regressions; assets have a separate current-version audit.

Use --rerun-failed to retain the complete report and retry only failed suites.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse, subprocess, sys, json, time, hashlib

R=Path(__file__).resolve().parent
REPORT=R/'analysis/v20-regressions.json'
JOBS=[['test_physics.py'],['test_2v2.py'],['test_formation_serve.py'],
      ['test_serve_delay.py'],['test_serve_rules.py'],['test_online_2v2.py'],
      ['test_reception.py'],['test_comfort_v14.py'],['test_hooks.py'],
      ['test_celebration_v15.py'],['test_motion_finite_v17.py'],['test_pause_v16.py'],
      ['test_gloves_v16.py','--asset','working/VolleyballFever_Data/resources.assets'],
      ['test_wall_boards_v17.py','--asset','working/VolleyballFever_Data/level3'],
      ['test_cloudcourt_v16.py'],['test_identity_rpc_v16.py'],['test_setting_v18.py'],
      ['test_lobby_v18.py'],['test_gameplay_v19.py'],['test_bot_contact_v19.py'],
      ['test_customization_v19.py'],['test_input_v19.py'],['test_map_v19.py'],
      ['test_score_outline_v20.py'],['test_landing_v20.py'],['test_skin_cache_v20.py'],
      ['test_bots_native_v20.py']]

def execute(args):
    start=time.monotonic()
    try:
        result=subprocess.run([sys.executable,str(R/args[0]),*args[1:]],cwd=R,
                              capture_output=True,text=True,encoding='utf-8',
                              errors='replace',timeout=600)
        output=result.stdout+result.stderr;code=result.returncode
    except subprocess.TimeoutExpired as error:
        output=f'Timed out after 600 seconds: {error}\n';code=124
    log=R/'analysis'/('v20-'+Path(args[0]).stem+'.log')
    log.write_text(output,encoding='utf-8')
    return {'test':args[0],'passed':code==0,'exit_code':code,
            'seconds':round(time.monotonic()-start,2),
            'log':str(log.relative_to(R))},output

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rerun-failed',action='store_true')
    parser.add_argument('--workers',type=int,default=3);options=parser.parse_args()
    binary=R/'working/GameAssembly.dll';binary_hash=hashlib.sha256(binary.read_bytes()).hexdigest();results={}
    if options.rerun_failed and REPORT.exists():
        previous=json.loads(REPORT.read_text());results={row['test']:row for row in previous['results']}
        if previous.get('binary_sha256',binary_hash)!=binary_hash:results={}
    selected=[args for args in JOBS if not options.rerun_failed or not results.get(args[0],{}).get('passed')]
    def save():
        ordered=[results[args[0]] for args in JOBS if args[0] in results]
        REPORT.write_text(json.dumps({'passed':len(ordered)==len(JOBS) and all(row['passed'] for row in ordered),
                          'completed':len(ordered),'total':len(JOBS),'results':ordered,'binary_sha256':binary_hash,
                          'excluded_intentionally':['test_assets_v18.py','test_menu_raycast_v16.py'],
                          'fixture_updates':[{'test':'test_2v2.py','change':'Require Beach label and inactive Beach Night, matching v19/v20 behavior.'},{'test':'test_online_2v2.py','change':'Expect the production v20 online room namespace.'}],
                          'scope':'Native machine code and original control flow with engine stubs. Final v20 assets audited separately; physical Quest 3 and two-PC playtest still pending.'},indent=2),encoding='utf-8')
    with ThreadPoolExecutor(max_workers=max(1,min(options.workers,3))) as pool:
        futures={pool.submit(execute,args):args for args in selected}
        for future in as_completed(futures):
            row,output=future.result();results[row['test']]=row;save()
            print(json.dumps(row),flush=True)
            if not row['passed']:print(output[-3000:],flush=True)
    save()
    raise SystemExit(not all(results.get(args[0],{}).get('passed',False) for args in JOBS))

if __name__=='__main__':main()
