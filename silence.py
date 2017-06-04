# original - https://raw.githubusercontent.com/jiaaro/pydub/master/pydub/silence.py
import numpy as np

def rms(signal):
    return np.sqrt(np.mean(np.abs(signal)**2))

def db_to_float(db):
    return 10 ** (float(db)/20)

def detect_silence(audio_segment, min_silence_len=1000, silence_thresh=-16):
    seg_len = len(audio_segment)

    # you can't have a silent portion of a sound that is longer than the sound
    if seg_len < min_silence_len:
        return []

    # convert silence threshold to a float value (so we can compare it to rms)
    silence_thresh = db_to_float(silence_thresh) * np.max(np.abs(audio_segment))

    # find silence and add start and end indicies to the to_cut list
    silence_starts = []

    # check every (1 sec by default) chunk of sound for silence
    slice_starts = int(seg_len / min_silence_len)

    for i in range(0, seg_len, min_silence_len):
        audio_slice = audio_segment[i:i+min_silence_len]
        if rms(audio_slice) < silence_thresh:
            silence_starts.append(i)

    # short circuit when there is no silence
    if not silence_starts:
        return []

    # combine the silence we detected into ranges (start ms - end ms)
    silent_ranges = []

    prev_i = silence_starts.pop(0)
    current_range_start = prev_i

    for silence_start_i in silence_starts:
        continuous = (silence_start_i == prev_i + 1)

        # sometimes two small blips are enough for one particular slice to be
        # non-silent, despite the silence all running together. Just combine
        # the two overlapping silent ranges.
        silence_has_gap = silence_start_i > (prev_i + min_silence_len)

        if not continuous and silence_has_gap:
            silent_ranges.append([current_range_start,
                                  prev_i + min_silence_len])
            current_range_start = silence_start_i
        prev_i = silence_start_i

    silent_ranges.append([current_range_start,
                          prev_i + min_silence_len])

    return silent_ranges


def detect_nonsilent(audio_segment, min_silence_len=1000, silence_thresh=-16):
    silent_ranges = detect_silence(audio_segment, min_silence_len, silence_thresh)
    len_seg = len(audio_segment)

    # if there is no silence, the whole thing is nonsilent
    if not silent_ranges:
        return [[0, len_seg]]

    # short circuit when the whole audio segment is silent
    if silent_ranges[0][0] == 0 and silent_ranges[0][1] == len_seg:
        return []

    prev_end_i = 0
    nonsilent_ranges = []
    for start_i, end_i in silent_ranges:
        nonsilent_ranges.append([prev_end_i, start_i])
        prev_end_i = end_i

    if end_i != len_seg:
        nonsilent_ranges.append([prev_end_i, len_seg])

    if nonsilent_ranges[0] == [0, 0]:
        nonsilent_ranges.pop(0)

    return nonsilent_ranges



def split_on_silence(audio_segment, rate, min_silence=1000, silence_thresh=-16, keep_silence=100):
    """
    audio_segment - np.array of audio

    rate - the sample rate of the audio

    min_silence - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms

    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS

    keep_silence - (in ms) amount of silence to leave at the beginning
        and end of the chunks. Keeps the sound from sounding like it is
        abruptly cut off. (default: 100ms)
    """

    min_silence_len = int(rate * min_silence/1000)
    keep_silence_len = int(rate * keep_silence/1000)
    not_silence_ranges = detect_nonsilent(audio_segment, min_silence_len, silence_thresh)

    chunks = []
    for start_i, end_i in not_silence_ranges:
        start_i = max(0, start_i - keep_silence_len)
        end_i += keep_silence_len

        chunks.append(audio_segment[start_i:end_i])

    return chunks
