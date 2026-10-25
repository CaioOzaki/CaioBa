"""Ensure invalid hit/remote motion never reaches the engine or a Photon send."""
from pathlib import Path
import json, struct
R = Path(__file__).resolve().parent
scope = {'__file__': str(R / 'test_cloudcourt_v16.py')}
exec((R / 'test_cloudcourt_v16.py').read_text().split('\nchecks=[]')[0], scope)
CloudEngine = scope['CloudEngine']


class MotionEngine(CloudEngine):
    def __init__(self, base):
        super().__init__(base)
        self.applied = []

    def hook(self, u, addr, size, user):
        r = addr - self.b
        if r in (0x77e5c0, scope['ex']['client_motion_trampoline']):
            self.applied.append(r)
            self.ret()
        else:
            super().hook(u, addr, size, user)


checks = []
for base in (0x180000000, 0x190000000):
    for online in (False, True):
        e = MotionEngine(base)
        e.online = online
        e.flag('online_version_ready', int(online))
        for entry in ('motion_hook', 'client_motion_hook'):
            for field in ('position', 'velocity'):
                for invalid in (float('nan'), float('inf'), -float('inf')):
                    for axis in range(3):
                        position, velocity = [0., 2., -1.], [1., 3., 2.]
                        (position if field == 'position' else velocity)[axis] = invalid
                        e.u.mem_write(e.pv, struct.pack('<3f', *position))
                        e.u.mem_write(e.vv, struct.pack('<3f', *velocity))
                        before = len(e.applied)
                        e.call(entry, e.ball, e.pv, e.vv, 0, 0, 0, 0, 0)
                        assert len(e.applied) == before, (entry, field, axis, invalid)
            for values in ((0., 0., 0.), (2., 5., -3.)):
                e.vec(e.pv, (0., 2., -1.))
                e.vec(e.vv, values)
                before = len(e.applied)
                e.call(entry, e.ball, e.pv, e.vv, 0, 0, 0, 0, 0)
                assert len(e.applied) == before + 1, (entry, online)
            checks.append({'base': hex(base), 'online': online, 'entry': entry})
report = {'passed': True, 'invalid_frames_rejected': 144,
          'finite_and_stationary_frames_preserved': 16, 'checks': checks,
          'scope': 'Compiled native code with engine stubs; physical headset validation pending.'}
(R / 'analysis/v17-motion-finite-tests.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
