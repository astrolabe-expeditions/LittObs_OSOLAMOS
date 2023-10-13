""" Receiver main """
import numpy as np
import pyaudio

from deps.decoder import Decoder

# %% Decoder initialization
decoder = Decoder(log=True)

sample_rate = decoder.get_sample_rate()
n_step = decoder.get_n_step()
n_sample_buffer = decoder.get_n_sample_buffer()

# %% PyAudio initialization
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=n_step)

# %% Main routine
FLAG_RELEASE = False
if __name__ == "__main__":
    # %%% While loop initialization

    processing_buffer = np.zeros(n_sample_buffer, dtype=np.int16)

    # %%% While loop
    while FLAG_RELEASE is False:
        # %%%% Update samples
        processing_buffer[:-n_step] = processing_buffer[n_step:]
        processing_buffer[-n_step:] = np.copy(np.frombuffer(stream.read(n_step), dtype=np.int16))

        # %%%% Processing step
        FLAG_RELEASE = decoder.step(processing_buffer)

    stream.stop_stream()
    stream.close()
    p.terminate()
