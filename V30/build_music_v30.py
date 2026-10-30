"""Create original CC0 instrumental lofi music for Cloudcourt v30.

All audio is synthesized from oscillators and deterministic noise in this file.
No downloaded music, samples, recordings, or game assets are used.
"""
from pathlib import Path
import hashlib, json, math, wave, sys
import numpy as np
sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parent / "tools" / "python")]

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets" / "audio-v30"
SAMPLE_RATE = 22050
TRACKS = [
    {"title": "Window Rain", "bpm": 80, "roots": [62, 59, 55, 57], "quality": "maj7", "seed": 301, "palette": 0},
    {"title": "Sunday Rally", "bpm": 76, "roots": [57, 53, 60, 55], "quality": "min9", "seed": 302, "palette": 1},
    {"title": "Neon Coastline", "bpm": 84, "roots": [63, 58, 60, 55], "quality": "maj9", "seed": 303, "palette": 2},
]


def _hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def _voice(freq, seconds, kind, velocity=1.0, seed=0):
    n = max(1, round(seconds * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(seed)
    if kind == "keys":
        # Soft electric-piano partials with a slow, subtle beating pair.
        y = (np.sin(2*np.pi*freq*t) + .25*np.sin(2*np.pi*freq*2.01*t + .1)
             + .075*np.sin(2*np.pi*freq*3*t + .35) + .025*np.sin(2*np.pi*freq*4.02*t))
        env = (1-np.exp(-t*42)) * np.exp(-t*1.18)
        env *= 1 + .035*np.sin(2*np.pi*4.7*t)
    elif kind == "pluck":
        y = (np.sin(2*np.pi*freq*t) + .19*np.sin(2*np.pi*freq*2*t)
             + .045*np.sin(2*np.pi*freq*3*t))
        env = (1-np.exp(-t*65)) * np.exp(-t*3.2)
    elif kind == "bass":
        y = np.sin(2*np.pi*freq*t) + .12*np.sin(2*np.pi*freq*2*t)
        env = (1-np.exp(-t*55)) * np.exp(-t*2.6)
    else:
        raise ValueError(kind)
    return y * env * velocity


def _drum(kind, seconds, rng):
    n = max(1, round(seconds*SAMPLE_RATE)); t = np.arange(n)/SAMPLE_RATE
    if kind == "kick":
        # Short pitch-dropping sine kick, deliberately soft.
        phase = 2*np.pi*(52*t + 36*(1-np.exp(-t*28))/28)
        return np.sin(phase)*np.exp(-t*18)*.62
    if kind == "snare":
        noise = rng.normal(0, 1, n)
        # Smooth the noise so the snare is warm, then blend a quiet body tone.
        noise = np.convolve(noise, np.ones(9)/9, mode="same")
        return noise*np.exp(-t*24)*.28 + np.sin(2*np.pi*185*t)*np.exp(-t*31)*.075
    noise = rng.normal(0, 1, n)
    # A little high-passed noise for a quiet brushed hat.
    smooth = np.convolve(noise, np.ones(5)/5, mode="same")
    return (noise-smooth)*np.exp(-t*72)*.14


def synthesize_track(index):
    spec = TRACKS[index]
    beat = 60.0/spec["bpm"]
    bars = 32
    duration = bars*4*beat
    out = np.zeros(round((duration + 1.0)*SAMPLE_RATE), dtype=np.float64)
    rng = np.random.default_rng(spec["seed"])
    melody_steps = [0, 2, 4, 7, 9, 11]
    palette = spec["palette"]

    def put(seconds, data, gain=1.0):
        start = round(seconds*SAMPLE_RATE)
        if start < 0 or start >= len(out): return
        count = min(len(data), len(out)-start)
        if count > 0: out[start:start+count] += data[:count]*gain

    for bar in range(bars):
        chord_ix = (bar//2) % 4
        root = spec["roots"][chord_ix]
        if spec["quality"] == "min9":
            intervals = [0, 3, 7, 10, 14]
        elif spec["quality"] == "maj9":
            intervals = [0, 4, 7, 11, 14]
        else:
            intervals = [0, 4, 7, 11]
        start = bar*4*beat
        # Wide, gentle chord voicing. The fifth is lifted an octave for space.
        for i, interval in enumerate(intervals):
            note = root + interval + (12 if i == 2 else 0)
            put(start + .012*i, _voice(_hz(note), beat*3.75, "keys", .105/(1+.11*i), spec["seed"]+bar*9+i), .72)
        # Rounded bass locks to kick and outlines changing harmony.
        put(start, _voice(_hz(root-24), beat*1.5, "bass", .36, spec["seed"]+bar), .85)
        put(start+2*beat, _voice(_hz(root-24), beat*1.25, "bass", .29, spec["seed"]+bar+200), .78)
        # Short original melodic motif, with alternate endings each 4-bar phrase.
        if bar % 4 != 3 or palette == 1:
            notes = [root+12+melody_steps[(bar*2+palette)%6],
                     root+12+melody_steps[(bar*2+2+palette)%6],
                     root+12+melody_steps[(bar*2+4+(bar//4)%2)%6]]
            offsets = [0.5, 1.75, 3.0] if (bar+palette)%2 == 0 else [1.0, 2.25, 3.5]
            for j, (note, offset) in enumerate(zip(notes, offsets)):
                dur = beat*(.72 if j < 2 else .48)
                put(start+offset*beat, _voice(_hz(note), dur, "pluck", .21, spec["seed"]+bar*17+j), .75)
        # Half-time kick/snare with quiet swung brushed hats.
        for b in range(4):
            at = start+b*beat
            if b in (0, 2): put(at, _drum("kick", .25, rng), .65 if palette != 2 else .56)
            if b in (1, 3): put(at+.012, _drum("snare", .21, rng), .68)
            put(at, _drum("hat", .07, rng), .48)
            if (b + bar + palette) % 2 == 1:
                put(at + beat*.56, _drum("hat", .055, rng), .24)

    # Subtle saturation, very short stereo-free room reflection, and edge fades.
    out = np.tanh(out*1.05)
    delay = round(.115*SAMPLE_RATE)
    out[delay:] += out[:-delay]*.085
    fade = round(1.0*SAMPLE_RATE)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    # Conservative gain with guaranteed headroom; remove any numerical DC offset.
    out -= np.mean(out)
    peak = float(np.max(np.abs(out)))
    if peak > 0: out *= .72/peak
    return out.astype(np.float32)


def _write_wav(path, signal):
    pcm = np.rint(np.clip(signal, -.999, .999)*32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SAMPLE_RATE)
        f.writeframes(pcm.tobytes())
    return pcm


def write_audio_art_v30():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    pieces=[]; rows=[]; cursor=0.0
    for i, spec in enumerate(TRACKS):
        signal=synthesize_track(i)
        path=ASSET_DIR/f"track-{i+1}.wav"
        pcm=_write_wav(path, signal)
        sec=len(pcm)/SAMPLE_RATE
        rows.append({"title":spec["title"], "bpm":spec["bpm"], "seconds":round(sec,3),
                     "start_seconds":round(cursor,3), "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                     "file":path.name})
        cursor += sec - (2.0 if i < len(TRACKS)-1 else 0.0)
        pieces.append(pcm.astype(np.float32)/32768.0)
    # Equal-power two-second overlaps keep the three different arrangements flowing.
    blend=round(2.0*SAMPLE_RATE)
    mix=pieces[0]
    for next_piece in pieces[1:]:
        theta=np.linspace(0, np.pi/2, blend, endpoint=True)
        overlap=mix[-blend:]*np.cos(theta) + next_piece[:blend]*np.sin(theta)
        mix=np.concatenate((mix[:-blend], overlap, next_piece[blend:]))
    # Let the full playlist wrap quietly on its final-to-first boundary.
    edge=round(1.25*SAMPLE_RATE)
    mix[:edge]*=np.linspace(0,1,edge)
    mix[-edge:]*=np.linspace(1,0,edge)
    mix -= np.mean(mix)
    peak=float(np.max(np.abs(mix)))
    if peak > .72: mix *= .72/peak
    playlist=_write_wav(ASSET_DIR/"cloudcourt-v30-original-playlist.wav", mix)
    rows.append({"title":"Full playlist", "seconds":round(len(playlist)/SAMPLE_RATE,3),
                 "sha256":hashlib.sha256((ASSET_DIR/"cloudcourt-v30-original-playlist.wav").read_bytes()).hexdigest(),
                 "file":"cloudcourt-v30-original-playlist.wav"})
    license_text=("Cloudcourt v30 original lofi music\n\n" + "\n".join(f"- {x['title']} ({x['bpm']} BPM)" for x in TRACKS) +
      "\n\nCompositions and recordings were generated locally by build_music_v30.py using synthesized oscillators and deterministic noise. No third-party music, samples, recordings, or melodies were used.\n\n" +
      "To the extent possible under law, the creator dedicates these compositions and recordings to the public domain under CC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/\n")
    (ASSET_DIR/"CC0-NOTICE.txt").write_text(license_text, encoding="utf-8")
    (ASSET_DIR/"playlist-metadata.json").write_text(json.dumps({"sample_rate":SAMPLE_RATE,"channels":1,"bit_depth":16,"tracks":rows,"generation":"algorithmic synthesis; no samples"},indent=2),encoding="utf-8")
    return playlist, rows


def apply_music_v30(file, old_bank, pcm):
    """Replace only v29's playlist AudioClip 171, preserving other audio bytes."""
    from build_audio_v18 import fsb as native_fsb
    bank=bytearray(); audit=[]
    for obj in sorted(file.objects.values(), key=lambda item:item.path_id):
        if obj.type.name != "AudioClip": continue
        data_tree=obj.read_typetree(); resource=data_tree["m_Resource"]
        old=dict(resource)
        if obj.path_id == 171:
            payload=native_fsb(pcm, "Cloudcourt_Original_Lofi_Playlist_v30")
            data_tree.update(m_Name="Cloudcourt v30 Original Lofi Playlist", m_Frequency=SAMPLE_RATE,
                m_Channels=1, m_BitsPerSample=16, m_Length=len(pcm)/SAMPLE_RATE,
                m_CompressionFormat=0, m_SubsoundIndex=0, m_LoadType=2,
                m_PreloadAudioData=False, m_LoadInBackground=True)
        else:
            begin=resource["m_Offset"]; end=begin+resource["m_Size"]
            payload=old_bank[begin:end]
            if len(payload) != resource["m_Size"]: raise ValueError(f"AudioClip {obj.path_id}: source payload is truncated")
        bank.extend(bytes((-len(bank))%32)); offset=len(bank); bank.extend(payload)
        data_tree["m_Resource"]={"m_Source":"sharedassets0.resource", "m_Offset":offset, "m_Size":len(payload)}
        obj.save_typetree(data_tree)
        audit.append({"id":obj.path_id,"changed_audio":obj.path_id==171,"old":old,"new":data_tree["m_Resource"]})
    if not any(item["changed_audio"] for item in audit):
        raise ValueError("Expected playlist AudioClip path_id 171 was not found")
    return bytes(bank), audit

if __name__ == "__main__":
    playlist, rows = write_audio_art_v30()
    print(json.dumps({"asset_dir":str(ASSET_DIR),"tracks":rows},indent=2))




