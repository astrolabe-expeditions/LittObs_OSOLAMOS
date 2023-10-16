""" unit tests main """
# %% Packages
import unittest
import sys
import numpy as np
from scipy.io import wavfile

from deps.decoder import Decoder


class RxTest(unittest.TestCase):
    """
        RxTest object
    """

    def test_full_sequence(self):
        """
        The test_full_sequence function tests the Decoder class by
        running it on a recorded audio file. The test_full_sequence
        function is run in the main() function of this script, and
        if it passes, the user will see 'OK' printed to their terminal.
        If not, they will see an error message.

        :param self: Represent the instance of the class
        :return: True if the flag_release is true

        """

        # %% Decoder initialization
        decoder = Decoder()

        n_step = decoder.get_n_step()
        n_sample_buffer = decoder.get_n_sample_buffer()

        _, s_rx = wavfile.read(sys.path[0] + '/data/Tx/tx_full_sequence.wav')

        # %%% While loop initialization
        flag_release = False
        processing_buffer = np.zeros(n_sample_buffer, dtype=np.int16)

        # %%% While loop
        for i in range(len(s_rx) // n_step):
            # %%%% Update samples
            processing_buffer[:-n_step] = processing_buffer[n_step:]
            processing_buffer[-n_step:] = s_rx[i * n_step: (i + 1) * n_step]

            # %%%% Processing step
            flag_release = decoder.step(processing_buffer)
            if flag_release is True:
                break

        self.assertEqual(True, flag_release)

    def test_wake_up_sequence(self):
        """
        The test_wake_up_sequence function tests the Decoder class's ability to
        detect a wake-up sequence.
        The test_wake_up_sequence function is called by the unittest module, which
        is imported in main.py.
        The test_wake_up_sequence function calls the Decoder class's step method
        with a signal containing a wake-up sequence and checks that flag release
        and flag wake up are set correctly.

        :param self: Represent the instance of the class
        :return: True, not flag_release and flag_wake_up

        """
        # %% Decoder initialization
        decoder = Decoder()

        n_step = decoder.get_n_step()
        n_sample_buffer = decoder.get_n_sample_buffer()

        _, s_rx = wavfile.read(sys.path[0] + '/data/Tx/tx_wake_up_sequence.wav')

        # %%% While loop initialization
        flag_release = False
        flag_wake_up = False
        processing_buffer = np.zeros(n_sample_buffer, dtype=np.int16)

        # %%% While loop
        for i in range(len(s_rx) // n_step):
            # %%%% Update samples
            processing_buffer[:-n_step] = processing_buffer[n_step:]
            processing_buffer[-n_step:] = s_rx[i * n_step: (i + 1) * n_step]

            # %%%% Processing step
            flag_release = decoder.step(processing_buffer)

            # %%%% Check wake-up status
            flag_wake_up = decoder.flag_wake_up

        self.assertEqual(True, not flag_release and flag_wake_up)

    def test_release_sequence(self):
        """
        The test_release_sequence function tests the Decoder class's step function.
        The test_release_sequence function is a unit test that checks if the decoder can
        detect a release sequence.
        The test_release_sequence function uses an audio file of a release sequence to
        check if the decoder can detect it.

        :param self: Represent the instance of the class
        :return: True, not flag_release and not flag_wake_up

        """

        # %% Decoder initialization
        decoder = Decoder()

        n_step = decoder.get_n_step()
        n_sample_buffer = decoder.get_n_sample_buffer()

        _, s_rx = wavfile.read(sys.path[0] + '/data/Tx/tx_release_sequence.wav')

        # %%% While loop initialization
        flag_release = False
        flag_wake_up = False
        processing_buffer = np.zeros(n_sample_buffer, dtype=np.int16)

        # %%% While loop
        for i in range(len(s_rx) // n_step):
            # %%%% Update samples
            processing_buffer[:-n_step] = processing_buffer[n_step:]
            processing_buffer[-n_step:] = s_rx[i * n_step: (i + 1) * n_step]

            # %%%% Processing step
            flag_release = decoder.step(processing_buffer)

            # %%%% Check wake-up status
            flag_wake_up = decoder.flag_wake_up

        self.assertEqual(True, not flag_release and not flag_wake_up)

    def test_real_data(self):
        """
        The test_real_data function tests the Decoder class's step function.
        The test_real_data function is a unit test that checks if the decoder
        can detect a release sequence.
        The test_real_data function uses an audio file of a release sequence to
        check if the decoder can detect it.

        :param self: Represent the instance of the class
        :return: True, not flag_release and not flag_wake_up
        """

        # %% Decoder initialization
        decoder = Decoder()

        n_step = decoder.get_n_step()
        n_sample_buffer = decoder.get_n_sample_buffer()

        _, s_rx = wavfile.read(sys.path[0] + '/data/Rx/test_rx_2023-10-03_004340409.wav')

        # %%% While loop initialization
        flag_release = False
        flag_wake_up = False
        processing_buffer = np.zeros(n_sample_buffer, dtype=np.int16)

        # %%% While loop
        for i in range(len(s_rx) // n_step):
            # %%%% Update samples
            processing_buffer[:-n_step] = processing_buffer[n_step:]
            processing_buffer[-n_step:] = s_rx[i * n_step: (i + 1) * n_step]

            # %%%% Processing step
            flag_release = decoder.step(processing_buffer)

            if flag_release:
                break

            # %%%% Check wake-up status
            flag_wake_up = decoder.flag_wake_up

        self.assertEqual(True, flag_release and flag_wake_up)


if __name__ == '__main__':
    unittest.main()
