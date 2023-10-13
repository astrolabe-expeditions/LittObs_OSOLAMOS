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

        # %% Decoder initialization
        """
        The test_full_sequence function tests the Decoder class by
        running it on a recorded audio file. The test_full_sequence
        function is run in the main() function of this script, and
        if it passes, the user will see 'OK' printed to their terminal.
        If not, they will see an error message.

        :param self: Represent the instance of the class
        :return: True if the flag_release is true

        """
        decoder = Decoder()

        n_step = decoder.get_n_step()
        n_sample_buffer = decoder.get_n_sample_buffer()

        _, s_rx = wavfile.read(sys.path[0] + '/data/Tx/tx.wav')

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


if __name__ == '__main__':
    unittest.main()
