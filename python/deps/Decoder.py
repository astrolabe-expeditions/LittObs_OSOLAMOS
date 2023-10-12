import logging
import numpy as np
import json
import sys

from .ReleaseDecoder import ReleaseDecoder
from .flag_tones_to_symbol import flag_tones_to_symbol
from .get_release_sequence import get_release_sequence
from .tones_detection import tones_detection
from .update_flag_wake_up import update_flag_wake_up

# %% Init logger
logging.basicConfig(filename="./logs/rx_log.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S')


class Decoder:
    def step(self, processing_buffer):
        # %%% Check wake up tones
        if self.flag_wake_up is False:
            current_flag_wake_up = tones_detection(processing_buffer,
                                                   self.index_wake_up_tones,
                                                   self.threshold_wake_up)

            self.flag_wake_up_tones, index_event = update_flag_wake_up(self.flag_wake_up_tones,
                                                                       current_flag_wake_up,
                                                                       self.threshold_time)
            self.print_update_wake_up_tone(index_event)
            self.check_wake_up_status()

        else:
            detection_release_tones = tones_detection(processing_buffer,
                                                      self.index_release_tones,
                                                      self.threshold_release)

            current_symbol = flag_tones_to_symbol(detection_release_tones)
            flag_end, bit = self.release_decoder.step(current_symbol)

            self.flag_release = self.update_decoded_message(bit)

            if self.flag_release:
                return True

            if flag_end:
                self.reset()

        return False

    def check_wake_up_status(self):
        if (self.flag_wake_up_tones[0].all() and np.all(
                np.sort(self.flag_wake_up_tones[0][::-1]) == self.flag_wake_up_tones[0][::-1])):
            self.flag_wake_up = True

        else:
            self.i_chunk += 1

            if (self.i_chunk * self.n_step) % (4 * self.sample_rate) == 0:
                self.print_looking_wake_up_tone()
                self.i_chunk = 0

    def update_decoded_message(self, bit):
        if len(bit) != 0:
            self.decoded_message += str(int(bit[0]))
            self.print_update_decoded_message()

            if self.decoded_message == self.true_message:
                self.print_release()
                return True

    def reset(self):
        self.flag_wake_up_tones = [np.zeros(self.n_wake_up_tones, dtype=bool),
                                   -np.ones(self.n_wake_up_tones)]

        self.decoded_message = ""
        self.flag_wake_up = False
        self.flag_wake_up_tones = [np.zeros(self.n_wake_up_tones, dtype=bool),
                                   -np.ones(self.n_wake_up_tones)]
        self.decoded_message = ""
        self.release_decoder.reset()

    def print_looking_wake_up_tone(self):
        if self.log:
            sys.stdout.write("Looking for wake-up tones...\n")
            sys.stdout.flush()

    def print_release(self):
        if self.log:
            message = '!! Release !!'
            sys.stdout.write(message + '\n')
            logging.warning(message)
            sys.stdout.flush()

    def print_update_decoded_message(self):
        if self.log:
            message = f'Decoded message - {self.decoded_message}'
            sys.stdout.write(message + '\n')
            logging.info(message)
            sys.stdout.flush()

    def print_update_wake_up_tone(self, index_event):
        if self.log:
            if index_event:
                message = (f'Wake up tones update - [no {index_event[0] + 1}: '
                           f'{np.sum(self.flag_wake_up_tones[0])}/{self.n_wake_up_tones}]')
                sys.stdout.write(message + '\n')
                logging.info(message)
                sys.stdout.flush()

    def get_sample_rate(self):
        return self.sample_rate

    def get_n_step(self):
        return self.n_step

    def get_n_sample_buffer(self):
        return self.n_sample_buffer

    def __init__(self,
                 log=False):
        # %% Parameters
        parameters = json.load(open(sys.path[0] + "/config/config.json"))

        # waveform parameters
        self.pulse_width = parameters["waveform"]["pulse_width"]  # pulse width, 1 x 1, [s]
        self.pulse_interval = parameters["waveform"][
            "pulse_repetition_interval"]  # pulse repetition interval, 1 x 1, [s]
        self.carrier_freq = parameters["waveform"]["carrier_frequency"]  # carrier frequency, 1 x 1, [Hz]
        self.freq_shift = parameters["waveform"]["frequency_shift"]  # frequency shift for bi-tone mode, 1 x 1, [Hz]

        # processing parameters
        self.threshold_wake_up = parameters["processing"][
            "threshold_wake_up"]  # zscore threshold for wake up tones, 1 x 1, [ ]
        self.threshold_release = parameters["processing"][
            "threshold_release"]  # zscore threshold for release tones, 1 x 1, [ ]
        self.n_step = parameters["processing"]["n_sample_step"]  # number of time samples between each FFT, 1 x 1, [ ]
        self.wake_up_tone = np.array(
            parameters["processing"]["wake_up_tone"])  # wake up tones, 1 x n_wake_up_tones, [Hz]
        self.release_tone = np.array(parameters["processing"]["release_tone"])  # release tones, 1 x 2, [Hz]
        self.n_sample_buffer = parameters["processing"]["n_sample_buffer"]  # number of bins in FFT, 1 x 1, [ ]
        self.sample_rate = parameters["processing"]["sample_rate"]  # sample rate, 1 x 1, [Hz]

        # %% Get binary release sequence from rx_id
        self.release_sequence = get_release_sequence(parameters["rx_id"])

        # %% Deducted parameters
        self.threshold_time = ((2 * self.pulse_interval + self.pulse_width)  # maximum time sample between the
                               * self.sample_rate / self.n_step
                               + 2 * self.n_sample_buffer)  # first wake-up tone and the last one, 1 x 1, [ ]

        self.n_wake_up_tones = len(self.wake_up_tone)  # number of wake-up tones, 1 x 1, [ ]
        self.n_release_tones = len(self.release_sequence)  # number of release tones, 1 x 1, [ ]
        self.release_tones = np.where(self.release_sequence == 0,
                                      self.release_tone[0],
                                      self.release_tone[1])  # release tones, 1 x n_release_tones, [Hz]
        self.true_message = ''.join(str(tone) for tone in self.release_sequence)  # binary release sequence, string, [ ]

        # %% Get wake up and release tones index in the FFT
        self.wake_up_tone[self.wake_up_tone < 0] = self.sample_rate + self.wake_up_tone[self.wake_up_tone < 0]
        self.index_wake_up_tones = (np.round(self.wake_up_tone * self.n_sample_buffer / self.sample_rate)
                                    ).astype(int)  # index of wake-up tones in FFT, 1 x n_wake_up_tones, [ ]
        self.release_tones[self.release_tones < 0] = self.sample_rate + self.release_tones[self.release_tones < 0]
        self.index_release_tones = (np.round(np.unique(self.release_tones) * self.n_sample_buffer / self.sample_rate)
                                    ).astype(int)  # index of release tones in FFT, 1 x n_release_tones, [ ]

        # %% Buffer initialization
        self.flag_wake_up_tones = [np.zeros(self.n_wake_up_tones, dtype=bool),
                                   -np.ones(self.n_wake_up_tones)]

        self.decoded_message = ""
        self.flag_release = False
        self.flag_wake_up = False
        self.i_chunk = 0
        self.log = log

        # %% Release Decoder initialization
        self.release_decoder = ReleaseDecoder(n_symbols=self.n_release_tones,
                                              pulse_interval=self.pulse_interval,
                                              n_fft=self.n_sample_buffer,
                                              n_step=self.n_step,
                                              shannon_frequency=self.sample_rate)
