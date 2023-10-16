import numpy as np
import pyaudio

from deps.decoder import Decoder

# %% Initialization
decoder = Decoder(log=True)

SAMPLE_RATE = decoder.get_sample_rate()
N_STEP = decoder.get_n_step()
N_SAMPLE_BUFFER = decoder.get_n_sample_buffer()
FLAG_RELEASE = False

# %% Main routine
if __name__ == "__main__":
    # %% PyAudio initialization
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=N_STEP)

    # %%% While loop initialization
    processing_buffer = np.zeros(N_SAMPLE_BUFFER, dtype=np.int16)

    # %%% While loop
    while FLAG_RELEASE is False:
        # %%%% Update samples
        processing_buffer[:-N_STEP] = processing_buffer[N_STEP:]
        processing_buffer[-N_STEP:] = np.copy(np.frombuffer(stream.read(N_STEP), dtype=np.int16))

        # %%%% Processing step
        FLAG_RELEASE = decoder.step(processing_buffer)

    stream.stop_stream()
    stream.close()
    p.terminate()
