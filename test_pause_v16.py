"""Execute the original pause/resume and velocity coroutine through real frames.

Unity APIs are deterministic stubs; the x64 coroutine, reciprocal, sample ring,
pause/resume controller and final averaging execute from GameAssembly.dll.
This catches NaN stored during pause and surviving Resume, not just a clock stub.
"""
from pathlib import Path
import sys, struct, json, math

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *
from fix_pause_v16 import patch_pause_tracking, TRACKING_TIME_CALLS, TRACKING_DELTA

H, S, STOP = 0x300000000, 0x400000000, 0x3000ff000


class PausedTracking:
    def __init__(self, image, base):
        self.pe = pefile.PE(data=image, fast_load=True)
        self.base = base
        self.u = Uc(UC_ARCH_X86, UC_MODE_64)
        self.u.mem_map(base, (self.pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
        self.u.mem_write(base, self.pe.get_memory_mapped_image())
        # Metadata access is mocked as an initialized class with no cctor work.
        self.u.mem_map(0, 0x1000)
        self.u.mem_map(H, 0x100000)
        self.u.mem_map(S, 0x100000)
        self.next = H + 0x1000
        self.estimator, self.routine, self.tracked = self.alloc(), self.alloc(), self.alloc()
        self.linear, self.angular = self.alloc(), self.alloc()
        for arr, n in ((self.linear, 5), (self.angular, 11)):
            self.ptr(arr + 0x18, n)
        self.ptr(self.estimator + 0x38, self.linear)
        self.ptr(self.estimator + 0x40, self.angular)
        self.ptr(self.routine + 0x20, self.estimator)
        self.page, self.shower, self.visuals, self.canvas = [self.alloc() for _ in range(4)]
        self.ptr(self.page + 0x40, self.shower)
        self.ptr(self.shower + 0x18, self.visuals)
        self.ptr(self.shower + 0x20, self.canvas)
        self.ptr(self.visuals + 0x18, 0)
        self.position = (0., 1.5, -5.)
        self.real_dt, self.scale = 1. / 90., 1.
        self.menu_visible = False
        self.clock_calls = []
        self.u.hook_add(UC_HOOK_CODE, self.hook)

    def alloc(self, n=0x200):
        v = self.next
        self.next += (n + 15) & ~15
        return v

    def ptr(self, addr, value):
        self.u.mem_write(addr, struct.pack('<Q', value))

    def integer(self, addr, value):
        self.u.mem_write(addr, struct.pack('<i', value))

    def int_at(self, addr):
        return struct.unpack('<i', self.u.mem_read(addr, 4))[0]

    def vec(self, addr, value=None):
        if value is None:
            return struct.unpack('<fff', self.u.mem_read(addr, 12))
        self.u.mem_write(addr, struct.pack('<fff', *value))

    def quat(self, addr):
        self.u.mem_write(addr, struct.pack('<ffff', 0., 0., 0., 1.))

    def float_register(self, register):
        return struct.unpack('<f', struct.pack('<I', self.u.reg_read(register) & 0xffffffff))[0]

    def ret(self, value=None, scalar=None):
        if value is not None:
            self.u.reg_write(UC_X86_REG_RAX, value)
        if scalar is not None:
            self.u.reg_write(UC_X86_REG_XMM0, struct.unpack('<I', struct.pack('<f', scalar))[0])
        sp = self.u.reg_read(UC_X86_REG_RSP)
        self.u.reg_write(UC_X86_REG_RIP, struct.unpack('<Q', self.u.mem_read(sp, 8))[0])
        self.u.reg_write(UC_X86_REG_RSP, sp + 8)

    def hook(self, u, addr, size, user):
        r = addr - self.base
        a, b, c = [u.reg_read(reg) for reg in (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8)]
        if r in (0x1c21b0, 0x14b040, 0x1f4660):
            self.ret()
        elif r == 0x1c22e0:
            self.ret(self.alloc())
        elif r == 0x94b620:
            self.ret(self.tracked)
        elif r == 0xb74de0:
            self.vec(a, self.position)
            self.ret(a)
        elif r == 0xb74fd0:
            self.quat(a)
            self.ret(a)
        elif r in (0xa13810, 0xa14bb0):
            self.quat(a)
            self.ret(a)
        elif r in (0xb72960, 0xb72b10):
            self.clock_calls.append(r)
            self.ret(scalar=self.real_dt * (self.scale if r == 0xb72960 else 1.))
        elif r in (0xb7a090, 0xb79e30):
            left, right = self.vec(b), self.vec(c)
            sign = -1 if r == 0xb7a090 else 1
            self.vec(a, tuple(x + sign * y for x, y in zip(left, right)))
            self.ret(a)
        elif r == 0xb7a040:  # Multiply(float, Vector3), actual reciprocal is xmm1.
            scale = self.float_register(UC_X86_REG_XMM1)
            self.vec(a, tuple(x * scale for x in self.vec(c)))
            self.ret(a)
        elif r == 0xb7a000:  # Multiply(Vector3, float), averaging uses xmm2.
            scale = self.float_register(UC_X86_REG_XMM2)
            self.vec(a, tuple(x * scale for x in self.vec(b)))
            self.ret(a)
        elif r == 0xb79db0:
            self.vec(a, (0., 0., 0.))
            self.ret(a)
        elif r == 0x957250:
            self.ret(min(a, b))
        elif r == 0x956d70:
            self.ret(scalar=max(self.float_register(UC_X86_REG_XMM1),
                                min(self.float_register(UC_X86_REG_XMM2),
                                    self.float_register(UC_X86_REG_XMM0))))
        elif r == 0x1cc8d8:
            self.ret(scalar=math.acos(self.float_register(UC_X86_REG_XMM0)))
        elif r == 0xb79770:
            self.vec(a, (0., 0., 0.))
            self.ret(a)
        elif r == 0xb79d00:
            self.ret(scalar=0.)
        elif r == 0x314180:  # CanPause: the solo room permits simulation pause.
            self.ret(1)
        elif r == 0x947920:
            self.menu_visible = bool(b)
            self.ret()
        elif r == 0xb72bb0:
            self.scale = self.float_register(UC_X86_REG_XMM0)
            self.ret()
        elif r == 0x402600:
            self.ret(self.alloc())
        elif r in (0x1c2320, 0x1c2130, 0x1c22f0):
            raise AssertionError(('unexpected Unity exception', hex(r)))

    def call(self, rva, *args):
        sp = S + 0x80008
        self.ptr(sp, STOP)
        self.u.reg_write(UC_X86_REG_RSP, sp)
        for reg, arg in zip((UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9), list(args) + [0] * 4):
            self.u.reg_write(reg, arg)
        self.u.emu_start(self.base + rva, STOP, count=50000)
        assert self.u.reg_read(UC_X86_REG_RIP) == STOP, hex(rva)
        return self.u.reg_read(UC_X86_REG_RAX)

    def frame(self, dx=0.):
        self.position = (self.position[0] + dx, self.position[1], self.position[2])
        assert self.call(0x327b30, self.routine) & 1  # Original MoveNext yields.

    def samples(self):
        return [self.vec(self.linear + 0x20 + n * 12) for n in range(5)]

    def estimated_velocity(self):
        result = self.alloc()
        assert self.call(0x32d960, result, self.estimator) == result
        return self.vec(result)

    def hand_velocity(self):
        hand, result = self.alloc(), self.alloc()
        self.ptr(hand + 0x28, self.estimator)
        assert self.call(0x312ec0, result, hand) == result
        return self.vec(result)

    def acceleration(self):
        result = self.alloc()
        assert self.call(0x32d490, result, self.estimator) == result
        return self.vec(result)


def exercise(image, base):
    e = PausedTracking(image, base)
    e.frame()  # Initial coroutine setup captures the tracked pose.
    for _ in range(5):
        e.frame(.01)
    assert all(math.isfinite(v) for sample in e.samples() for v in sample)
    e.call(0x314a70, e.page)  # Actual ShowMenu -> timeScale=0.
    assert e.scale == 0. and e.menu_visible
    for _ in range(3):
        e.frame()  # Stationary hand is sufficient to reproduce 0 * infinity.
    paused_samples = e.samples()
    paused_acceleration = e.acceleration()
    e.call(0x3143c0, e.page)  # Actual Resume -> menu hidden, timeScale=1.
    assert e.scale == 1. and not e.menu_visible
    e.frame(.01)
    return e, paused_samples, paused_acceleration


def main():
    original = (R / 'backup/GameAssembly.dll').read_bytes()
    source = pefile.PE(data=original, fast_load=True)
    fixed, records = bytearray(original), []
    patch_pause_tracking(fixed, source, records)
    checks = []
    for base in (0x180000000, 0x190000000):
        old, paused, acceleration = exercise(original, base)
        assert any(not math.isfinite(v) for sample in paused for v in sample)
        assert any(not math.isfinite(v) for sample in old.samples() for v in sample)
        assert any(not math.isfinite(v) for v in old.estimated_velocity())
        assert any(not math.isfinite(v) for v in old.hand_velocity())
        assert any(not math.isfinite(v) for v in acceleration)
        new, paused, acceleration = exercise(bytes(fixed), base)
        assert all(math.isfinite(v) for sample in paused for v in sample)
        assert all(math.isfinite(v) for sample in new.samples() for v in sample)
        assert all(math.isfinite(v) for v in new.estimated_velocity())
        assert all(math.isfinite(v) for v in new.hand_velocity())
        assert all(math.isfinite(v) for v in acceleration)
        assert set(new.clock_calls) == {TRACKING_DELTA}
        shipped, paused, acceleration = exercise((R / 'working/GameAssembly.dll').read_bytes(), base)
        assert all(math.isfinite(v) for sample in paused for v in sample)
        assert all(math.isfinite(v) for v in shipped.hand_velocity())
        assert all(math.isfinite(v) for v in acceleration)
        assert set(shipped.clock_calls) == {TRACKING_DELTA}
        checks.append(hex(base))
    report = {'passed': True, 'ASLR_bases': checks,
              'before': 'Stationary hand writes NaN velocity during pause; samples survive Resume.',
              'after': 'Tracking remains finite through actual ShowMenu, paused frames and Resume.',
              'verified_consumers': ['Original GetLinearVelocityEstimate', 'Original Hand.GetVelocity',
                                     'Original GetAccelerationEstimate while paused'],
              'calls_changed': [dict(name=name, rva=hex(site)) for name, site in TRACKING_TIME_CALLS],
              'shipped_dll_also_exercised': True,
              'scope': 'Actual original x64 coroutine and pause controller with Unity API stubs; does not replace headset testing.'}
    (R / 'analysis/v16-pause-regression.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
