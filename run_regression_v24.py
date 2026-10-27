"""Recoverable final native regression runner; resume only unchanged passed suites."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
TESTS=['test_spawn_input_v24.py','test_online_2v2.py','test_lobby_integrated_v21.py',
 'test_pause_v16.py','test_pause_audio_v23.py','test_customization_v19.py',
 'test_hand_visuals_integrated_v21.py','test_serve_roster_integrated_v21.py',
 'test_landing_projection_v22.py']
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 native=H(R/'working/GameAssembly.dll');dest=R/'analysis/v24-regression.json'
 prior=json.loads(dest.read_text()) if dest.exists() else {}
 passed={r['test']:r for r in prior.get('suites',[]) if r['passed']} if prior.get('native_sha256')==native else {}
 rows=[]
 for name in TESTS:
  test_hash=H(R/name)
  if name in passed and passed[name].get('source_sha256',test_hash)==test_hash:
   rows.append(dict(passed[name],source_sha256=test_hash));continue
  result=subprocess.run([sys.executable,str(R/name)],capture_output=True,text=True,timeout=300)
  (R/'analysis'/('v24-'+name.replace('.py','.log'))).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
  rows.append(dict(test=name,source_sha256=test_hash,passed=result.returncode==0,
   tail='' if result.returncode==0 else (result.stdout+result.stderr)[-3000:]))
  report=dict(passed=all(x['passed'] for x in rows),native_sha256=native,suites=rows,
   scope='Final compiled trigger, lobby, network/protocol, pause/audio, appearance and scoring regressions; no headset or real two-PC claim.')
  dest.write_text(json.dumps(report,indent=2))
  print(json.dumps(rows[-1]),flush=True)
  if result.returncode:sys.exit(result.returncode)
 assert native==H(R/'working/GameAssembly.dll')
 assert len(rows)==len(TESTS)
if __name__=='__main__':main()
