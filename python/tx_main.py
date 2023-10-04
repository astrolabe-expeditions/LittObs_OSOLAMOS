# %% Packages
import numpy as np 
import scipy.io.wavfile as wavf
from scipy.signal.windows import tukey

# %% Parameters
pulse_width = 0.8       # pulse width, 1 x 1, [s]
pulse_interval = 1      # pulse interval repetition, 1 x 1, [s]
power_tx = 1            # power of the transmitted signal, 1 x 1, [W]
sampling_freq = 44_100  # sampling frequency, 1 x 1, [Hz]
carrier_freq = 10_000   # carrier frequency, 1 x 1, [Hz]
n_sample_buffer = 128   
file_name = "tx.wav"

# %% Deducted parameters 
sampling_prd = 1 / sampling_freq    # sampling period, 1 x 1, [s]
amp_tx = np.sqrt(power_tx)          # amplitude of the transmitted 
                                    # signal, 1 x 1, [V]
sub_sampling_factor = int(pulse_interval / sampling_prd)
                                    # sub sampling period (nyquist period 
                                    # to symbol period), 1 x 1, [ ]
                                
# %% Generate wake up tones and release tones
wake_up_tone = np.array([-2, 0, 2]) * sampling_freq / n_sample_buffer + carrier_freq
n_symb_preamb = len(wake_up_tone) 
wake_up_tone[wake_up_tone<0] = sampling_freq + wake_up_tone[wake_up_tone<0]
release_tones = 4 * sampling_freq / n_sample_buffer * np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1]) + carrier_freq
n_pulse = len(release_tones)       # number of pulse, 1 x 1, [ ]


# %% Generate Tx signal
t_recording = (n_symb_preamb + n_pulse) * pulse_interval
t = np.arange(0, t_recording, sampling_prd)
s_tx = 0

for i_pulse in range(n_pulse + n_symb_preamb):    
    if i_pulse <= n_symb_preamb - 1:
        pulse_freq = wake_up_tone[i_pulse] 
        
    else:
        pulse_freq = release_tones[i_pulse - n_symb_preamb]

    door_tx = np.where(np.logical_and(t - i_pulse * pulse_interval >= 0,
                                      t - i_pulse * pulse_interval < pulse_width),
                       1.0, 0.0)
    door_tx[door_tx == 1.0] = tukey(int(door_tx.sum()))

    s_tx += amp_tx * np.exp(1j * 2 * np.pi * pulse_freq * 
                            (t - i_pulse * pulse_interval)) * door_tx
    
wavf.write(file_name, sampling_freq, s_tx.real)