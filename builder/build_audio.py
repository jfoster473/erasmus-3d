# Renders the game's sound: a looping Barcelona street soundscape (and a muffled indoor
# version), three music loops built from the 2D game's tunes, and a set of footsteps.
#
#   python3 build_audio.py ../godot/audio
#
# Everything is synthesised; there are no recordings. Loops are seamless: each is rendered
# with a tail that is wrapped back onto its start.

import os, sys, wave
import numpy as np
import scipy.signal as sig

SR = 44100
OUT = next((a for a in sys.argv[1:] if not a.startswith('--')), 'audio')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)


# ------------------------------------------------------------------ helpers

def write(name, x, peak=0.85):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    x = x / max(1e-9, np.max(np.abs(x))) * peak
    with wave.open(os.path.join(OUT, name), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())
    print('wrote', name, round(len(x) / SR, 1), 's')


def filt(x, kind, f, order=2):
    nyq = SR / 2
    wn = [f[0] / nyq, f[1] / nyq] if kind == 'band' else f / nyq
    b, a = sig.butter(order, wn, kind)
    return sig.lfilter(b, a, x)


def noise(n):
    return rng.uniform(-1, 1, n)


def pink(n):
    spec = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[1:] /= np.sqrt(f[1:])
    spec[0] = 0
    x = np.fft.irfft(spec, n)
    return x / np.max(np.abs(x))


def smooth_random(n, period_s, depth):
    """A slow random wobble around 1.0."""
    pts = max(4, int(n / SR / period_s) + 3)
    ctrl = rng.uniform(-1, 1, pts)
    return 1 + depth * np.interp(np.arange(n), np.linspace(0, n, pts), ctrl)


def pan(mono, p):
    p = np.clip(p, -1, 1)
    return np.stack([mono * np.sqrt((1 - p) / 2), mono * np.sqrt((1 + p) / 2)], axis=1)


def add(buf, clip, t):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[:j - i]


def reverb(st, seconds, wet, darkness=3500):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(st)
    for c in range(2):
        ir = filt(noise(n), 'low', darkness) * np.exp(-t * 6.9 / seconds)
        ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        out[:, c] = sig.fftconvolve(st[:, c], ir)[:len(st)]
    out *= np.max(np.abs(st)) / max(1e-9, np.max(np.abs(out)))
    return st * (1 - wet) + out * wet


def wrap(st, loop_len):
    """Fold everything after loop_len back onto the start, for a seamless loop."""
    n = int(loop_len * SR)
    out = st[:n].copy()
    tail = st[n:]
    out[:len(tail)] += tail
    return out


# ------------------------------------------------------------------ the street

def car_pass(dur, peak_gain, direction):
    n = int(dur * SR)
    t = np.arange(n) / SR
    tc = dur / 2
    w = dur / 5
    env = 1 / (1 + ((t - tc) / w) ** 2)
    body = filt(noise(n), 'band', (140, 1300)) * 0.7
    # engine: a few harmonics of a low hum, with a small Doppler drop as it passes
    f0 = rng.uniform(32, 46)
    dop = 1 + 0.035 * np.tanh(-(t - tc) / (w * 0.6))
    ph = np.cumsum(f0 * dop / SR) * 2 * np.pi
    eng = sum(np.sin(ph * k) / k for k in range(1, 7))
    eng = filt(filt(eng, 'low', 380), 'high', 90) * 0.25
    tyre = filt(noise(n), 'band', (900, 3500)) * 0.12
    mono = (body + eng + tyre) * env * peak_gain
    p = direction * np.tanh((t - tc) / (w * 1.2))
    return pan(mono, p * 0.85)


