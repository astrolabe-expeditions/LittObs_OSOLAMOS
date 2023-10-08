# %% Packages
import logging
import numpy as np
import json

from scipy.io import wavfile
from deps.Decoder import Decoder
from deps.tones_detection import tones_detection
from deps.update_flag_wake_up import update_flag_wake_up
from time import time

# %% Init logger
logging.basicConfig(filename="./logs/rx_log.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S')

# %% Get audio data
sampling_freq, s_rx = wavfile.read('./data/Rx/test_rx_2023-10-03_004340409.wav')

# %% Parameters
parameters = json.load(open("./config/config.json"))

# waveform parameters
pulse_width = parameters["waveform"]["pulse_width"]  # pulse width, 1 x 1, [s]
pulse_interval = parameters["waveform"]["pulse_repetition_interval"]  # pulse interval repetition, 1 x 1, [s]
carrier_freq = parameters["waveform"]["carrier_frequency"]   # carrier frequency, 1 x 1, [Hz]
freq_shift = parameters["waveform"]["frequency_shift"]   # frequency shift for bi-tone mode, 1 x 1, [Hz]

# processing parameters
threshold_wake_up = parameters["processing"]["threshold_wake_up"]  # zscore threshold for wake up tones (FFT), 1 x 1, [ ]
threshold_release = parameters["processing"]["threshold_release"]  # zscore threshold for release tones (FFT), 1 x 1, [ ]
n_step = parameters["processing"]["n_sample_step"]  # number of time sample between each FFT, 1 x 1, [ ]
wake_up_tone = np.array(parameters["processing"]["wake_up_tone"])  # wake up tones, 1 x n_symb_preamb, [Hz]
n_sample_buffer = parameters["processing"]["n_sample_buffer"]  # number of bins in FFT, 1 x 1, [ ]

# decoder informations
rx_id = parameters["rx_id"]  # decoder index, 1 x 1, [ ] 
release_sequence = np.array(parameters["release_sequence"])  # binary release sequence, 1 x n_pulse, [ ]

# %% Deducted parameters 
threshold_time = (2 * pulse_interval + pulse_width) * sampling_freq + 2 * n_sample_buffer  # maximum time sample between the first wake up tone and the last release tone, 1 x 1, [ ] 
n_symb_preamb = len(wake_up_tone)  # number of wake up tones, 1 x 1, [ ]
n_pulse = len(release_sequence)   # number of release tones, 1 x 1, [ ]
release_tones = 4 * sampling_freq / n_sample_buffer * np.where(release_sequence == 1, 1, -1) + carrier_freq  # release tones, 1 x n_pulse, [Hz]
true_message = ''.join(str(tone) for tone in release_sequence)   # binary release sequence, string, [ ]

# %% Get wake up and release tones index in the FFT
release_tones[release_tones < 0] = sampling_freq + release_tones[release_tones < 0]
index_release_tones = (np.round(np.unique(release_tones) * n_sample_buffer
                                / sampling_freq)).astype(int)
wake_up_tone[wake_up_tone < 0] = sampling_freq + wake_up_tone[wake_up_tone < 0]
index_wake_up_tones = (np.round(wake_up_tone * n_sample_buffer
                                / sampling_freq)).astype(int)

# %% Real time processing
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
    if not flag_wake_up[0].all():
        current_flag_wake_up = tones_detection(processing_buffer,
                                               index_wake_up_tones,
                                               threshold_wake_up)
        flag_wake_up, event = update_flag_wake_up(flag_wake_up,
                                                  current_flag_wake_up,
                                                  threshold_time)
        if event:
            logging.info(f'Wake up tones found - [{np.sum(flag_wake_up[0])}/{n_symb_preamb}]')

    else:
        detection_release_tones = tones_detection(processing_buffer,
                                                  index_release_tones,
                                                  threshold_release)
        current_symbol = int(detection_release_tones[1]) - int(detection_release_tones[0])
        decoded_sequence[i] = current_symbol
        flag_end, bit = decoder.step(current_symbol)

        if len(bit) != 0:
            decoded_message += str(int(bit[0]))
            logging.info(f'Decoded message - {decoded_message}')

            if decoded_message == true_message:
                flag_release = True
                logging.warning('!! Release !!')

                break

        if flag_end:
            flag_wake_up = [np.zeros(n_symb_preamb, dtype=bool),
                            -np.ones(n_symb_preamb)]

print(f"Elapsed time: {np.round(time() - t_begin, 5)} s")
