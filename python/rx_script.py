# %% Packages
import numpy as np 

from scipy.io import wavfile
from numpy.fft import fft
from Decoder import Decoder
from time import time 

# %% Functions
def tones_detection(x, 
                    index_tones,
                    threshold):
    
    X = np.abs(fft(x - np.mean(x)))
    mean = np.mean(X)
    variance = np.var(X)
    
    if variance == 0 :
        variance = 1
        
    zscore = (X - mean) / np.sqrt(variance)
    index_tones_wide = np.tile(index_tones, (3, 1)) + np.array([-1, 0, 1]).reshape(-1, 1)
    
    return (zscore[index_tones_wide] > threshold).any(axis=0)
    
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
    event = flag_value.sum() > flag[0].sum()

    return ([flag_value, index], event)

# %% Get audio data
sampling_freq, iq_data = wavfile.read('test_rx_2023-10-03_004340409.wav')
s_rx = iq_data
# s_rx = iq_data[:, 0] + 1j * iq_data[:, 1]

# %% Parameters
pulse_width = 0.8       # pulse width, 1 x 1, [s]
pulse_interval = 1      # pulse interval repetition, 1 x 1, [s]
t_recording = 3e1       # recording time, 1 x 1, [s]
carrier_freq = 10_000   # carrier frequency, 1 x 1, [Hz]
freq_shift = 400        # frequency shift for bi-tone mode, 1 x 1, [Hz]
threshold_wake_up = 4  
threshold_release = 4
n_sample_buffer = 512
n_step = 50
threshold_time = (2 * pulse_interval + pulse_width) * sampling_freq + 2 * n_sample_buffer

# %% Deducted parameters 
sampling_prd = 1 / sampling_freq    # sampling period, 1 x 1, [s]
sub_sampling_factor = int(pulse_interval / sampling_prd)
                                    # sub sampling period (nyquist period 
                                    # to symbol period), 1 x 1, [ ]
                                    
                                    
# %% Generate wake up tones and release tones
n_sample_buffer = 128
wake_up_tone = np.array([-2, 0, 2]) * sampling_freq / n_sample_buffer + carrier_freq
wake_up_tone = np.array([9_250, 10_000, 10_750])
n_symb_preamb = len(wake_up_tone)



true_message = "1111100110101"
release_tones = 4 * sampling_freq / n_sample_buffer * np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1]) + carrier_freq
n_pulse = len(release_tones)       # number of pulse, 1 x 1, [ ]
release_tones[release_tones<0] = sampling_freq + release_tones[release_tones<0]
index_release_tones = (np.round(np.unique(release_tones) * n_sample_buffer
                                / sampling_freq)).astype(int)
n_sample_buffer = 128
wake_up_tone[wake_up_tone<0] = sampling_freq + wake_up_tone[wake_up_tone<0]
index_wake_up_tones = (np.round(wake_up_tone * n_sample_buffer
                                / sampling_freq)).astype(int)

# %% Real time processing
n_sample = np.round((n_symb_preamb + n_pulse) * pulse_interval * sampling_freq)
decoded_sequence = np.zeros(len(s_rx) // n_step)
processing_buffer = np.zeros(n_sample_buffer, dtype="complex128")
flag_wake_up = [np.zeros(n_symb_preamb, dtype=bool), 
                -np.ones(n_symb_preamb)]

decoded_message = ""
flag_release = False
flag_end = False
decoder = Decoder(n_pulse, 
                  pulse_width,
                  pulse_interval,
                  n_sample_buffer,
                  n_step,
                  sampling_freq)

t_begin = time()
for i in range(0, len(s_rx) // n_step):
    # %%% Update samples
    processing_buffer[:-n_step] = processing_buffer[n_step:]
    processing_buffer[-n_step:] = s_rx[i * n_step: (i + 1) * n_step]
    current_flag_release = np.array([False, False])
    
    # %%% Check wake up tones
    if flag_wake_up[0].all() == False:
        if (i * n_step) % (2 * sampling_freq) == 0:
            print("==================================")
            print("|| Looking for wake up tones... ||")
            print("==================================\n")
        current_flag_wake_up =  tones_detection(processing_buffer,
                                                index_wake_up_tones,
                                                threshold_wake_up)
        flag_wake_up, event = update_flag_wake_up(flag_wake_up,
                                                  current_flag_wake_up,
                                                  threshold_time)
        if event:
            print("================================")
            print(f"|| Wake up tones found:\t[{np.sum(flag_wake_up[0])}/{n_symb_preamb}] ||")
            print("================================\n")

    else:
        detection_release_tones = tones_detection(processing_buffer, 
                                                  index_release_tones,
                                                  threshold_release)
        current_symbol = int(detection_release_tones[1]) - int(detection_release_tones[0])
        decoded_sequence[i] = current_symbol
        flag_end, bit = decoder.step(current_symbol)
        
        if len(bit) != 0:
            decoded_message += str(int(bit[0]))
            print("=================")
            print(f"  {true_message}    ")
            print(f"  {decoded_message}    ")
            print("=================\n")
            
            
            if decoded_message == true_message:
                flag_release = True
                print("=====/!\=====")
                print("!! Release !!")
                print("=====/!\=====\n")
                
                break

            
        if flag_end == True:
            flag_wake_up = [np.zeros(n_symb_preamb, dtype=bool), 
                            -np.ones(n_symb_preamb)]

print(f"Elapsed time: {np.round(time() - t_begin, 5)} s")