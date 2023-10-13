""" Decoder class definition """
import logging
import json
import sys
import numpy as np

from .release_decoder import ReleaseDecoder
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
    """
        Decoder object
    """

    def step(self, processing_buffer):

        # %%% Check wake up tones
        """
        The step function is the main function of the class. It takes in a buffer
        of audio data and returns a boolean indicating whether it has detected
        a release tone. The step function also updates its internal state, which is
        used to keep track of whether it has detected wake-up tones and if so,
        how long ago they were detected.

        :param self: Refer to the object itself
        :param processing_buffer: Pass the audio data to the step function
        :return: True if the flag_release is true, which means that

        """
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
        """
        The check_wake_up_status function checks if the wake-up tones have been detected.

        :param self: Access the attributes and methods of the class in python
        :return: The value of the flag_wake_up variable

        """

        if (self.flag_wake_up_tones[0].all() and np.all(
                np.sort(self.flag_wake_up_tones[0][::-1]) == self.flag_wake_up_tones[0][::-1])):
            self.flag_wake_up = True

        else:
            self.i_chunk += 1

            if (self.i_chunk * self.n_step) % (4 * self.sample_rate) == 0:
                self.print_looking_wake_up_tone()
                self.i_chunk = 0

    def update_decoded_message(self, bit):

        """
        The update_decoded_message function takes in a bit and adds it to the decoded_message.
        It then prints out the updated message, and if the decoded_message is equal to true_message,
        it will print that you have released your friend from prison.

        :param self: Access the attributes of the class
        :param bit: Add the bit to the decoded message
        :return: True if the decoded message is equal to the true message

        """
        if len(bit) != 0:
            self.decoded_message += str(int(bit[0]))
            self.print_update_decoded_message()

            if self.decoded_message == self.true_message:
                self.print_release()
                return True

        return False

    def reset(self):
        """
        The reset function is used to reset the decoder.

        :param self: Represent the instance of the class
        :return: The decoded_message and the flag_wake_up

        """

        self.flag_wake_up_tones = [np.zeros(self.n_wake_up_tones, dtype=bool),
                                   -np.ones(self.n_wake_up_tones)]

        self.decoded_message = ""
        self.flag_wake_up = False
        self.flag_wake_up_tones = [np.zeros(self.n_wake_up_tones, dtype=bool),
                                   -np.ones(self.n_wake_up_tones)]
        self.decoded_message = ""
        self.release_decoder.reset()

    def print_looking_wake_up_tone(self):
        """
        The print_looking_wake_up_tone function prints a message to the console
        indicating that the program is looking for wake-up tones.


        :param self: Refer to the object itself
        :return: A string
        """

        if self.log:
            sys.stdout.write("Looking for wake-up tones...\n")
            sys.stdout.flush()

    def print_release(self):
        """
        The print_release function prints a message to the screen and logs it.

        :param self: Refer to the instance of the class
        :return: Nothing

        """

        if self.log:
            message = '!! Release !!'
            sys.stdout.write(message + '\n')
            logging.warning(message)
            sys.stdout.flush()

    def print_update_decoded_message(self):
        """
        The print_update_decoded_message function prints the decoded message
        to the console and logs it.

        :param self: Reference the object itself
        :return: Nothing
        """

        if self.log:
            message = f'Decoded message - {self.decoded_message}'
            sys.stdout.write(message + '\n')
            logging.info(message)
            sys.stdout.flush()

    def print_update_wake_up_tone(self, index_event):

        """
        The print_update_wake_up_tone function prints the number of wake-up tones
        that have been found in a given file.

        :param self: Bind the method to a class
        :param index_event: Print the number of wake-up tones that have been found
        :return: A message that is printed to the console

        """
        if self.log:
            if index_event:
                message = (f'Wake up tones update - [no {index_event[0] + 1}: '
                           f'{np.sum(self.flag_wake_up_tones[0])}/{self.n_wake_up_tones}]')
                sys.stdout.write(message + '\n')
                logging.info(message)
                sys.stdout.flush()

    def get_sample_rate(self):
        """
        The get_sample_rate function returns the sample rate of the audio file.

        :param self: Represent the instance of the class
        :return: The sample rate of the audio file
        """

        return self.sample_rate

    def get_n_step(self):
        """
        The get_n_step function returns the number of steps.

        :param self: Represent the instance of the class
        :return: The number of steps that the user has taken
        """

        return self.n_step

    def get_n_sample_buffer(self):

        """
        The get_n_sample_buffer function returns the number of samples in the buffer.

        :param self: Represent the instance of the class
        :return: The number of samples in the buffer
        :doc-author: Trelent
        """
        return self.n_sample_buffer

    def __init__(self,
                 log=False):
        """
        The __init__ function initializes the class.

        :param self: Represent the instance of the class
        :param log: Print the decoded message in real time
        :return: Nothing

        """

        # %% Parameters
        with open(sys.path[0] + "/config/config.json", encoding="utf-8") as file:
            parameters = json.load(file)

        # waveform parameters
        self.pulse_width = parameters["waveform"]["pulse_width"]  # pulse width, 1 x 1, [s]
        self.pulse_interval = parameters["waveform"][
            "pulse_repetition_interval"]  # pulse repetition interval, 1 x 1, [s]
        self.carrier_freq = parameters["waveform"][
            "carrier_frequency"]  # carrier frequency, 1 x 1, [Hz]
        self.freq_shift = parameters["waveform"][
            "frequency_shift"]  # frequency shift for bi-tone mode, 1 x 1, [Hz]

        # processing parameters
        self.threshold_wake_up = parameters["processing"][
            "threshold_wake_up"]  # zscore threshold for wake-up tones, 1 x 1, [ ]
        self.threshold_release = parameters["processing"][
            "threshold_release"]  # zscore threshold for release tones, 1 x 1, [ ]
        self.n_step = parameters["processing"][
            "n_sample_step"]  # number of time samples between each FFT, 1 x 1, [ ]
        self.wake_up_tone = np.array(
            parameters["processing"]["wake_up_tone"])  # wake up tones, 1 x n_wake_up_tones, [Hz]
        self.release_tone = np.array(parameters["processing"][
                                         "release_tone"])  # release tones, 1 x 2, [Hz]
        self.n_sample_buffer = parameters["processing"][
            "n_sample_buffer"]  # number of bins in FFT, 1 x 1, [ ]
        self.sample_rate = parameters["processing"][
            "sample_rate"]  # sample rate, 1 x 1, [Hz]

        # %% Get the binary release sequence from rx_id
        self.release_sequence = get_release_sequence(parameters["rx_id"])

        # %% Deducted parameters
        # maximum time sample between the first wake-up tone and the last one, 1 x 1, [ ]
        self.threshold_time = ((2 * self.pulse_interval + self.pulse_width)
                               * self.sample_rate / self.n_step
                               + 2 * self.n_sample_buffer)

        self.n_wake_up_tones = len(self.wake_up_tone)  # number of wake-up tones, 1 x 1, [ ]
        self.n_release_tones = len(self.release_sequence)  # number of release tones, 1 x 1, [ ]
        # release tones, 1 x n_release_tones, [Hz]
        self.release_tones = np.where(self.release_sequence == 0,
                                      self.release_tone[0],
                                      self.release_tone[1])
        # binary release sequence, string, [ ]
        self.true_message = ''.join(str(tone) for tone in self.release_sequence)

        # %% Get wake up and release tones index in the FFT
        self.wake_up_tone[self.wake_up_tone < 0] = (self.sample_rate
                                                    + self.wake_up_tone[self.wake_up_tone < 0])
        # index of wake-up tones in FFT, 1 x n_wake_up_tones, [ ]
        self.index_wake_up_tones = (np.round(self.wake_up_tone
                                             * self.n_sample_buffer / self.sample_rate)
                                    ).astype(int)
        self.release_tones[self.release_tones < 0] = (self.sample_rate
                                                      + self.release_tones[self.release_tones < 0])
        # index of release tones in FFT, 1 x n_release_tones, [ ]
        self.index_release_tones = (np.round(np.unique(self.release_tones)
                                             * self.n_sample_buffer / self.sample_rate)
                                    ).astype(int)

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
