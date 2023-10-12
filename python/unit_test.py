# %% Packages
import sys
import numpy as np
from scipy.io import wavfile

from deps.Decoder import Decoder
import unittest


class RxTest(unittest.TestCase):
    def test_full_sequence(self):
        # %% Decoder initialization
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
