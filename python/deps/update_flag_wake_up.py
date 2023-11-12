""" update wake-up flag status """
import numpy as np


def update_flag_wake_up(flag,
                        current_flag,
                        threshold):
    """
    The update_flag_wake_up function is used to update the flag and
    index values for each channel. The function takes in a flag, current_flag,
    and threshold value as inputs. The function then updates the flag_value array
    by setting all the values that are equal to True in current_flag to 0. It then
    sets all the values that are equal to True in flag_value (which will be any
    peaks detected) to 1 more than their previous value. If this new value is greater
    than a threshold, it sets both its index and flag_value
    back down to - 1 (so it can start over).

    :param flag: Keep track of the previous state of the flag
    :param current_flag: Indicate the index of the current flag
    :param threshold: Determine how many samples must pass before the flag is reset
    :return: The flag and the index of the changed flags

    """
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

    # One flag has changed
    event = np.arange(len(flag[0]))[flag_value != flag[0]].tolist()

    return [flag_value, index], event
