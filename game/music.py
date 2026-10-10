"""Original, gentle four-level chiptune; synthesized locally with no asset downloads."""
from array import array
from functools import lru_cache


BEAT_SECONDS = 0.75  # 80 BPM, eight bars; the loop ends on a quiet cadence.
CHORDS = ((48,52,55),(45,48,52),(41,45,48),(43,47,50),
          (48,52,55),(45,48,52),(41,45,48),(43,47,50))
MELODY = ((72,76,79,76),(72,69,76,None),(69,72,76,72),(71,74,79,None),
          (76,79,84,79),(76,72,69,None),(72,69,65,69),(71,67,72,None))


def frequency(note):
    return 440 * 2 ** ((note-69)/12)


def four_level_wave(phase):
    triangle = 1-4*abs((phase % 1)-0.5)
    return (-1,-1/3,1/3,1)[min(3,int((triangle+1)*2))]


def envelope(time, duration):
    # Short ramps keep quantized notes and the loop seam free of clicks.
    return min(1,time/0.02,max(0,(duration-time)/0.04)) * (1-time/duration)**0.6


@lru_cache(maxsize=4)
def soundtrack(rate, channels):
    """Return interleaved signed-16 PCM, cached across game launches in tests."""
    duration = BEAT_SECONDS*32
    samples = array('h')
    lead_pitch = [[frequency(n) if n else 0 for n in bar] for bar in MELODY]
    chord_pitch = [[frequency(n+12) for n in bar] for bar in CHORDS]
    bass_pitch = [frequency(bar[0]) for bar in CHORDS]
    smooth = 0.0
    for i in range(round(rate*duration)):
        time = i/rate
        bar = min(7,int(time/(BEAT_SECONDS*4)))
        beat = int(time/BEAT_SECONDS)%4
        note_time = time % BEAT_SECONDS
        eighth_time = time % (BEAT_SECONDS/2)
        arp_index = (0,1,2,1)[int(time/(BEAT_SECONDS/2))%4]
        lead = lead_pitch[bar][beat]
        value = (620*four_level_wave(time*lead)*envelope(note_time,BEAT_SECONDS) if lead else 0)
        value += 260*four_level_wave(time*chord_pitch[bar][arp_index])*envelope(eighth_time,BEAT_SECONDS/2)
        value += 200*four_level_wave(time*bass_pitch[bar])*envelope(time%(BEAT_SECONDS*4),BEAT_SECONDS*4)
        smooth += 0.16*(value-smooth)  # Soften the edges of the four-level instruments.
        samples.extend([round(smooth)]*channels)
    return samples.tobytes()
