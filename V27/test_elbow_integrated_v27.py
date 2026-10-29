"""Read-only verification of the root-built full DLL against immutable v26."""
from test_elbow_solver_v27 import *
import hashlib
native=R/'working/GameAssembly.dll';helper=R/'elbow_v27.c'
manifest=json.loads((R/'analysis/native-patch-manifest.json').read_text())
patch=next(x for x in manifest['patches'] if x['name']=='elbow_bend_v27')
assert patch['rva']==0xeeabe0 and patch['length']==7
checks=unchanged_right=changed_left=unchanged_left=0;rows=[]
def axis_q(axis,angle):return np.r_[np.array(axis)*math.sin(angle*math.pi/360),math.cos(angle*math.pi/360)]
wrists={f'yaw_{angle}':axis_q([0,1,0],angle) for angle in [-90,0,90]}
wrists.update(palms_up=axis_q([1,0,0],90),setting=qm(axis_q([0,1,0],-45),axis_q([1,0,0],90)),thumbs_up=qm(axis_q([0,1,0],-45),axis_q([0,0,1],90)),high_five=axis_q([1,0,0],-90))
for base in [0x180000000,0x190000000]:
 old,new=Solver(base),Solver(base,image=native)
 for left in [True,False]:
  for pose,target in [('standing',[.22,1.05,.16]),('raised',[.22,1.95,.16]),('crossbody',[-.18,1.4,.3]),('straight',[.16,1.46,.56])]:
   for wrist_name,wrist in wrists.items():
    target=np.array(target);target[0]=(-abs(target[0]) if left else abs(target[0])) if pose!='crossbody' else (.18 if left else -.18)
    a,b=old.update(left,target,wrist),new.update(left,target,wrist)
    assert a['wrist']==b['wrist'] and np.allclose(b['wrist'],target,atol=1e-6)
    assert np.array_equal(old.rot[old.q(old.arm+0x28)],new.rot[new.q(new.arm+0x28)])
    if not left:assert a==b;unchanged_right+=1
    else:
     if a==b:unchanged_left+=1
     else:changed_left+=1
     shoulder=np.array(b['shoulder']);direction=target-shoulder;mid=(target+shoulder)/2
     pole=np.array([-1.,0,0])-direction*np.dot([-1.,0,0],direction)/np.dot(direction,direction)
     assert np.dot(np.array(b['elbow'])-mid,pole)>-2e-7
    if np.linalg.norm(target-np.array(b['shoulder']))<.5999:
     assert abs(np.linalg.norm(np.array(b['elbow'])-b['shoulder'])-.3)<2e-6
     assert abs(np.linalg.norm(np.array(b['elbow'])-target)-.3)<2e-6
    for segment in ['upper','lower']:
     assert np.allclose(b[segment],(np.array(b['shoulder' if segment=='upper' else 'wrist'])+b['elbow'])/2,atol=2e-7)
    assert np.isfinite(list(b.values())).all();checks+=1
    if base==0x180000000:rows.append(dict(side='L' if left else 'R',pose=pose,wrist_variant=wrist_name,before=a,after=b))
report=dict(passed=True,cases=checks,ASLR_bases=2,right_unchanged=unchanged_right,left_corrected=changed_left,left_unchanged=unchanged_left,
 wrist_variants=list(wrists),
 helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),hook=patch,
 tracked_wrist_position_and_rotation_identical=True,segment_lengths_and_collider_alignment=True,samples=rows,
 scope='Actual full patched DLL and immutable v26 native two-bone IK in CPU emulation with Unity APIs stubbed. No live VR/Quest/two-PC claim.')
(R/'analysis/elbow-v27-integrated-results.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
