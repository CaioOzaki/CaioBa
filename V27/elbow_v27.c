/* PhysicalBody's own player IK uses the wrist orientation to choose its bend
 * plane. On the anatomical left arm this may select the torso-facing branch.
 * Reflect only that inward pole around the shoulder/wrist axis. The original
 * analytic two-bone solve still sets every arm transform and the tracked hand.
 * No persistent state, asset edits, extra Unity calls or network fields. */
TRAMP(V3*,elbow_bend_v27,(V3* result,void* body,V3* direction,void* arm,Q4* chest,void* method))

static V3 elbow_outward_v27(V3 normal,V3 direction,Q4 chest){
 if(!finitev(normal)||!finitev(direction)||!finitev((V3){chest.x,chest.y,chest.z})||
    !(chest.w==chest.w)||chest.w>2.f||chest.w< -2.f)return normal;
 float dd=dot(direction,direction),nn=dot(normal,normal);
 float qq=chest.x*chest.x+chest.y*chest.y+chest.z*chest.z+chest.w*chest.w;
 if(dd<.000001f||nn<.000000000001f||qq<.99f||qq>1.01f)return normal;
 /* Unity torso local -X is the measured left shoulder side, independent of
  * camera, court end, head yaw, local ownership or network pose playback. */
 V3 q={chest.x,chest.y,chest.z},axis={-1,0,0};
 V3 outward=add(axis,mul(cross(q,add(cross(q,axis),mul(axis,chest.w))),2.f));
 V3 pole=sub(outward,mul(direction,dot(outward,direction)/dd));
 float pp=dot(pole,pole);if(pp<.000001f)return normal;
 V3 bend=cross(direction,normal);float inward=dot(bend,pole);
 if(inward>=0)return normal; /* Already natural: bit-identical native result. */
 V3 delta=mul(pole,-2.f*inward/pp);
 V3 corrected=add(normal,mul(cross(delta,direction),1.f/dd));
 return finitev(corrected)?corrected:normal;
}

EXPORT V3* elbow_bend_v27_hook(V3* result,void* body,V3* direction,void* arm,Q4* chest,void* method){
 V3* solved=elbow_bend_v27_trampoline(result,body,direction,arm,chest,method);
 /* PhysicalBody.leftArm is a managed PhysicalArm (not a Unity object).
  * The right arm and all bot FinalIK rigs stay under their original solver. */
 if(solved&&body&&arm&&direction&&chest&&PTR(body,0x40)==arm)
  *solved=elbow_outward_v27(*solved,*direction,*chest);
 return solved;
}
