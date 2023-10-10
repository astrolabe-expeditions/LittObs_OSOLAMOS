# %% Packages
import logging
import numpy as np
import json
import pyaudio
import sys

from deps import *

# %% Init logger
logging.basicConfig(filename="./logs/rx_log.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S')

# %% Parameters
parameters = json.load(open("./config/config.json"))

# waveform parameters
pulse_width = parameters["waveform"]["pulse_width"]  # pulse width, 1 x 1, [s]
pulse_interval = parameters["waveform"]["pulse_repetition_interval"]  # pulse repetition interval, 1 x 1, [s]
carrier_freq = parameters["waveform"]["carrier_frequency"]  # carrier frequency, 1 x 1, [Hz]
freq_shift = parameters["waveform"]["frequency_shift"]  # frequency shift for bi-tone mode, 1 x 1, [Hz]

# processing parameters
threshold_wake_up = parameters["processing"]["threshold_wake_up"]  # zscore threshold for wake up tones, 1 x 1, [ ]
threshold_release = parameters["processing"]["threshold_release"]  # zscore threshold for release tones, 1 x 1, [ ]
n_step = parameters["processing"]["n_sample_step"]  # number of time samples between each FFT, 1 x 1, [ ]
wake_up_tone = np.array(parameters["processing"]["wake_up_tone"])  # wake up tones, 1 x n_wake_up_tones, [Hz]
release_tone = np.array(parameters["processing"]["release_tone"])  # release tones, 1 x 2, [Hz]
n_sample_buffer = parameters["processing"]["n_sample_buffer"]  # number of bins in FFT, 1 x 1, [ ]
sample_rate = parameters["processing"]["sample_rate"]  # sample rate, 1 x 1, [Hz]

# decoder information
rx_id = parameters["rx_id"]  # Rx ID, 1 x 1, [ ]

# %% Get binary release sequence from rx_id
release_sequence = get_release_sequence(rx_id)

# %% Deducted parameters
threshold_time = ((2 * pulse_interval + pulse_width)  # maximum time sample between the
                  * sample_rate / n_step + 2 * n_sample_buffer)  # first wake-up tone and the last one, 1 x 1, [ ]

n_wake_up_tones = len(wake_up_tone)  # number of wake-up tones, 1 x 1, [ ]
n_release_tones = len(release_sequence)  # number of release tones, 1 x 1, [ ]
release_tones = np.where(release_sequence == 0,
                         release_tone[0], release_tone[1])  # release tones, 1 x n_release_tones, [Hz]
true_message = ''.join(str(tone) for tone in release_sequence)  # binary release sequence, string, [ ]

# %% Get wake up and release tones index in the FFT
wake_up_tone[wake_up_tone < 0] = sample_rate + wake_up_tone[wake_up_tone < 0]
index_wake_up_tones = (np.round(wake_up_tone * n_sample_buffer / sample_rate)
                       ).astype(int)  # index of wake-up tones in FFT, 1 x n_wake_up_tones, [ ]
release_tones[release_tones < 0] = sample_rate + release_tones[release_tones < 0]
index_release_tones = (np.round(np.unique(release_tones) * n_sample_buffer / sample_rate)
                       ).astype(int)  # index of release tones in FFT, 1 x n_release_tones, [ ]

# %% Main routine
if __name__ == "__main__":
    # %% PyAudio initialization
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=n_step)

    # %% Decoder initialization
    decoder = Decoder(n_release_tones,
                      pulse_interval,
                      n_sample_buffer,
                      n_step,
                      sample_rate)

    # %% Buffer initialization
    processing_buffer = np.zeros(n_sample_buffer, dtype=np.int16)
    flag_wake_up_tones = [np.zeros(n_wake_up_tones, dtype=bool),
                          -np.ones(n_wake_up_tones)]

    decoded_message = ""
    flag_release = False
    flag_wake_up = False
    flag_end = False
    i_chunk = 0

    while flag_release is False:
        # %%% Update samples
        processing_buffer[:-n_step] = processing_buffer[n_step:]
        processing_buffer[-n_step:] = np.copy(np.frombuffer(stream.read(n_step), dtype=np.int16))
        current_flag_release = np.array([False, False])

        # %%% Check wake up tones
        if flag_wake_up is False:
            if (i_chunk * n_step) % (2 * sample_rate) == 0:
                i_chunk = 0
                sys.stdout.write("Looking for wake-up tones...\n")
                sys.stdout.flush()

            current_flag_wake_up = tones_detection(processing_buffer,
                                                   index_wake_up_tones,
                                                   threshold_wake_up)

            flag_wake_up_tones, index_event = update_flag_wake_up(flag_wake_up_tones,
                                                                  current_flag_wake_up,
                                                                  threshold_time)

            if index_event:
                sys.stdout.write(
                    f'Wake up tones update - [n{index_event[0] + 1}: {np.sum(flag_wake_up_tones[0])}/{n_wake_up_tones}]\n')
                sys.stdout.flush()
                logging.info(
                    f'Wake up tones update - [n{index_event[0] + 1}: {np.sum(flag_wake_up_tones[0])}/{n_wake_up_tones}]')

            i_chunk += 1
            flag_wake_up_tones[0] = np.array([True, True, True])
            if (flag_wake_up_tones[0].all() and np.all(
                    np.sort(flag_wake_up_tones[0][::-1]) == flag_wake_up_tones[0][::-1])):
                flag_wake_up = True
        else:
            detection_release_tones = tones_detection(processing_buffer,
                                                      index_release_tones,
                                                      threshold_release)

            current_symbol = int(detection_release_tones[1]) - int(detection_release_tones[0])
            flag_end, bit = decoder.step(current_symbol)

            if len(bit) != 0:
                decoded_message += str(int(bit[0]))

                sys.stdout.write(f'Decoded message - {decoded_message}\n')
                sys.stdout.flush()
                logging.info(f'Decoded message - {decoded_message}')

                if decoded_message == true_message:
                    flag_release = True

                    sys.stdout.write('!! Release !!\n')
                    sys.stdout.flush()
                    logging.warning('!! Release !!')

                    break

            if flag_end:
                flag_wake_up = False
                flag_wake_up_tones = [np.zeros(n_wake_up_tones, dtype=bool),
                                      -np.ones(n_wake_up_tones)]
                decoded_message = ""
                decoder.reset()

    stream.stop_stream()
    stream.close()
    p.terminate()
