"""Use tracking time for tracked head/arm/hand velocity during a solo pause.

In the compatible original build, VelocityEstimator's end-of-frame coroutine
keeps running when the menu sets timeScale=0.  It computes 1 / deltaTime and
multiplies a position delta by that infinity, writing NaN samples even for a
stationary controller.  Both velocity and acceleration must use real frame time
because VR tracking continues while game simulation is paused.

This changes two verified call sites, never Unity's global clock or bot timing.
"""
import struct

SCALED_DELTA = 0xb72960
TRACKING_DELTA = 0xb72b10
TRACKING_TIME_CALLS = (
    ('tracked_velocity_real_time', 0x327bea),
    ('tracked_acceleration_real_time', 0x32d666),
)


def patch_pause_tracking(result, original_pe, patches):
    for name, site in TRACKING_TIME_CALLS:
        before = b'\xe8' + struct.pack('<i', SCALED_DELTA - site - 5)
        after = b'\xe8' + struct.pack('<i', TRACKING_DELTA - site - 5)
        offset = original_pe.get_offset_from_rva(site)
        assert original_pe.get_data(site, 5) == before, (name, 'incompatible game')
        assert result[offset:offset + 5] in (before, after), (name, 'overlapping edit')
        result[offset:offset + 5] = after
        patches.append(dict(name=name, rva=site, length=5,
                            original=before.hex(), hook=TRACKING_DELTA, kind='call'))

