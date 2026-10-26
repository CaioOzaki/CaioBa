"""Execute production input helpers with listener-paused and missing-icall cases."""
from pathlib import Path
import json
from test_input_v19 import InputEngine
R=Path(__file__).resolve().parent
rows=[]
for base in (0x180000000,0x190000000):
    e=InputEngine(base)
    e.listener_paused=True
    e.call('click_probe',e.button)
    assert e.listener_paused and e.played==e.audible_plays==1
    assert e.pause_resolves==1 and len(e.ignore_listener_pause)==1
    original_source=next(iter(e.ignore_listener_pause))
    e.listener_paused=False
    e.call('click_probe',e.alloc())
    e.listener_paused=True
    e.call('click_probe',e.alloc())
    assert e.played==e.audible_plays==3
    assert e.source_count==e.clip_count==e.pause_resolves==1
    # Unity can destroy the original owner across a scene lifecycle. Recreated
    # sources must receive the flag too; the icall itself stays cached.
    e.dead.add(original_source)
    e.call('click_probe',e.button)
    assert e.source_count==2 and e.clip_count==1 and e.pause_resolves==1
    assert e.played==e.audible_plays==4 and len(e.ignore_listener_pause)==2
    e.locked.add(e.button);e.call('click_probe',e.button)
    e.locked.clear();e.inactive.add(e.button);e.call('click_probe',e.button)
    assert e.played==e.audible_plays==4 and e.listener_paused
    fallback=InputEngine(base)
    fallback.missing_pause_api=True
    fallback.call('click_probe',fallback.button)
    fallback.call('click_probe',fallback.button)
    assert fallback.played==fallback.audible_plays==2
    assert fallback.pause_resolves==1 and not fallback.ignore_listener_pause
    rows.append(dict(base=hex(base),cached_ui_source=True,recreated_source_configured=True,listener_state_preserved=True,inactive_locked_silent=True,null_icall_safe=True))
report=dict(passed=True,rows=rows,checks=['Only the UI AudioSource ignores AudioListener.pause','Resolver cached including null result','Cached source and clip across scene/button changes','Recreated source receives the setting','Disabled and inactive buttons stay silent'])
(R/'analysis/v23-pause-audio-native-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
