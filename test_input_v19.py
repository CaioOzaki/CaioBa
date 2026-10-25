"""Execute production v19 UI helpers and the original generic interface invoker.

Only Unity/OVR/Audio APIs and physical controller responses are mocked. Native
interface dispatch actually resolves and tail-calls bool/float vtable entries,
catching mismatched float ABI and verifying per-hand hysteresis.
"""
from pathlib import Path
import argparse, hashlib, json, math, os, struct, subprocess, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / 'tools/python'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

H, S, STOP, DELTA = 0x300000000, 0x400000000, 0x3000ff000, 0x194f000
# Zig's Windows cache has a bounded object path; keep these basenames short.
source = R / 'tools/i19.c'
source.write_text((R / 'test_input_v19_harness.c').read_text().replace('#include "input_v19.c"', '#include "../input_v19.c"'), encoding='utf-8')
env = dict(os.environ)
env.update(ZIG_GLOBAL_CACHE_DIR=str(R / 'tools/zig-cache-v13'), ZIG_LOCAL_CACHE_DIR=str(R / 'tools/zig-cache-v13'))
subprocess.run([str(R / 'tools/zigfast/zig-x86_64-windows-0.14.1/zig.exe'), 'cc', '-target', 'x86_64-windows-msvc',
                '-shared', '-O2', '-ffreestanding', '-fno-stack-protector', '-nostdlib', '-DPATCH_DELTA=0x194f000',
                str(source), '-o', str(R / 'tools/i19.dll'), '-Wl,--entry=DllMain'], check=True, env=env, capture_output=True)
P = pefile.PE(str(R / 'tools/i19.dll'), fast_load=True)
P.parse_data_directories(directories=[0, 5])
EX = {x.name.decode(): x.address + DELTA for x in P.DIRECTORY_ENTRY_EXPORT.symbols}
ORIGINAL = pefile.PE(str(R / 'backup/GameAssembly.dll'), fast_load=True)


