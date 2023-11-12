#include "update_flag_wake_up.h"
#include <string.h> // for using memcpy (library function)

int update_flag_wake_up(bool* flag_tab, int* index_tab, int current_flag, int threshold){
    /*
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
    */

    bool new_flag_tab[3];
    memcpy(new_flag_tab, flag_tab, 3 * sizeof(bool)); // int is a POD

    // if a peak is detected
    index_tab[current_flag] = 0;
    flag_tab[current_flag] = true;

    for (int i_tone = 0; i_tone < 3; i_tone++) {

        // update counter for each detected tone
        if (flag_tab[i_tone] == true){
            index_tab[i_tone]++;
        }

        // if the last peak was threshold samples ago
        if (index_tab[i_tone] > threshold){
            flag_tab[i_tone] = false;
            index_tab[i_tone] = -1;
        }
    }

    // one flag has changed
    int event = -1;
    for (int i_tone = 0; i_tone < 3; i_tone++) {
        if (new_flag_tab[i_tone] != flag_tab[i_tone]){
            event = i_tone;
            break;
        }
    }

    return event;
}