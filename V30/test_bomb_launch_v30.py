"""Regression for the actual missing native human-placement dependency."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'tools/python'),str(R)]
import UnityPy
from build_bomb_launch_v30 import bomb_placement_audit_v30,apply_bomb_launch_v30
f=UnityPy.load(str(R/'versions/cloudcourt-v29-antes-v30/resources.assets')).file
before=bomb_placement_audit_v30(f)
assert sum(not x['placements'] for x in before)==7,before
assert all(x['default_valid'] for x in before)
result=apply_bomb_launch_v30(f)
assert len(result['added_ids'])==21 and len(result['changed_existing_ids'])==7
assert not apply_bomb_launch_v30(f)['added_ids']
# Prove the real Unity serialization keeps all children and marker components.
g=UnityPy.load(f.save()).file
assert all(x['default_valid'] and len(x['placements'])==1 for x in bomb_placement_audit_v30(g))
print(json.dumps(dict(passed=True,regression='V29 has seven absent native human placement markers; V30 serializes exactly one per Bomb area.',repair=result),indent=2))