class InputEngine:
    def __init__(self, base):
        self.b, self.u = base, Uc(UC_ARCH_X86, UC_MODE_64)
        u = self.u
        u.mem_map(base, 0x1c00000)
        u.mem_write(base + DELTA, P.get_memory_mapped_image())
        # The actual IL2CPP InterfaceFuncInvoker0 implementation preserves XMM0.
        u.mem_write(base + 0xa2710, ORIGINAL.get_data(0xa2710, 0x80))
        slide = base + DELTA - P.OPTIONAL_HEADER.ImageBase
        for block in getattr(P, 'DIRECTORY_ENTRY_BASERELOC', []):
            for e in block.entries:
                if e.type == 10:
                    at = base + DELTA + e.rva
                    self.ptr(at, self.q(at) + slide)
        u.mem_map(H, 0x100000)
        u.mem_map(S, 0x100000)
        self.next = H + 0x1000
        self.roots, self.strings = {}, {}
        self.a, self.steam_a = False, False
        self.digital, self.analog = [False, False], [0., 0.]
        self.dead, self.inactive, self.locked = set(), set(), set()
        self.input, stat, klass = self.alloc(), self.alloc(), self.alloc()
        self.ptr(base + 0x1542b48, klass)
        self.ptr(klass + 0xb8, stat)
        self.ptr(stat, self.input)
        self.system_type, self.controller_type, self.vr = self.alloc(), self.alloc(), self.alloc()
        self.ptr(base + 0x1541dc0, self.system_type)
        self.ptr(base + 0x1541d98, self.controller_type)
        self.ptr(self.input + 0x40, self.vr)
        self.controllers = [self.alloc(), self.alloc()]
        for i, controller in enumerate(self.controllers):
            self.interface(controller, self.controller_type, {4: H + 0x81000, 5: H + 0x82000})
        self.interface(self.vr, self.system_type, {5: H + 0x80000, 6: H + 0x80010})
        # Make the right controller an OpenVR controller for the A fallback.
        self.ptr(base + 0x15412b0, self.q(self.controllers[1]))
        self.ptr(self.controllers[1] + 0x10, self.alloc())
        self.button = self.alloc()
        self.source_count, self.clip_count, self.played = 0, 0, 0
        self.audio_settings, self.samples = {}, None
        self.module, ui_stat, ui_class = self.alloc(), self.alloc(), self.alloc()
        self.ptr(base + 0x1542440, ui_class)
        self.ptr(ui_class + 0xb8, ui_stat)
        self.ptr(ui_stat + 8, self.module)
        self.go_buttons, self.go_transforms, self.parents, self.component_go = {}, {}, {}, {}
        u.hook_add(UC_HOOK_CODE, self.hook)

    def alloc(self, n=0x400):
        result = self.next
        self.next += (n + 15) & ~15
        return result

    def ptr(self, addr, value):
        self.u.mem_write(addr, struct.pack('<Q', value))

    def q(self, addr):
        return struct.unpack('<Q', self.u.mem_read(addr, 8))[0]

    def integer(self, addr, value):
        self.u.mem_write(addr, struct.pack('<i', value))

    def interface(self, obj, interface_type, methods):
        klass, offsets = self.alloc(), self.alloc()
        self.ptr(obj, klass)
        self.u.mem_write(klass + 0x126, struct.pack('<H', 1))
        self.ptr(klass + 0xb0, offsets)
        self.ptr(offsets, interface_type)
        self.integer(offsets + 8, 0)
        for index, function in methods.items():
            self.ptr(klass + (0x13 + index) * 16, function)

    def f(self, reg):
        return struct.unpack('<f', struct.pack('<I', self.u.reg_read(reg) & 0xffffffff))[0]

    def ret(self, value=None, scalar=None):
        if value is not None:
            self.u.reg_write(UC_X86_REG_RAX, value)
        if scalar is not None:
            self.u.reg_write(UC_X86_REG_XMM0, struct.unpack('<I', struct.pack('<f', scalar))[0])
        sp = self.u.reg_read(UC_X86_REG_RSP)
        self.u.reg_write(UC_X86_REG_RIP, self.q(sp))
        self.u.reg_write(UC_X86_REG_RSP, sp + 8)

    def hook(self, u, addr, size, user):
        r = addr - self.b
        a, b, c, d = [u.reg_read(reg) for reg in (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9)]
        if addr in (H + 0x80000, H + 0x80010):
            self.ret(self.controllers[int(addr == H + 0x80010)])
        elif addr == H + 0x81000:
            self.ret(self.digital[self.controllers.index(a)])
        elif addr == H + 0x82000:
            # Deliberately incompatible integer bits: only XMM0 is correct.
            self.ret(0xdeadbeef, self.analog[self.controllers.index(a)])
        elif r == 0x452d40:
            assert (a, b) == (1, 2)
            self.ret(self.a)
        elif r == 0x40d5a0:
            assert b == 7
            self.ret(self.steam_a)
        elif r == 0x14ac80:
            self.ret(self.roots[a])
        elif r == 0x14ac70:
            self.roots.pop(a)
            self.ret()
        elif r == 0x14ac90:
            handle = max(self.roots, default=0) + 1
            self.roots[handle] = a
            self.ret(handle)
        elif r == 0xa0bfb0:
            self.ret(a != 0 and a not in self.dead)
        elif r == 0x478bf0:
            self.ret(a not in self.inactive)
        elif r == 0x83c7f0:
            self.ret(a not in self.locked)
        elif r == 0x14b790:
            value = bytes(u.mem_read(a, 100)).split(b'\0')[0].decode()
            obj = self.alloc()
            self.strings[obj] = value
            self.ret(obj)
        elif r == 0x94b570:
            self.ret(self.component_go.get(a, a))
        elif r == 0x94f410:
            assert self.strings[b] == 'Button'
            self.ret(self.go_buttons.get(a, 0))
        elif r == 0x94fb00:
            self.ret(self.go_transforms.get(a, 0))
        elif r == 0xb739d0:
            self.ret(self.parents.get(a, 0))
        elif r in (0x14a920, 0x14a910, 0x14a530, 0x14a5a0, 0x14a710, 0x14b9c0, 0x14acb0):
            self.ret(H + 0xe0000)
        elif r == 0x94f240:
            assert a == self.input  # Persistent source, not an inactive page.
            self.source_count += 1
            self.ret(self.alloc())
        elif r in (0xebc590, 0xebc760):
            self.audio_settings[r] = self.f(UC_X86_REG_XMM1)
            self.ret()
        elif r in (0xebc370, 0xebc500, 0xebc460):
            self.audio_settings[r] = b
            self.ret()
        elif r == 0xeba090:
            assert (b, c, d) == (1764, 1, 22050)
            self.clip_count += 1
            self.ret(self.alloc())
        elif r == 0x14a4f0:
            assert b == 1764
            self.ret(self.alloc(0x20 + b * 4))
        elif r == 0xeba5f0:
            self.samples = struct.unpack('<1764f', u.mem_read(b + 0x20, 1764 * 4))
            self.ret(1)
        elif r == 0xebc2d0:
            self.ret()
        elif r == 0xebbe30:
            self.played += 1
            self.ret()

    def call(self, name, *args):
        sp = S + 0x80008
        self.ptr(sp, STOP)
        self.u.reg_write(UC_X86_REG_RSP, sp)
        for reg, value in zip((UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9), list(args) + [0] * 4):
            self.u.reg_write(reg, value)
        self.u.emu_start(self.b + EX[name], STOP, count=200000)
        assert self.u.reg_read(UC_X86_REG_RIP) == STOP, name
        return self.u.reg_read(UC_X86_REG_RAX)


