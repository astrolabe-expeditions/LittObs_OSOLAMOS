# %% Packages
import sys
import json
import jsbeautifier
import numpy as np
import scipy.io.wavfile as wavf

from scipy.signal.windows import tukey
from python.deps.get_release_sequence import get_release_sequence

# %% Script options
GENERATE_FILE_NAME = "data/Tx/tx_full_sequence.wav"
RX_ID = "1"

# %% Open config file
with open(sys.path[0] + "/config/config.json", encoding="utf-8") as file:
    parameters = json.load(file)

# %% Parameters
pulse_width = parameters["waveform"]["pulse_width"]  # pulse width, 1 x 1, [s]
pulse_interval = parameters["waveform"]["pulse_repetition_interval"]  # pulse interval repetition, 1 x 1, [s]
sampling_freq = parameters["processing"]["sample_rate"]  # sampling frequency, 1 x 1, [Hz]
carrier_freq = parameters["waveform"]["carrier_frequency"]  # carrier frequency, 1 x 1, [Hz]
n_sample_buffer = parameters["processing"]["n_sample_buffer"]  # number of bins in FFT, 1 x 1, [ ]
release_sequence = get_release_sequence(RX_ID)  # binary release sequence, 1 x 1, [ ]

# %% Generate wake-up tones and release tones
wake_up_tones = np.array([-10, 0, 10]) * sampling_freq / n_sample_buffer + carrier_freq
wake_up_tones[wake_up_tones < 0] = sampling_freq + wake_up_tones[wake_up_tones < 0]
release_tones = 20 * sampling_freq / n_sample_buffer * (2 * release_sequence - 1) + carrier_freq

# %% Deducted parameters
sampling_prd = 1 / sampling_freq  # sampling period, 1 x 1, [s]
n_release_tones = len(release_tones)  # number of release tones, 1 x 1, [ ]
n_wake_up_tones = len(wake_up_tones)  # number of wake-up tones, 1 x 1, [ ]

# %% Generate Tx signal
time_recording = (n_wake_up_tones + n_release_tones) * pulse_interval
time = np.arange(0, time_recording, sampling_prd)
s_tx = np.zeros(len(time), dtype="complex")

for i_pulse in range(n_release_tones + n_wake_up_tones):
    if i_pulse <= n_wake_up_tones - 1:
        pulse_freq = wake_up_tones[i_pulse]

    else:
        pulse_freq = release_tones[i_pulse - n_wake_up_tones]

    door_tx = np.where(np.logical_and(time - i_pulse * pulse_interval >= 0,
                                      time - i_pulse * pulse_interval < pulse_width),
                       1.0, 0.0)
    door_tx[door_tx == 1.0] = tukey(int(door_tx.sum()))

    s_tx += np.exp(1j * 2 * np.pi * pulse_freq *
                   (time - i_pulse * pulse_interval)) * door_tx

# %% Get real part and scale to [-32768, 32767]
s_tx = (s_tx.real + 1) / 2 * (32767 + 32768) - 32768

# %% Save Tx signals in .wav file
wavf.write(GENERATE_FILE_NAME, sampling_freq, s_tx.astype(np.int16))

# %% Update release_sequences.json file
with open(sys.path[0] + "/config/release_sequences.json", mode="r", encoding="utf-8") as file:
    rx_id_parameters = json.load(file)

    rx_id_parameters[RX_ID]["release_tones"] = np.unique(release_tones).tolist()
    rx_id_parameters[RX_ID]["wake_up_tones"] = wake_up_tones.tolist()

    options = jsbeautifier.default_options()
    options.indent_size = 4
    payload = jsbeautifier.beautify(json.dumps(rx_id_parameters), options)

with open(sys.path[0] + "/config/release_sequences.json", mode="w", encoding="utf-8") as file:
    file.write(payload)
