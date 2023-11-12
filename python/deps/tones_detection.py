""" Tones detection """
import numpy as np

def tones_detection(signal,
                    index_tones,
                    threshold):

    """
    The tones_detection function takes in a signal, the indices of
    the tones to be detected, and a threshold. It then calculates the z-score
    for each frequency bin in that signal. If any of those bins are above
    the threshold, it returns True.

    :param signal: Pass the signal to be analyzed to
    :param index_tones: Identify the frequency of each tone to
    :param threshold: Determine if the tone is present or not
    :return: A boolean array

    """
    spectrum = np.abs(np.fft.fft(signal - np.mean(signal)))
    mean = np.mean(spectrum)
    variance = np.var(spectrum)

    if variance == 0:
        variance = 1

    zscore = (spectrum - mean) / np.sqrt(variance)
    index_tones_wide = np.tile(index_tones, (3, 1)) + np.array([-1, 0, 1]).reshape(-1, 1)

    return (zscore[index_tones_wide] > threshold).any(axis=0)
