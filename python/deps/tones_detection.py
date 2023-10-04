import numpy as np


def tones_detection(x,
                    index_tones,
                    threshold):
    X = np.abs(np.fft.fft(x - np.mean(x)))
    mean = np.mean(X)
    variance = np.var(X)

    if variance == 0:
        variance = 1

    zscore = (X - mean) / np.sqrt(variance)
    index_tones_wide = np.tile(index_tones, (3, 1)) + np.array([-1, 0, 1]).reshape(-1, 1)

    return (zscore[index_tones_wide] > threshold).any(axis=0)