def scooter_pass(dur, peak_gain, direction):
    """A two-stroke Vespa buzzing past."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tc = dur / 2
    w = dur / 6
    env = 1 / (1 + ((t - tc) / w) ** 2)
    f0 = rng.uniform(95, 120)
    dop = 1 + 0.06 * np.tanh(-(t - tc) / (w * 0.5))
    wob = 1 + 0.02 * np.sin(2 * np.pi * 3.1 * t)
    ph = np.cumsum(f0 * dop * wob / SR) * 2 * np.pi
    buzz = sum((np.sin(ph * k) / k ** 0.8) for k in range(1, 18))
    buzz *= 1 + 0.35 * np.sign(np.sin(ph / 2))       # uneven firing
    buzz = filt(filt(buzz, 'band', (150, 2600)), 'low', 1800)
    mono = buzz / np.max(np.abs(buzz)) * env * peak_gain
    p = direction * np.tanh((t - tc) / w)
    return pan(mono, p * 0.9)


def voice_phrase(f0, syllables):
    """Distant chatter: a voiced source through shifting vowel formants."""
    out = []
    for s in range(syllables):
        d = rng.uniform(0.11, 0.24)
        n = int(d * SR)
        t = np.arange(n) / SR
        pitch = f0 * (1 + rng.uniform(-0.12, 0.15)) * (1 + 0.08 * np.sin(np.pi * t / d))
        ph = np.cumsum(pitch / SR)
        src = (ph % 1.0) * 2 - 1 + noise(n) * 0.15
        f1, f2 = rng.uniform(320, 780), rng.uniform(950, 2100)
        v = filt(src, 'band', (f1 * 0.8, f1 * 1.25)) + 0.6 * filt(src, 'band', (f2 * 0.85, f2 * 1.18))
        out.append(v * np.hanning(n))
        if rng.random() < 0.15:
            out.append(np.zeros(int(rng.uniform(0.05, 0.15) * SR)))
    return np.concatenate(out)


def clink():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    fs = rng.uniform(2600, 3200) * np.array([1, 1.48, 2.06])
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * rng.uniform(14, 24)) for f in fs)
    return x * 0.3


def bell_strike(f0=196.0):
    n = int(7.5 * SR)
    t = np.arange(n) / SR
    ratios = [0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 2.662, 3.011, 4.166]
    decays = [5.5, 4.2, 3.4, 2.8, 2.2, 1.6, 1.4, 1.0, 0.6]
    amps = [0.6, 1.0, 0.7, 0.5, 0.45, 0.3, 0.25, 0.18, 0.1]
    x = sum(a * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * np.exp(-t / d) for r, d, a in zip(ratios, decays, amps))
    x[:200] *= np.linspace(0, 1, 200)
    return filt(x, 'low', 3200)


def pigeon_coo():
    parts = []
    for f, d in ((290, 0.22), (330, 0.42), (265, 0.3)):
        n = int(d * SR)
        t = np.arange(n) / SR
        fr = f * (1 - 0.12 * t / d)
        ph = np.cumsum(fr / SR) * 2 * np.pi
        x = np.sin(ph) * (0.7 + 0.3 * np.sin(2 * np.pi * 28 * t)) * np.hanning(n)
        parts += [x, np.zeros(int(0.06 * SR))]
    return filt(np.concatenate(parts), 'low', 900)


def chirp_phrase():
    out = np.zeros(int(1.2 * SR))
    base = rng.uniform(2800, 4400)
    t0 = 0.0
    for k in range(rng.integers(2, 6)):
        d = rng.uniform(0.04, 0.1)
        n = int(d * SR)
        t = np.arange(n) / SR
        f = np.linspace(base * rng.uniform(0.9, 1.15), base * rng.uniform(0.75, 1.35), n)
        x = np.sin(np.cumsum(f / SR) * 2 * np.pi) * np.sin(np.pi * t / d)
        add(out, x, t0)
        t0 += rng.uniform(0.07, 0.16)
    return out


def swift_scream():
    """Swifts screaming overhead on a summer evening: a buzzy, wavering high trill."""
    d = rng.uniform(0.5, 0.9)
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 6800 + 900 * np.sin(2 * np.pi * 38 * t) + rng.uniform(-400, 400)
    x = np.sin(np.cumsum(f / SR) * 2 * np.pi) * np.sin(np.pi * t / d) ** 0.7
    return x * (0.6 + 0.4 * np.sin(2 * np.pi * 19 * t))


def heel_step(dull=0.5):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    tap = filt(noise(n), 'band', (300, 1400 * dull + 500)) * np.exp(-t * 55)
    thud = np.sin(2 * np.pi * rng.uniform(110, 150) * t) * np.exp(-t * 50) * 0.35
    return tap * 0.7 + thud


def street(loop=96.0):
    n = int((loop + 9) * SR)
    st = np.zeros((n, 2))
    # the city beyond the block: a steady, slightly mid-heavy hum (steady, so it doesn't read as surf)
    for c in range(2):
        bed = filt(pink(n), 'band', (180, 1400)) * smooth_random(n, 9, 0.06)
        st[:, c] += bed * 0.03 + filt(noise(n), 'band', (700, 2600)) * 0.005
    # cars and scooters on the streets around
    t = rng.uniform(0, 4)
    while t < loop:
        if rng.random() < 0.28:
            add(st, scooter_pass(rng.uniform(4, 6), rng.uniform(0.07, 0.13), rng.choice([-1, 1])), t)
        else:
            add(st, car_pass(rng.uniform(4.5, 7), rng.uniform(0.06, 0.12), rng.choice([-1, 1])), t)
        t += rng.uniform(5, 11)
    # café terraces and people talking further along the street
    chat = np.zeros((n, 2))
    for v in range(9):
        f0 = rng.choice([115, 125, 140, 200, 215, 230])
        t = rng.uniform(0, 8)
        p = rng.uniform(-0.8, 0.8)
        while t < loop:
            ph = voice_phrase(f0, int(rng.integers(4, 11)))
            add(chat, pan(ph * rng.uniform(0.5, 1), p), t)
            t += len(ph) / SR + rng.uniform(0.8, 4.5)
    chat = np.stack([filt(chat[:, c], 'low', 2300) for c in range(2)], axis=1)
    st += chat / np.max(np.abs(chat)) * 0.05
    for k in range(14):
        add(st, pan(clink() * rng.uniform(0.015, 0.03), rng.uniform(-0.7, 0.7)), rng.uniform(0, loop))
    # other people's footsteps going by
    for k in range(7):
        t = rng.uniform(0, loop - 8)
        p0 = rng.uniform(-1, 1)
        pace = rng.uniform(0.5, 0.6)
        for s in range(int(rng.integers(8, 14))):
            add(st, pan(filt(heel_step(0.8), 'high', 300) * 0.03, p0 + s * 0.08 * np.sign(-p0)), t + s * pace)
    # a church bell somewhere in Gràcia
    for k in range(3):
        add(st, pan(bell_strike() * 0.05, -0.4), 31 + k * 2.6)
    # birds
    for k in range(int(loop / 3.2)):
        add(st, pan(chirp_phrase() * rng.uniform(0.015, 0.032), rng.uniform(-0.9, 0.9)), rng.uniform(0, loop))
    for k in range(5):
        add(st, pan(swift_scream() * 0.012, rng.uniform(-0.9, 0.9)), rng.uniform(0, loop))
    for k in range(4):
        add(st, pan(pigeon_coo() * 0.035, rng.uniform(-0.5, 0.5)), rng.uniform(0, loop - 2))
    st = reverb(st, 1.4, 0.22, 4000)
    st = np.stack([filt(st[:, c], 'high', 110) for c in range(2)], axis=1)   # no surf-like rumble
    return wrap(st, loop)


# ------------------------------------------------------------------ music (from the 2D game)

def note_hz(n):
    import re
    m = re.match(r'^([A-G])(b|#)?(\d)$', n)
    base = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[m.group(1)] + (1 if m.group(2) == '#' else -1 if m.group(2) == 'b' else 0)
    return 440 * 2 ** ((base + (int(m.group(3)) + 1) * 12 - 69) / 12)


PLUCKS = {}


def pluck(name, soft=False):
    """Karplus-Strong nylon string, computed a period at a time. soft: plucked with the thumb, mellower."""
    if (name, soft) in PLUCKS:
        return PLUCKS[(name, soft)]
    f = note_hz(name)
    N = max(2, int(round(SR / f)))
    L = int(SR * (2.2 if f < 150 else 1.6))
    y = np.zeros(L + N + 1)
    burst = filt(noise(N), 'low', 1100 if soft else 2500)
    y[:N] = burst
    decay = 0.9975 if f < 150 else 0.996
    i = N
    while i < L:
        j = min(L, i + N)
        k = np.arange(i, j)
        y[i:j] = decay * 0.5 * (y[k - N] + y[k - N - 1])
        i = j
    y = y[:L]
    y *= np.minimum(1, (L - np.arange(L)) / (0.3 * SR))
    PLUCKS[(name, soft)] = y
    return y


def parse_seq(s, mult=1):
    out, t = [], 0
    for tok in s.split():
        n, l = tok.split(':')
        ln = int(l) * mult
        if n != '-':
            out.append((t, n, ln))
        t += ln
    return out, t


MEL_OW = ' '.join(['F#5:3 E5:1 D5:2 A4:2 D5:4 -:4', 'B4:2 D5:2 G5:3 F#5:1 E5:4 -:4', 'C#5:2 E5:2 A5:4 G5:2 F#5:2 E5:4', 'F#5:6 -:2 D5:2 E5:2 F#5:4',
                   'B5:3 A5:1 F#5:2 D5:2 B4:4 -:4', 'D5:2 E5:2 G5:2 B5:2 A5:4 G5:4', 'G5:3 F#5:1 E5:4 C#5:3 E5:1 A5:4', 'F#5:2 E5:2 D5:8 -:4',
                   '-:2 B4:2 D5:2 F#5:2 B5:4 A5:2 F#5:2', 'A5:3 G5:1 F#5:2 C#5:2 F#5:8', 'G5:2 B5:2 D6:3 B5:1 A5:2 G5:2 D5:4', 'F#5:4 A5:4 F#5:2 E5:2 D5:4',
                   'E5:2 G5:2 B5:4 A5:2 G5:2 E5:4', 'C#5:2 E5:2 A5:4 G5:2 F#5:2 E5:4', 'D5:2 G5:2 B5:3 A5:1 G5:2 F#5:2 E5:4', 'E5:2 F#5:2 G5:2 A5:2 C#5:4 E5:2 -:2'])
CH_OW = 'D G A D Bm G Em|A D Bm F#m G D Em F#m G A'
MEL_IN = ' '.join(['D5:4 B4:2 G4:2 B4:4 D5:4', 'E5:4 G5:2 E5:2 B4:8', 'C5:2 E5:2 G5:4 F#5:2 E5:2 C5:4', 'D5:6 A4:2 F#4:4 A4:4',
                   'B4:2 D5:2 G5:4 F#5:2 G5:2 A5:4', 'F#5:4 D5:2 B4:2 D5:8', 'E5:2 G5:2 E5:2 C5:2 D5:2 F#5:2 A5:4', 'G5:8 -:8'])
CH_IN = 'G Em C D G Bm C|D G'
VOICE = {'D': ['D3', 'A3', 'D4', 'F#4'], 'G': ['G2', 'D3', 'G3', 'B3'], 'A': ['A2', 'E3', 'A3', 'C#4'], 'Bm': ['B2', 'F#3', 'B3', 'D4'],
         'Em': ['E2', 'B2', 'E3', 'G3'], 'F#m': ['F#2', 'C#3', 'F#3', 'A3'], 'C': ['C3', 'G3', 'C4', 'E4']}
ROOT = {'D': 'D2', 'G': 'G2', 'A': 'A2', 'Bm': 'B2', 'Em': 'E2', 'F#m': 'F#2', 'C': 'C2'}
FIFTH = {'D': 'A2', 'G': 'D3', 'A': 'E2', 'Bm': 'F#2', 'Em': 'B2', 'F#m': 'C#3', 'C': 'G2'}


def flute(name, dur):
    f = note_hz(name)
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.004 * np.minimum(1, t / 0.25) * np.sin(2 * np.pi * 5 * t)
    ph = np.cumsum(f * vib / SR) * 2 * np.pi
    x = np.sin(ph) + 0.12 * sig.sawtooth(2 * ph, 0.5)
    env = np.minimum(1, t / 0.06) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.06))
    breath = filt(noise(n), 'band', (f * 1.6, f * 2.6)) * 0.08 * np.exp(-t / 0.08)
    return (x * env * 0.75 + breath)


def bass(name, dur, v):
    f = note_hz(name)
    n = int((dur + 0.2) * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / max(0.2, dur)) * np.minimum(1, t / 0.01)
    p = pluck(name)
    return (x * 0.7 + np.pad(p, (0, max(0, n - len(p))))[:n] * 0.45) * v


def music(kind):
    soft = kind == 'passeig_soft'           # the indoor version: slower, thumb-plucked, further away
    bpm = 76 if kind == 'siesta' else 72 if soft else 88
    half = kind in ('passeig', 'passeig_soft')
    mult = 2 if half else 1
    step = 60 / bpm / 4
    bar = 16 * mult
    mel, length = parse_seq(MEL_IN if kind == 'siesta' else MEL_OW, mult)
    bars = (CH_IN if kind == 'siesta' else CH_OW).split()
    loop = length * step
    st = np.zeros((int((loop + 4) * SR), 2))
    dry = np.zeros_like(st)

    def put(clip, t, p=0.0, gain=1.0):
        add(dry, pan(clip * gain, p), t * step + rng.uniform(0, 0.006))

    for t, n, l in mel:
        if kind == 'rumba':
            put(flute(n, l * step * 0.95), t, 0.15, 0.32)
        else:
            put(pluck(n, soft), t, 0.15, 0.4 if soft else 0.55)
    for i, b in enumerate(bars):
        parts = b.split('|')
        seg = bar / len(parts)
        for j, ch in enumerate(parts):
            t0 = i * bar + j * seg
            if kind == 'rumba':
                s = 0
                while s < seg:
                    for o, way, v in ((0, 1, 1.0), (3, -1, 0.55), (6, 1, 0.8)):
                        if s + o < seg:
                            strings = VOICE[ch] if way > 0 else VOICE[ch][::-1]
                            for k, nn in enumerate(strings):
                                add(dry, pan(pluck(nn) * 0.3 * v, -0.2 + k * 0.1), (t0 + s + o) * step + k * 0.014)
                    chuck = filt(noise(int(0.05 * SR)), 'band', (1300, 2400)) * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.015)
                    put(chuck, t0 + s + 4, -0.1, 0.12)
                    for o, nn, d, v in ((0, ROOT[ch], 3, 1.0), (3, FIFTH[ch], 3, 0.7), (6, ROOT[ch], 2, 0.8)):
                        put(bass(nn, d * step, v), t0 + s + o, 0.0, 0.35)
                    lo = int(0.2 * SR)
                    tt = np.arange(lo) / SR
                    kick = np.sin(np.cumsum(np.geomspace(120, 60, lo) / SR) * 2 * np.pi) * np.exp(-tt / 0.06)
                    put(kick, t0 + s, 0.0, 0.2)
                    slap = filt(noise(int(0.09 * SR)), 'band', (650, 1300)) * np.exp(-np.arange(int(0.09 * SR)) / SR / 0.025)
                    put(slap, t0 + s + 4, 0.1, 0.18)
                    s += 8
            else:
                v = VOICE[ch]
                pat = [0, 2, 1, 3, 2, 1, 3, 2]
                stp = 4 if half else 2
                for k, s in enumerate(range(0, int(seg), stp)):
                    nn = ROOT[ch] if k == 0 else v[pat[k % 8]]
                    put(pluck(nn, soft), t0 + s, -0.25 + 0.15 * (k % 4), (0.3 if k == 0 else 0.16) if soft else (0.42 if k == 0 else 0.26))
                put(bass(ROOT[ch], (seg - 2) * step, 0.6), t0, 0.0, 0.18 if soft else 0.3)
    if kind == 'rumba':
        for t in range(0, length, 2):
            sh = filt(noise(int(0.05 * SR)), 'high', 6500) * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.012)
            put(sh, t, 0.35, 0.05 if t % 4 else 0.08)
    wet = reverb(dry, 2.6 if soft else 1.9, 0.42 if soft else 0.3, 3000 if soft else 3800)
    wet = np.stack([filt(filt(wet[:, c], 'low', 2400 if soft else 2800 if kind == 'siesta' else 4200), 'high', 90 if soft else 70) for c in range(2)], axis=1)
    return wrap(wet, loop)


# ------------------------------------------------------------------ the 2D game's sound effects (its sfx()), and its sea

NOTE_BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def note2d(n):
    """The 2D game's NOTE(): 'F#5' -> Hz."""
    base = NOTE_BASE[n[0]] + (1 if '#' in n else -1 if n[1] == 'b' else 0)
    return 440.0 * 2 ** ((base + (int(n[-1]) + 1) * 12 - 69) / 12)


