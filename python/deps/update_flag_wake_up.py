import numpy as np


def update_flag_wake_up(flag,
                        current_flag,
                        threshold):
    flag_value = np.copy(flag[0])
    index = flag[1]

    # if a peak is detected
    index[current_flag] = 0
    flag_value[current_flag] = True
    index[flag_value] += 1

    # if the last peak was threshold samples ago
    flag_time_threshold = index > threshold
    flag_value[flag_time_threshold] = False
    index[flag_time_threshold] = -1

    # One flag was changed
    index = np.arange(len(flag[0]))
    event = index[flag_value != flag[0]].tolist()

    return [flag_value, index], event