def run():
    bases = []
    for base in (0x180000000, 0x190000000):
        e = InputEngine(base)
        assert not e.call('input_probe', 0)
        assert e.call('input_probe', 1)
        e.a = True
        assert e.call('input_probe', 0)
        e.a = False
        e.steam_a = True
        assert e.call('input_probe', 0)
        e.steam_a = False
        for side in (0, 1):
            e.digital[side] = True
            assert e.call('input_probe', 0)
            e.digital[side] = False
            assert not e.call('input_probe', 0)
            for value, expected in ((.59, 0), (.61, 1), (.45, 1), (.34, 0), (.45, 0), (.62, 1), (float('nan'), 0)):
                e.analog[side] = value
                assert e.call('input_probe', 0) == expected, (side, value)
            e.analog[side] = 0.
        e.analog[0] = .9
        assert e.call('input_probe', 0)
        e.ptr(e.input + 0x40, 0)
        assert not e.call('input_probe', 0)
        e.analog[0] = .45
        e.ptr(e.input + 0x40, e.vr)
        assert not e.call('input_probe', 0)  # Disconnect clears analog latch.
        assert not e.call('valid_probe', 0)
        assert e.call('valid_probe', e.button)
        e.locked.add(e.button)
        assert not e.call('valid_probe', e.button)
        e.call('click_probe', e.button)
        assert e.played == e.clip_count == e.source_count == 0
        e.locked.clear()
        e.inactive.add(e.button)
        e.call('click_probe', e.button)
        assert e.played == 0
        e.inactive.clear()
        e.call('click_probe', e.button)
        e.call('click_probe', e.alloc())
        assert e.played == 2 and e.clip_count == e.source_count == 1
        assert e.audio_settings[0xebc590] == 0.
        assert abs(e.audio_settings[0xebc760] - .55) < 1e-6
        assert all(e.audio_settings[i] == 0 for i in (0xebc370, 0xebc500, 0xebc460))
        assert e.samples and all(math.isfinite(v) and abs(v) <= 1. for v in e.samples)
        assert max(abs(v) for v in e.samples) > .2
        assert not e.call('pointer_probe')
        child, parent, ct, pt = [e.alloc() for _ in range(4)]
        e.ptr(e.module + 0xf8, child)
        e.go_transforms[child] = ct
        e.parents[ct] = pt
        e.component_go[pt] = parent
        e.go_buttons[parent] = e.button
        assert e.call('pointer_probe')
        e.locked.add(e.button)
        assert e.call('pointer_probe')  # UI intent still suppresses lobby spawn.
        e.dead.add(child)
        assert not e.call('pointer_probe')
        bases.append(hex(base))
    report = {'passed': True, 'ASLR_bases': bases,
              'actual_generic_interface_invoker': True, 'float_return_in_XMM0': True,
              'checks': ['Original held input', 'OVR A and SteamVR A fallback', 'Left and right digital trigger',
                         'Independent analog 0.60/0.35 hysteresis', 'NaN analog and disconnect release',
                         'Inactive/locked buttons silent', 'One cached 2D source/clip for repeated clicks',
                         'Finite 80ms procedural click samples', 'Pointer detects parent Button without allocating each frame'],
              'VR_tested': False}
    (R / 'analysis/v19-input-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