def osc2d(kind, f, start, dur, vol, total):
    """The 2D game's osc(): a quick rise, a fall to 55% by min(0.12, dur * 0.4), then away by dur."""
    out = np.zeros(int(total * SR))
    n = int((dur + 0.02) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    w = {'sine': np.sin(ph), 'square': np.sign(np.sin(ph)) * 0.6,
         'triangle': 2 / np.pi * np.arcsin(np.sin(ph))}[kind]
    k1, k2 = 0.012, min(0.12, dur * 0.4)
    env = np.where(t < k1, vol * (t / k1),
                   np.where(t < k2, vol * (1 - 0.45 * (t - k1) / max(1e-6, k2 - k1)),
                            vol * 0.55 * np.exp(-6 * (t - k2) / max(1e-6, dur - k2))))
    i0 = int(start * SR)
    out[i0:i0 + n] += (w * env)[:len(out) - i0]
    return out


def seq2d(notes, kind='triangle', gap=0.07, vol=0.12, ln=0.12):
    total = len(notes) * gap + ln + 0.1
    return sum(osc2d(kind, note2d(nn), i * gap, ln, vol, total) for i, nn in enumerate(notes))


def shutter_click():
    """(round 41, the user: "make the camera sound more of a click") a camera's two quick clicks, the shutter opening
    and shutting: each a bright tick of filtered noise over a short wooden knock. Its own random numbers, so every
    other sound comes out as before (the old hiss's draws are still taken from the shared ones)."""
    noise(int(0.08 * SR))                              # (the shared numbers move on as they did)
    r = np.random.default_rng(4242)
    n = int(0.15 * SR)
    x = np.zeros(n)
    for at, amp, knock in ((0.0, 1.0, 230.0), (0.052, 0.75, 185.0)):
        i0 = int(at * SR)
        m = n - i0
        t = np.arange(m) / SR
        tick = filt(r.uniform(-1, 1, m), 'band', (1800, 9000)) * np.exp(-t / 0.0025)
        thock = np.sin(2 * np.pi * knock * t) * np.exp(-t / 0.009) * 0.45
        x[i0:] += amp * (tick + thock)
    return x


def noise_hit(kind, f, vol, dur):
    n = int((dur + 0.02) * SR)
    x = filt(noise(n), kind, f)
    return x * vol * np.exp(-np.arange(n) / SR / (dur / 6))


def sfx():
    """Every effect the 2D game plays, made the same way; written at the 2D game's relative loudness."""
    both = lambda a, b: np.concatenate([a, np.zeros(max(0, len(b) - len(a)))]) + np.concatenate([b, np.zeros(max(0, len(a) - len(b)))])
    fx = {
        'tick': osc2d('triangle', 880, 0, 0.04, 0.05, 0.1),
        'select': seq2d(['C6', 'F6'], 'triangle', 0.05, 0.08, 0.08),
        'back': seq2d(['F5', 'C5'], 'triangle', 0.05, 0.07, 0.08),
        'open': seq2d(['A5', 'C6'], 'triangle', 0.04, 0.06, 0.07),
        'pickup': seq2d(['C5', 'E5', 'G5', 'C6'], 'triangle', 0.055, 0.1, 0.12),
        'coin': seq2d(['B5', 'E6'], 'triangle', 0.07, 0.07, 0.18),
        'buy': seq2d(['G5', 'C6', 'E6'], 'triangle', 0.06, 0.1, 0.14),
        'door': both(osc2d('sine', 110, 0, 0.18, 0.2, 0.4), seq2d(['E5', 'A5'], 'triangle', 0.08, 0.05, 0.15)),
        'quest': seq2d(['F5', 'A5', 'C6'], 'triangle', 0.09, 0.1, 0.2),
        'fanfare': seq2d(['D5', 'F#5', 'A5', 'D6'], 'triangle', 0.1, 0.09, 0.3),
        'nope': seq2d(['E4', 'C4'], 'triangle', 0.09, 0.1, 0.14),
        'bump': osc2d('sine', 90, 0, 0.08, 0.12, 0.15),
        'page': noise_hit('band', (1700, 2800), 0.1, 0.12),
        'bell': seq2d(['E6', 'E6'], 'sine', 0.14, 0.1, 0.25),
        'ring': seq2d(['A5', 'A5', 'A5', 'A5'], 'sine', 0.08, 0.06, 0.07),
        'eat': seq2d(['G4', 'C5'], 'triangle', 0.08, 0.08, 0.1),
        'bin': both(osc2d('sine', 140, 0, 0.2, 0.16, 0.35), seq2d(['C5'], 'triangle', 0.0, 0.05, 0.1)),
        'drop': seq2d(['G5', 'D5'], 'triangle', 0.05, 0.07, 0.08),
        'cloth': noise_hit('low', 1200, 0.12, 0.25),
        'shutter': shutter_click(),
        'bark': seq2d(['A4', 'E4'], 'square', 0.12, 0.05, 0.07),
    }
    for k, x in fx.items():
        write('sfx_%s.wav' % k, x, min(0.9, float(np.max(np.abs(x))) * 3.5))


def sea(loop=3 * 2 * np.pi / 0.7):
    """Waves on the beach: low noise swelling and falling (the 2D game's waveGain and waveLP)."""
    n = int(loop * SR)
    t = np.arange(n) / SR
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * t / (2 * np.pi / 0.7))
    lo = filt(noise(n), 'low', 380)
    hi = filt(noise(n), 'low', 900)
    x = lo * swell + hi * np.clip(swell - 0.6, 0, 1) * 1.4
    st = np.stack([x, np.roll(x, int(0.013 * SR))], axis=1)
    return wrap(np.concatenate([st, st[:int(2 * SR)]]), n)


if __name__ == '__main__' and '--sfx' in sys.argv:
    sfx()
    write('sea.wav', sea(), 0.8)
    sys.exit(0)

if __name__ == '__main__':
    s = street()
    write('street.wav', s, 0.8)
    inside = np.stack([filt(s[:, c], 'low', 450, 3) for c in range(2)], axis=1)
    write('street_indoors.wav', inside, 0.8)
    for k in ('rumba', 'passeig_soft'):          # Rumba outdoors, a soft Passeig at home
        write('music_%s.wav' % k, music(k), 0.8 if k == 'rumba' else 0.7)
    for i in range(6):
        write('step_pavement_%d.wav' % i, filt(heel_step(0.55) * rng.uniform(0.85, 1.0), 'low', 2200), 0.9)
    for i in range(6):
        write('step_tiles_%d.wav' % i, filt(heel_step(0.4) * rng.uniform(0.85, 1.0), 'low', 1600), 0.9)
