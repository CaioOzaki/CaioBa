"""Meaningful visible-string audit plus real UI.Text/TMP translation fixtures."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/python'))
import UnityPy
from build_english_v21 import apply_english_v21,inventory_visible_text,replace_text,text_field

def snap(files):return {n:{i:o.get_raw_data() for i,o in f.objects.items()} for n,f in files.items()}
def validate(files):
    before=snap(files);report=apply_english_v21(files);after=snap(files)
    for n,f in files.items():
        assert set(before[n])==set(after[n])
        assert sorted(i for i,b in before[n].items() if after[n][i]!=b)==report['changed_objects'][n]
    rows=report['inventory'];paths={r['path'] for r in rows}
    # Pages can be inactive at save time but become visible through the menu.
    pages=['Start','Settings','Solo','Online','CreateRoom','JoinRoom','InRoom','InGame','Matchmaking','Alert']
    assert all(any(p.startswith('Menu/Pages/'+page+'/') for p in paths) for page in pages)
    assert any(p.startswith('Menu/CC_Customization/') for p in paths)
    assert any(p.startswith('GameRules/Scoreboard/') for p in paths)
    assert any(p.startswith('GameRulesBomb/Scoreboard/') for p in paths)
    assert all(any(p.startswith(f'CloudBoard{i}/') for p in paths) for i in (0,1))
    assert report['outline_targets']['title'][0]['classname']=='Text'
    assert report['outline_targets']['tagline'][0]['classname']=='Text'
    assert report['outline_targets']['title'][0]['id']==1081
    assert report['outline_targets']['tagline'][0]['id']==1086
    assert not report['portuguese_residuals']
    second=apply_english_v21(files);assert not any(second['changed_objects'].values())
    # Exercise both actual serialized schemas with accented, length-changing
    # Portuguese. This detects accidental prefix/tail/layout/callback mutation.
    normal=next(r for r in rows if r['path']=='Menu/Pages/InGame/Resume Button/Text')
    tmp=next(r for r in rows if r['classname']=='TextMeshProUGUI')
    restore={}
    for row,text in [(normal,'Personalização'),(tmp,'COMEÇANDO NOVO RALI')]:
        obj=files[row['file']].objects[row['id']];restore[(row['file'],row['id'])]=obj.get_raw_data();replace_text(obj,row['text_length_offset'],text)
    injected=snap(files);tested=apply_english_v21(files)
    assert {(c['file'],c['id'],c['after']) for c in tested['changes']}=={(normal['file'],normal['id'],'Customization'),(tmp['file'],tmp['id'],'STARTING NEW RALLY')}
    out=snap(files)
    for n in files:
        assert sorted(i for i,b in injected[n].items() if out[n][i]!=b)==tested['changed_objects'][n]
    from build_menu_v19 import set_raw
    for (n,i),b in restore.items():set_raw(files[n].objects[i],b)
    assert snap(files)==after
    return dict(passed=True,visible_text_count=report['visible_text_count'],ui_text_count=sum(r['classname']=='Text' for r in rows),
      tmp_count=sum(r['classname']=='TextMeshProUGUI' for r in rows),baseline_changed_objects=report['changed_objects'],
      metadata_and_offsets_verified=True,all_menu_pages_offline_online_match_prefabs_covered=True,
      hierarchy_callbacks_fonts_colors_network_keys_unchanged=True,accented_UI_Text_and_TMP_translation_fixtures_passed=True,
      idempotent=True,outline_targets=report['outline_targets'])

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=R/'working/VolleyballFever_Data');a=p.parse_args()
    names=['level0','level1','level2','level3','level4','resources.assets']+[f'sharedassets{i}.assets' for i in range(5)]
    files={n:UnityPy.load(str(a.source_dir/n)).file for n in names};report=validate(files)
    (R/'analysis/v21-english-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
